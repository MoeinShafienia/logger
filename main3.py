import tkinter as tk

# Create the main window
window = tk.Tk()

# Set the window title
window.title("Real-time Variable Display")

# Set the window dimensions
window.geometry("400x300")  # Width x Height

# Function to log the variable values
def log_variables(event):
    # Log the values of the variables
    log_message = "Variable Values:\n"
    for i in range(num_variables):
        log_message += "Variable {}: {}\n".format(i+1, variable_values[i])
    print(log_message)

# Function to update the variable values and labels
def update_variables():
    # Update the values of the variables based on user input
    # variable_values = []
    for i in range(num_variables):
        # Replace this with your own logic to update the variables
        # Here, we're simply incrementing each variable value for demonstration purposes
        variable_values[i] += 1

    # Update the labels with the new variable values
    for i in range(num_variables):
        variable_labels[i].config(text="Variable {}: {}".format(i+1, variable_values[i]))

    # Schedule the next update after a certain interval (in milliseconds)
    window.after(1000, update_variables)  # Update variables every 1 second

# Get the number of variables from the user
num_variables = int(input("Enter the number of variables: "))

# Create label widgets to display the variable values
variable_labels = []
for i in range(num_variables):
    label = tk.Label(window, text="Variable {}: ".format(i+1))
    label.pack()
    variable_labels.append(label)

# Initialize the variable values
variable_values = [0] * num_variables

# Start updating the variable values and labels
update_variables()

# Bind the key press event to the log_variables function
window.bind("<Key>", log_variables)

# Start the Tkinter event loop
window.mainloop()
