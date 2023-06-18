import pyMultiSerial as p
import tkinter as tk
import threading

ms = p.MultiSerial()

ms.baudrate = 9600
ms.timeout = 2

def port_read_callback(portno, serial, text):
    print ("Received '"+text+"' from port "+portno)
    pass

ms.port_read_callback = port_read_callback


ms.Start()

####

# # Create a new thread and pass the target function and arguments
# thread = threading.Thread(target=readSerial)

# # Start the thread
# thread.start()

# ### new code
# # Create the main window
# window = tk.Tk()

# # Set the window title
# window.title("Real-time Variable Display")

# # Set the window dimensions
# window.geometry("400x300")  # Width x Height

# # Create label widgets to display the variable values
# variable1_label = tk.Label(window, text="Variable 1:")
# variable1_label.pack()

# # Function to update the variable values and labels
# def update_variables(value):
#     # Replace this with your own logic to update the variables
#     # Here, we're simply incrementing two counters for demonstration purposes
#     global variable1
#     variable1 = value

#     # Update the labels with the new variable values
#     variable1_label.config(text="Variable 1: " + str(variable1))

# # Initialize the variables
# variable1 = ''

# # Start updating the variable values and labels
# update_variables('nothing yet!')

# # Start the Tkinter event loop
# window.mainloop()
# ###