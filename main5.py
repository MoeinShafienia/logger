import concurrent.futures
from tkinter.font import names
import serial
import sys, keyboard, time, re
import tkinter as tk
import threading


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
                        # update_variables(line)
                    #data = re.split(',|\*', c)
                    if(keyboard.is_pressed('q')):
                        if(press):
                            data = re.split(',|\*', line)
                            print(data)
                            # update_variables(data)
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
        ports = ['COM30', 'COM31', 'COM32', 'COM33']
        results = []
        for port in ports:
            future = executor.submit(readSerial, port)