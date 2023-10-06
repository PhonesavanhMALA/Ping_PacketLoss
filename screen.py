import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
import subprocess
import threading
import platform

root = tk.Tk()
root.geometry('400x300')

# Create a notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

def ping_host():
    # Ask the user for input to name the new tab
    name = simpledialog.askstring('Tab Name', 'Enter a name for the new tab:')
    
    print(name)

    # Ask the user to browse for a file
    file_path = filedialog.askopenfilename()
    # Get the file name from the file path
    file_name = file_path.split('/')[-1]
    print(file_name)
    # Ask the user for input to set the options for the ping command
    interval = simpledialog.askstring('Ping Options', 'Enter the interval in seconds (default is 1):', initialvalue='1')
    size = simpledialog.askstring('Ping Options', 'Enter the size of the packet in bytes (default is 56):', initialvalue='56')
    count = simpledialog.askstring('Ping Options', 'Enter the number of packets to send (default is 4):', initialvalue='4')

    # Convert the size input to an integer and validate it
    try:
        size = int(size)
        if size < 1 or size > 65507:
            size = 56
    except ValueError:
        size = 56

    # Create a new tab and add a label and close button to it
    tab = tk.Frame(notebook)
    notebook.add(tab, text=name)

    label_frame = tk.Frame(tab, height=25)
    label_frame.pack(side='top', fill='x')

    label = tk.Label(label_frame, text=name)
    label.pack(side='left')

    # Create a close button for the tab
    close_button = ttk.Button(label_frame, text='X', command=lambda: notebook.forget(notebook.index(tab)))
    close_button.pack(side='right', padx=(0, 2), anchor='n')

    # Run the ping command in a separate process
    if platform.system() == 'Windows':
        command = ['ping', '-n', count, '-w', str(int(interval*1000)), '-l', str(size), 'google.com']
    else:
        command = ['ping', '-i', interval, '-s', str(size), '-c', count, 'google.com']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)

    # Define a function to read the process output in a separate thread
    def read_output():
        while True:
            line = process.stdout.readline()
            if not line:
                break
            text.insert('end', line.decode())
            text.see('end')

    # Create a Text widget to display the output and start the thread
    text = tk.Text(tab, wrap='word')
    text.pack(fill='both', expand=True)
    thread = threading.Thread(target=read_output)
    thread.start()

    # Select the new tab
    notebook.select(tab)

# Create a button that triggers the ping_host function
button = tk.Button(root, text='Ping Google', command=ping_host)
button.pack()

root.mainloop()