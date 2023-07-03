from asyncio.windows_events import NULL
import concurrent.futures
from weakref import finalize
import serial
import sys
import keyboard
import time
import re
import PySimpleGUI as sg
import threading
import csv
import os
import signal
import serial.tools.list_ports
#sg.theme('GrayGrayGray')
sg.theme('Topanga')
#sg.theme('DarkBlue1')


data_for_save = []

def error_popup(message):
    # Define the layout for the popup
    layout = [
        [sg.Text(message)],
        [sg.Button("OK", button_color='#414141')]
    ]

    # Create the popup window
    window = sg.Window("Error", layout, icon=r'logo2.ico')

    # Event loop for the popup
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "OK":
            window.close()
            return NULL

def show_number_of_ports_popup():
    # Define the layout for the popup
    layout = [
        [sg.Text("Select Number Of Ports:")],
        [sg.Input()],
        [sg.Button("OK", button_color='#414141')]
    ]

    # Create the popup window
    window = sg.Window("Selecting Number Of Ports", layout, finalize=True, icon=r'logo2.ico')
    window.bind("<Return>", "enter")

    # Event loop for the popup
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "OK" or event == 'enter':
            try:
                number = values[0]
                window.close()
                return int(number)
            except:
                print('here2')
                return NULL

def select_directory_popup():
    # Define the layout for the popup
    layout = [
        [sg.Text("Select a directory:")],
        [sg.Input(), sg.FolderBrowse()],
        [sg.Button("OK", button_color='#414141')]
    ]

    # Create the popup window
    window = sg.Window("Selecting Target Folder", layout, icon=r'logo2.ico')

    # Event loop for the popup
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "OK":
            directory_path = values[0]
            window.close()
            return directory_path

