import serial
import sys, keyboard, time, re
import tkinter as tk
import threading
import multiprocessing

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

def readSerial(port) : 
    print(sys.argv[0])
    ser = serial.Serial()
    # ser.port = sys.argv[1]
    # ser.baudrate = sys.argv[2]
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
    rl = ReadLine(ser)
    Log = []
    c = ""
    line = ""
    times2 = 0
    times1 = 0
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
                    times1 = times2
                    times2 = time.time()
                    c = c + ser.read(1).decode('ascii')
                    if(c.endswith('\n')):
                        line = c
                        c = ""
                        print(line,end='')
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
        print(Log)
        time.sleep(15)
        ser.close()
        exit()




### new code
# Create the main window
window = tk.Tk()

# Set the window title
window.title("Real-time Variable Display")

# Set the window dimensions
window.geometry("400x300")  # Width x Height

# Create label widgets to display the variable values
variable1_label = tk.Label(window, text="Variable:")
variable1_label.pack()

variable2_label = tk.Label(window, text="Variable:")
variable2_label.pack()

# Function to update the variable values and labels
def update_variables(key, value):
    # Replace this with your own logic to update the variables
    # Here, we're simply incrementing two counters for demonstration purposes
    global my_dict
    my_dict[key] = value

    # Update the labels with the new variable values
    my_dict2[key].config(text="Variable: " + str(value))

# Initialize the variables
my_dict = {sys.argv[1]: '', sys.argv[2]: ''}
my_dict2 = {sys.argv[1]: variable1_label, sys.argv[2]: variable2_label}

pool = multiprocessing.Pool()

numbers = [sys.argv[1], sys.argv[2]]
pool.map(readSerial, numbers)

# Start the Tkinter event loop
window.mainloop()
###