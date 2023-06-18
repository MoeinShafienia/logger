import tkinter as tk
from tkinter import filedialog

# Create the main window
window = tk.Tk()

# Set the window title
window.title("Yo wassap")

# Set the window dimensions
window.geometry("400x300")  # Width x Height

# Function to handle file selection
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        read_numbers(file_path)

# Function to read the numbers from the selected file
def read_numbers(file_path):
    numbers = []
    with open(file_path, "r") as file:
        for line in file:
            number = line.strip()
            numbers.append(number)
    
    display_numbers(numbers)

# Function to display the numbers in labels
def display_numbers(numbers):
    for number in numbers:
        number_label = tk.Label(window, text=number)
        number_label.pack()

# Create a button widget for file selection
select_button = tk.Button(window, text="Select File", command=select_file)
select_button.pack()


# Start the Tkinter event loop
window.mainloop()