def remove_columns_for_diff(data):
    result = []
    for row in data:
        new_row = [row[1]]
        for i in range((len(row)-2)//3):
            new_row.append(row[i*3+2])
            new_row.append(row[i*3+4])
        result.append(new_row)
    return result

def remove_columns_for_abs(data):
    result = []
    for row in data:
        new_row = [row[0]]
        for i in range((len(row)-2)//3):
            new_row.append(row[i*3+2])
            new_row.append(row[i*3+3])
        result.append(new_row)
    return result

def write_list_of_lists_to_file(path, data, ports):
    try:
        with open(path, 'w') as file:
            file.write('\t')
            for i in range(1, len(ports)+1):
                file.write(str(i)) 
                file.write('\t' * 2) 
            file.write('\n')  # Write a newline character
            for item in data:
                line = "\t".join(str(element) for element in item)
                file.write(line + "\n")
        print(f"Data has been successfully written to the file '{path}'.")
    except IOError:
        print(f"Error writing to the file '{file_path}'.")

def SaveData(ports, directory_path):
    try:
        print('trying to save')
        print(data_for_save)
        print('dpath : ' + directory_path)
        if str.isspace(directory_path):
            write_csv_file(directory_path + '/sample.csv', data_for_save)
            write_list_of_lists_to_file(directory_path + '/abs.txt', remove_columns_for_abs(data_for_save), ports)
            write_list_of_lists_to_file(directory_path + '/diff.txt', remove_columns_for_diff(data_for_save), ports)
        else:
            print(data_for_save)
            write_csv_file('sample.csv', data_for_save)
            write_list_of_lists_to_file('abs.txt', remove_columns_for_abs(data_for_save), ports)
            write_list_of_lists_to_file('diff.txt', remove_columns_for_diff(data_for_save), ports)

        # data_for_save = []
    except Exception as e:
        print("Error : " + str(e))
        return

def capture(ports):
    try:
        
        refA = data_dict[f"{ports[0]}"].get().split("=")[-1]
        print(refA)
        refD = data_dict[f"{ports[1]}"].get().split("=")[-1]

        localData = []
        localData.append(refA)
        localData.append(refD)

        for port in ports[2:]:
            print(data_dict[f"{port}"].get().split(","))
            temp = data_dict[f"{port}"].get().split(",")[3]
            pabs = data_dict[f"{port}"].get().split(",")[4]
            pdiff = data_dict[f"{port}"].get().split(",")[5].split("*")[0]
            localData.append(temp)
            localData.append(pabs)
            localData.append(pdiff)

        data_for_save.append(localData)
        print(data_for_save)
    except Exception as e:
        print("Error : " + str(e))
        return

def write_csv_file(file_path, data):
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        print(f"CSV file '{file_path}' has been successfully written.")
    except IOError:
        print(f"Error writing CSV file '{file_path}'.")

file_path = 'selected_ports.txt'

def get_selected_ports_from_file():
    try:
        with open(file_path, 'r') as file:
            selected_ports = file.read().splitlines()
        return selected_ports
    except FileNotFoundError:
        error_popup("Error: config not found.")
        return NULL
    except IOError:
        error_popup("Error: there is a problem opening the config file.")
        return NULL

def save_ports(ports):
    with open(file_path, 'w') as file:
        file.write('\n'.join(ports))

def get_available_com_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]
    return available_ports

# Global dictionary to store the data for each port
data_dict = {}

# Global dictionary to store the data for each port
prev_data_dict = {}

source_ports = []

# Function to update the data in the GUI
def update_gui(port, value):
    # print(source_ports)
    if port in source_ports:
        if port not in prev_data_dict:
            prev_data_dict[port] = []
        prev_data_dict[port].append(value)
        if len(prev_data_dict[port]) > 15:
            prev_data_dict[port].pop(0)
        data_dict[port].Update("\n".join(map(str, prev_data_dict[port][-15:])))
    else:
        data_dict[port].Update(value)



def read_serial(port):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 19200
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 0
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False
    ser.writeTimeout = 2

    try:
        ser.open()
    except Exception as e:
        print("Error opening serial port: " + str(e))
        return

    press = 1 
    c = ""
    line = ""
    while True:
        c = c + ser.read(1).decode('ascii')
        if c.endswith('\n'):
            line = c.strip()
            print(line)
            update_gui(port, line)
            # update_gui(port, line)
            c = ""

        if keyboard.is_pressed('q'):
            if press:
                data = re.split(',|\*', line)
                print(data)
                update_gui(port, data)
                # Log.append(tuple((data[3], data[4])))
            press = 0
        else:
            press = 1

    ser.close()

def read_ref_serial(port):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 9600
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 0
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False
    ser.writeTimeout = 2

    try:
        ser.open()
    except Exception as e:
        print("Error opening serial port: " + str(e))
        return

    for i in range(1):
        ser.write('*00p2\r\n'.encode())

    press = 1 
    c = ""
    line = ""
    while True:
        c = c + ser.read(1).decode('ascii')
        if c.endswith('\r') or c.endswith('\n'):
            line = c.strip()
            print(line)
            update_gui(port, line)
            # update_gui(port, line)
            c = ""
    ser.close()
# Create the initial page layout
# initial_layout = [
#     [sg.Text("Select an option:")],
#     [sg.Button('Load New Ports'), sg.Button('Load Previous Ports')]
#     # [sg.Button("Load New Ports")],
#     # [sg.Button("Load Previous Ports")]
# ]

# initial_layout = [
#     [sg.Column(
#         layout=[
#             [sg.Button('Load New Ports', size=(20, 2), font=("Calibri", 14), border_width=3), sg.Button('Load Previous Ports', size=(20, 2), font=("Calibri", 14), border_width=3)],
#         ],
#         justification='center',
#         vertical_alignment='center',
#         element_justification='center',
#         expand_x=True,
#         expand_y=True
#     )]
# ]

column_to_be_centered = [
    [sg.Button('Load New Ports', size=(20, 4), font=("Calibri", 14), border_width=3, button_color='#414141'),
        sg.Button('Load Previous Ports', size=(20, 4), font=("Calibri", 14), border_width=3, button_color='#414141')]
]

layout = [#[sg.VPush()],
                 [sg.Push(), sg.Image('logo.png',expand_x=False, expand_y=False, size=(250, 250) ), sg.Push()],
                 [sg.Push(), sg.Text('Airdata Logger', font=("Eras Demi ITC", 36, "bold")), sg.Push()],
                 [sg.VPush()],

              [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
              [sg.VPush()]]

# Create the initial page window
window_size = (1200, 600)
initial_window = sg.Window("Airdata Logger (Version 1.0)", layout, size = window_size, icon=r'logo2.ico')
# sg.Window('Icon Test', layout, icon=r'C:\Python\taskmanager.ico').read(close=True)
show_second_page = False
# Event loop for the initial page
num_ports = 0
while True:
    event, values = initial_window.read()

    # Handle events on the initial page
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Load New Ports":
        num_ports_nullable = show_number_of_ports_popup()
        if num_ports_nullable != NULL:
            num_ports = num_ports_nullable
            show_second_page = True
            # TODO: Implement the code for loading new ports
            # Show the number of ports selection page
            initial_window.hide()
            break
    elif event == "Load Previous Ports":
        selected_ports = get_selected_ports_from_file()
        if(selected_ports != NULL):
            source_ports = selected_ports[:2]
            show_second_page = False
            # Show the main page with previous ports
            initial_window.hide()
            break

if show_second_page is True:
    # # Create the number of ports selection page layout
    # num_ports_layout = [
    #     [sg.Text("Select the number of ports:")],
    #     [sg.Combo([i for i in range(1, 59)], size=(10, 1))],
    #     [sg.Button("Next")]
    # ]

    # # Create the number of ports selection page window
    # num_ports_window = sg.Window("Number of Ports Selection", num_ports_layout)

    # # Event loop for the number of ports selection page
    # while True:
    #     event, values = num_ports_window.read()

    #     # Handle events on the number of ports selection page
    #     if event == sg.WINDOW_CLOSED:
    #         break
    #     elif event == "Next":
    #         num_ports = int(values[0])
    #         # Show the port selection page with the selected number of ports
    #         num_ports_window.hide()
    #         break

    num_ports += 2
    # Create the port selection page layout
    port_selection_layout = [[sg.Text("Select Ports:")]]
    # for i in range(num_ports):
        #port_selection_layout.append([sg.Text(f"{i+1}."), sg.Combo(get_available_com_ports(), size=(10, 1))])

    num_columns = num_ports // 12 + 1 
    num_combos_per_column = 12
    num_combos_first_column = num_ports % 12
    column = num_combos_first_column
    combo_layout = []
    combo_boxes = []
    counter = 0
    # Generate the combo boxes for each column
    for i in range(num_columns):
        for j in range(column):
            combo_boxes.append([sg.Text(f"Airdata {(counter-1):>3}." if counter > 1 else f"RefD" if counter == 1 else f"RefA"), sg.Combo(get_available_com_ports(), size=(10, 1), key=f"-COMBO-{counter}")])
            counter += 1
        combo_layout.append(sg.Column(combo_boxes, element_justification='right'))
        if (i < num_columns - 1):
            combo_layout.append(sg.VSeperator())
        combo_boxes.clear()
        column = num_combos_per_column
    port_selection_layout.append(combo_layout)
    port_selection_layout.append([sg.Button("Next", button_color='#414141')])

    # Create the port selection page window
    port_selection_window = sg.Window("Port Selection", port_selection_layout, icon=r'logo2.ico')

    # Event loop for the port selection page
    while True:
        event, values = port_selection_window.read()

        # Handle events on the port selection page
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Next":
            print(values)

            selected_ports = []
            for i in range(num_ports):
                selected_ports.append(values[f"-COMBO-{i}"])

            # selected_ports = [values[i] for i in range(num_ports)]  # Exclude the "Next" button value
            source_ports = selected_ports[:2]
            save_ports(selected_ports)
            # TODO: Implement the code to handle the selected ports
            # Show the main page with selected ports
            port_selection_window.hide()
            break

# Create the main page layout
main_layout = []

# Separate the additional ports from the selected ports
additional_ports = selected_ports[:2]
remaining_ports = selected_ports[2:]


# Create a vertical box for the left side (additional ports)
left_layout = []
refa_frame = []
refd_frame = []

#refa_frame.append([sg.Text(f"refA", justification='left', font=("Calibri", 12))])
refa_frame.append(sg.Multiline("", key=additional_ports[0], size=(15, 15), no_scrollbar=True, border_width=2, disabled=True))
refa_frame.append(sg.Text("", key=f"{additional_ports[0]}_data"))
left_frame = sg.Frame(f"refA", [refa_frame], border_width=1)

#refd_frame.append([sg.Text(f"refD", justification='left', font=("Calibri", 12))])
refd_frame.append(sg.Multiline("", key=additional_ports[1], size=(15, 15), no_scrollbar=True, border_width=2, disabled=True))
refd_frame.append(sg.Text("", key=f"{additional_ports[1]}_data"))
right_frame = sg.Frame(f"refD", [refd_frame], border_width=1)

left_layout.append([left_frame, right_frame])
left_layout.append([sg.Button("Capture", size=(15, 3), font=("Calibri", 14), border_width=3, button_color='#414141')])  # Add a single capture button for all ports
left_layout.append([sg.Button("Save", size=(15, 3), font=("Calibri", 14), border_width=3, button_color='#414141')])  # Add a single capture button for all ports

left_column = sg.Column(left_layout, element_justification='center')


# Create a vertical box for the right side (remaining ports)
right_layout = []
# for index, port in enumerate(remaining_ports):
#     if index % 2 == 0:
#         right_layout.append([sg.Text(f"Airdata#{index+1}", justification='left', font=("Calibri", 12))])
#         right_layout.append([sg.Multiline("", key=port, no_scrollbar=True)])
#         right_layout.append([sg.Text("", key=f"{port}_data")])
#     else:
#         right_layout2.append([sg.Text(f"Airdata#{index+1}", justification='left', font=("Calibri", 12))])
#         right_layout2.append([sg.Multiline("", key=port, no_scrollbar=True)])
#         right_layout2.append([sg.Text("", key=f"{port}_data")])

for index in range(0, len(remaining_ports)):

    if index % 2 == 1:
        continue

    a = []
    #a.append(sg.Text(f"Airdata#{index+1}", justification='left', font=("Calibri", 12)))
    a.append(sg.Multiline("", key=remaining_ports[index], no_scrollbar=True, border_width=2, disabled=True))
    a.append(sg.Text("", key=f"{remaining_ports[index]}_data"))

    right_frame = sg.Frame(f"Airdata#{index+1}", [a], border_width=1)

    if index != len(remaining_ports) - 1:
        a = []
        #a.append(sg.Text(f"Airdata#{index+2}", justification='left', font=("Calibri", 12)))
        a.append(sg.Multiline("", key=remaining_ports[index+1], no_scrollbar=True, border_width=2, disabled=True))
        a.append(sg.Text("", key=f"{remaining_ports[index+1]}_data"))

        left_frame = sg.Frame(f"Airdata#{index+2}", [a], border_width=1)
        right_layout.append([right_frame, left_frame])
    else:
         right_layout.append([right_frame])
    
    # right_layout.append([sg.Text(f"Airdata#{index+1}", justification='left', font=("Calibri", 12)), sg.Text(f"Airdata#{index+2}", justification='left', font=("Calibri", 12))])
    # # right_layout.append([sg.Text(f"Airdata#{index+2}", justification='left', font=("Calibri", 12))])


    # right_layout.append([sg.Multiline("", key=remaining_ports[index], no_scrollbar=True), sg.Multiline("", key=remaining_ports[index+1], no_scrollbar=True)])
    # # right_layout.append([sg.Multiline("", key=remaining_ports[index+1], no_scrollbar=True)])
    


    # right_layout.append([sg.Text("", key=f"{remaining_ports[index]}_data"), sg.Text("", key=f"{remaining_ports[index+1]}_data")])
    # # right_layout.append([sg.Text("", key=f"{remaining_ports[index+1]}_data")])



right_column = sg.Column(right_layout, scrollable=True if len(remaining_ports) > 20 else False , vertical_scroll_only=True, expand_x= True, expand_y=True
                         , sbar_relief='RELIEF_RIDGE', sbar_width=10,sbar_trough_color='white', vertical_alignment='top')

# Add the left and right columns to the main layout
main_layout.append([left_column, sg.VSeperator(), right_column])

# Specify the desired window size
window_size = (1200, 550)  # Width, Height

# Create the main window
main_window = sg.Window("Airdata Logger (Version 1.0)", main_layout, size=window_size, finalize=True, use_default_focus=False, icon=r'logo2.ico')
main_window.TKroot.focus_force()
main_window.bind("<space>", "space")
main_window.bind("<Control_L><s>", "ctrl-s")
main_window.bind("<Control_L><S>", "ctrl-s")

# Start reading data from serial ports
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for port in selected_ports:
        data_dict[port] = main_window[port]
        data_dict[f"{port}_data"] = main_window[f"{port}_data"]
        if port in additional_ports:
            futures.append(executor.submit(read_ref_serial, port))
        else:
            futures.append(executor.submit(read_serial, port))

    while True:
        event, values = main_window.read()
        if event == sg.WINDOW_CLOSED:
            executor.shutdown(wait=False, cancel_futures=True)
            os.kill(os.getpid(),signal.SIGILL)
            sys.exit()
            break

        # Handle capture button event
        if event in ("Capture", "space"):
            # Capture data from all ports
            capture(selected_ports)
            for port in selected_ports:
                current_data = data_dict[f"{port}"].get()
                # TODO: Process the captured data as needed
                # print(f"Captured data from {port}: {current_data}")

        # Handle capture button event
        elif event in ("Save", "ctrl-s"):
            #print('save')
            directory_path = select_directory_popup()
            print(directory_path)
            SaveData(remaining_ports, directory_path)


# Close the windows
main_window.close()
