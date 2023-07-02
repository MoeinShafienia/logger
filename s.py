import concurrent.futures
import serial
import sys
import keyboard
import time
import re
import PySimpleGUI as sg
import threading
import csv
import os

import serial.tools.list_ports

sg.theme('GrayGrayGray')

data_for_save = []

def select_directory_popup():
    # Define the layout for the popup
    layout = [
        [sg.Text("Select a directory:")],
        [sg.Input(), sg.FolderBrowse()],
        [sg.Button("OK")]
    ]

    # Create the popup window
    window = sg.Window("Popup with FolderBrowse", layout)

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
        print(f"Data has been successfully written to the file '{file_path}'.")
    except IOError:
        print(f"Error writing to the file '{file_path}'.")

def SaveData(ports, directory_path):
    try:
        print(1)
        print(data_for_save)
        write_csv_file(directory_path + '/sample.csv', data_for_save)
        write_list_of_lists_to_file(directory_path + '/abs.txt', remove_columns_for_abs(data_for_save), ports)
        write_list_of_lists_to_file(directory_path + '/diff.txt', remove_columns_for_diff(data_for_save), ports)
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
        print("File not found.")
    except IOError:
        print("Error reading the file.")

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
    print(source_ports)
    if port in source_ports:
        if port in prev_data_dict:
            prev_data_dict[port].append(value)
            data_dict[port].Update("\n".join(map(str, prev_data_dict[port][-4:])))
        else:
            prev_data_dict[port] = []
            prev_data_dict[port].append(value)
            data_dict[port].Update("\n".join(map(str, prev_data_dict[port][-4:])))
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

    print('here')
    for i in range(5):
        ser.write('*00p2'.encode())
    print('here2')

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

# Create the initial page layout
initial_layout = [
    [sg.Text("Select an option:")],
    [sg.Button("Load New Ports")],
    [sg.Button("Load Previous Ports")]
]

# Create the initial page window
window_size = (1200, 600)
initial_window = sg.Window("Serial Port Loader", initial_layout, size = window_size)
show_second_page = True
# Event loop for the initial page
while True:
    event, values = initial_window.read()

    # Handle events on the initial page
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Load New Ports":
        # TODO: Implement the code for loading new ports
        # Show the number of ports selection page
        initial_window.hide()
        break
    elif event == "Load Previous Ports":
        selected_ports = get_selected_ports_from_file()
        source_ports = selected_ports[:2]
        show_second_page = False
        # Show the main page with previous ports
        initial_window.hide()
        break

if show_second_page is True:
    # Create the number of ports selection page layout
    num_ports_layout = [
        [sg.Text("Select the number of ports:")],
        [sg.Combo([i for i in range(1, 59)], size=(10, 1))],
        [sg.Button("Next")]
    ]

    # Create the number of ports selection page window
    num_ports_window = sg.Window("Number of Ports Selection", num_ports_layout)

    # Event loop for the number of ports selection page
    while True:
        event, values = num_ports_window.read()

        # Handle events on the number of ports selection page
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Next":
            num_ports = int(values[0])
            # Show the port selection page with the selected number of ports
            num_ports_window.hide()
            break

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
            combo_boxes.append([sg.Text(f"{counter+1}."), sg.Combo(get_available_com_ports(), size=(10, 1))])
            counter += 1
        combo_layout.append(sg.Column(combo_boxes))
        combo_boxes.clear()
        column = num_combos_per_column
    port_selection_layout.append(combo_layout)
    port_selection_layout.append([sg.Button("Next")])

    # Create the port selection page window
    port_selection_window = sg.Window("Port Selection", port_selection_layout)

    # Event loop for the port selection page
    while True:
        event, values = port_selection_window.read()

        # Handle events on the port selection page
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Next":
            selected_ports = [values[i] for i in range(num_ports)]  # Exclude the "Next" button value
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
flag = 1
for port in additional_ports:
    if(flag):
        left_layout.append([sg.Text(f"refA", justification='left', font=("Calibri", 12))])
    else:
        left_layout.append([sg.Text(f"refD", justification='left', font=("Calibri", 12))])
    flag = 0
    left_layout.append([sg.Multiline("", key=port, size=(40, 4), no_scrollbar=True)])
    left_layout.append([sg.Text("", key=f"{port}_data")])

left_column = sg.Column(left_layout)

# Create a vertical box for the right side (remaining ports)
right_layout = []
for index, port in enumerate(remaining_ports):
    right_layout.append([sg.Text(f"Airdata#{index+1}", justification='left', font=("Calibri", 12))])
    right_layout.append([sg.Multiline("", key=port, no_scrollbar=True)])
    right_layout.append([sg.Text("", key=f"{port}_data")])
right_column = sg.Column(right_layout)

# Add the left and right columns to the main layout
main_layout.append([left_column, sg.VSeperator(), right_column])

main_layout.append([sg.Button("Capture", size=(20, 4), font=("Calibri", 14), border_width=3)])  # Add a single capture button for all ports
main_layout.append([sg.Button("Save", size=(20, 4), font=("Calibri", 14), border_width=3)])  # Add a single capture button for all ports

# Specify the desired window size
window_size = (1200, 600)  # Width, Height

# Create the main window
main_window = sg.Window("Serial Port Data", main_layout, size=window_size)

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
            break

        # Handle capture button event
        if event == "Capture":
            # Capture data from all ports
            capture(selected_ports)
            for port in selected_ports:
                current_data = data_dict[f"{port}"].get()
                # TODO: Process the captured data as needed
                # print(f"Captured data from {port}: {current_data}")

        # Handle capture button event
        elif event == "Save":
            directory_path = select_directory_popup()
            print(directory_path)
            SaveData(remaining_ports, directory_path)

# Close the windows
main_window.close()
