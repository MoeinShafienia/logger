import tkinter as tk

# Create the main window
window = tk.Tk()

# Set the window title
window.title("Real-time Variable Display")

# Set the window dimensions
window.geometry("400x300")  # Width x Height

# Create label widgets to display the variable values
variable1_label = tk.Label(window, text="Variable 1:")
variable1_label.pack()

# Function to update the variable values and labels
def update_variables():
    # Replace this with your own logic to update the variables
    # Here, we're simply incrementing two counters for demonstration purposes
    global variable1
    variable1 += 1

    # Update the labels with the new variable values
    variable1_label.config(text="Variable 1: " + str(variable1))

    # Schedule the next update after a certain interval (in milliseconds)
    window.after(1000, update_variables)  # Update variables every 1 second

# Initialize the variables
variable1 = ''

# Start updating the variable values and labels
update_variables()

# Start the Tkinter event loop
window.mainloop()
