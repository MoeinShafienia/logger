import tkinter as tk
import concurrent.futures
from tkinter.font import names
import serial
import sys, keyboard, time, re
import tkinter as tk
import threading

def readSerial(port) : 
    print(sys.argv[0])
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 9600
    ser.bytesize = serial.SEVENBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_TWO #number of stop bits
    #ser.timeout = None          #block read
    ser.timeout = None          # non blocking read
    ser.xonxoff = False     #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
    ser.writeTimeout = 2     #timeout for write
    Log = []
    c = ""
    line = ""
    try:
        try:
            ser.open()
        except Exception as e:
            print("error open serial port: " + str(e))
            exit()
        press = 1 
        if ser.isOpen():
            try:
                while True:
                    #time.sleep(0.0001)
                    c = c + ser.read(1).decode('ascii')
                    if(c.endswith('\n')):
                        line = c
                        c = ""
                        print(line,end='')
                        print(port)
                        update_variable(port, line)
                    #data = re.split(',|\*', c)
                    if(keyboard.is_pressed('q')):
                        if(press):
                            data = re.split(',|\*', line)
                            print(data)
                            update_variable(port, data)
                            Log.append(tuple((data[3], data[4])))
                        press = 0
                    else:
                        press = 1

                ser.close()
            except Exception as e1:
                    print ("error communicating...: " + str(e1))
                    time.sleep(5)
        else:
                print("cannot open serial port ")
                exit()
    except KeyboardInterrupt:
        print('log')
        time.sleep(1)
        ser.close()
        exit()

with concurrent.futures.ProcessPoolExecutor(max_workers=60) as executor:
    # Create the main window
    window = tk.Tk()

    # Set the window title
    window.title("Real-time Variable Display")

    # Set the window dimensions
    window.geometry("400x300")  # Width x Height
    # Submit the function to the executor and get a Future object
    # Create label widgets to display the variable values
    variable_labels = {}
    variables = {}

    variable_keys = ["COM30", "COM31", "COM32", "COM33"]
    # Define your custom variable keys and initial values
    for key in variable_keys:
        label = tk.Label(window, text=f"Variable {key}:")
        label.pack()
        variable_labels[key] = label
        variables[key] = ''

    results = []
    for port in variable_keys:
        future = executor.submit(readSerial, port)

    # Function to update a specific variable value and label
    def update_variable(key, value):
        # Replace this with your own logic to update the specific variable
        # Here, we're simply incrementing the variable by 1
        variables[key] += value

        # Update the label with the new variable value
        variable_labels[key].config(text=f"Variable {key}: {variables[key]}")

        # Schedule the next update after a certain interval (in milliseconds)
        # window.after(1000, update_variable, key)  # Update the variable again

    # Start the Tkinter event loop
    window.mainloop()
