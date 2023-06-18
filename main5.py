import concurrent.futures
from tkinter.font import names
import serial
import sys, keyboard, time, re
import tkinter as tk
import threading

dict = {"COM30" : 1, "COM31": 1, "COM32": 1, "COM33": 1}

def update_variables(port, value):
    print(dict)
    dict[port].config(text="Variable 1: " + str(value))

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
                        update_variables(port, line)
                    #data = re.split(',|\*', c)
                    if(keyboard.is_pressed('q')):
                        if(press):
                            data = re.split(',|\*', line)
                            print(data)
                            update_variables(port, data)
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

if __name__ == '__main__':
    # Create a ProcessPoolExecutor with 5 worker processes
    with concurrent.futures.ProcessPoolExecutor(max_workers=60) as executor:
        # Submit the function to the executor and get a Future object
        ports = ["COM30", "COM31", "COM32", "COM33"]
        results = []
        for port in ports:
            future = executor.submit(readSerial, port)

        ### new code
        # Create the main window
        window = tk.Tk()

        # Set the window title
        window.title("Real-time Variable Display")

        # Set the window dimensions
        window.geometry("400x300")  # Width x Height
        
        for port in ports:

            # Create label widgets to display the variable values
            variable1_label = tk.Label(window, text="Variable :")
            variable1_label.pack()

            dict[port] = variable1_label
            print(dict)
        

        # Start updating the variable values and labels
        # update_variables('nothing yet!')

        # Start the Tkinter event loop
        window.mainloop()
        ###