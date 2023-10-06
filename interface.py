import tkinter as tk
from tkinter import filedialog
from tkinter import font
from tkinter import ttk

import paramiko
import time
import re
import subprocess
import pandas as pd
import os
from datetime import datetime
from google_drive_downloader import GoogleDriveDownloader as g
from werkzeug.exceptions import InternalServerError
from werkzeug.serving import run_simple
import logging
import requests


def getTime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M-%S")
    current_time = f'{current_time}'
    return current_time
    



cwd = os.getcwd()
output = 'csbLiKdofanny/OOP/Schema/akkop/one_jqu/oplak/AUTOPING.xlsx'
def CheckLicense():
    try:
        os.system('cls')
        # disable console output
        # with open(os.devnull, 'w') as f:
        #     g.download_file_from_google_drive(file_id ='1yrtHgFnx3BMTsbJu-SYfMRgwQr6uHu2D', dest_path=f"{cwd}\{output}", showsize=False)
        respon = g.download_file_from_google_drive (file_id ='1yrtHgFnx3BMTsbJu-SYfMRgwQr6uHu2D', dest_path=f"{cwd}\{output}", overwrite=True, showsize=False)
        os.system('cls')
        time.sleep(2)
        license = pd.read_excel(output, sheet_name="pycharmLicense")
        license = license['STATUS'].values[0]
        os.remove(output)
        

        # license = "t"
        if str(license).upper().startswith('T'):
            os.system('cls')
            return runPing()
        else:
            os.system('cls')
            print("License has expired!")
            print("Ente exit:")
            x = input()
            print("THANKS")
    except requests.exceptions.ConnectionError as err:
        os.system('cls')
        print("PLEASE CONNECT INTERNET")
        time.sleep(5)
    except Exception as e:
        os.system('cls')
        print(e)
        print("License has expired!")
        print("Enter to exit:")
        x = input()
        print("THANKS")
    
def runPing():
    
    ### GET BSCIP
    BSCIP = pd.read_excel('2GCOMBA_IP.xlsx', sheet_name="BSCIP", dtype=str)
    bscIP = BSCIP['BSCIP'][0]
    passwordBSC = BSCIP['bscPassword'][0]
    # return
    
    
    ### Get time
    Startime = getTime()

    ### Username and Password use for login COMBA NMS AND BSC
    command = "df"
    host = "10.39.31.3"
    username = "comba"
    Combapassword = "2WSXzaq1"
    rootBSC = f"ssh root@{bscIP}"
    bscPassword = passwordBSC

    ### Declar params
    Sum_CellName = []
    Sum_IP = []
    Package_Loss = []
    Sum_Status = []
    Sum_Gateway = []


    ### Connect to NMS
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh1.connect(host, username=username, password=Combapassword)
    # Connect to BSC. Depends on bsc or IP
    ssh2 = ssh1.invoke_shell()
    ssh2.send(f'ssh root@{bscIP}\n')
    time.sleep(2)
    ssh2.send(f'{passwordBSC}\n')


    #### Time use to ping (minute)
    os.system('cls')
    print("ENTER NUMBER HOW LONG YOU WANT TO PING IN MINUTES:")
    pingTimer = input()
    pingTimer = int(pingTimer)
    os.system('cls')
    ### Check time
    if pingTimer <= 1:
        minute = "Minute"
    else:
        minute = "Minutes"
    print(f"\nYou have input: {pingTimer} {minute}")
    time.sleep(0.2)
    try:
        ### Prepaire information to Ping
        checkClearCommand = 0
        MainData = pd.read_excel('2GCOMBA_IP.xlsx', dtype=str)
        CellNames = MainData['CELLNAME'].tolist()
        IPAddresses = MainData['WANIP'].tolist()
        List_STATUS = MainData['Current STATUS'].tolist()
        wanGateway = MainData['WAN GATEWAY'].tolist()
        print(MainData)
        
        
        # Wait for the command prompt to appear
        channel_buffer = ''
        while not channel_buffer.endswith('# '):
            print(f"TRY TO CONNECT BSC IP: {bscIP}")
            channel_buffer = ssh2.recv(1024).decode()
        print(channel_buffer)
        
        # Run a command on the second server and capture the output
        i = 0
        for ip in IPAddresses:
            command = f"ping -c {pingTimer*60} -s 3000 {ip}"
            ssh2.send(f'{command}\n')
            
            # Wait for the command output to appear
            channel_buffer = ''
            while not channel_buffer.endswith('# '):
                channel_buffer = ssh2.recv(1024).decode()
                print(channel_buffer)
            print("************************************************")
            print(f"CellName: {CellNames[i]}, STATUS: {List_STATUS[i]}")
            print(f"TOTAL OF BIT-ERRORs: {len(Sum_CellName)} SITES")
            print(f"TOTAL HAS CHECKED: {i} SITES")
            try:
                # Extract the packet loss from the command output
                packet_loss = re.search(r'(\d+)% packet loss', channel_buffer)
                val_packetLoss = int(packet_loss.group(1))
                if packet_loss:
                    ### Add information to list
                    Sum_CellName.append(CellNames[i])
                    Sum_IP.append(ip)
                    Package_Loss.append(val_packetLoss)
                    Sum_Status.append(List_STATUS[i])
                    Sum_Gateway.append(wanGateway[i])
                    
                
                ### To clear monitor
                if checkClearCommand >= 3:
                    # use the clear_screen() function to clear the console screen
                    clear_screen()
                    checkClearCommand = 0
            except Exception:
                pass
            
            
            ### Plus 1 each loop
            checkClearCommand +=1
            i+=1
            
        if int(len(Sum_CellName)) > 0:
            CellBitError={
                    "NE":Sum_CellName,
                    'WAN GATEWAY': Sum_Gateway,
                    "WANIP":Sum_IP,
                    "pingTimer": f'{int(pingTimer*60)}s',
                    "Package Loss %": Package_Loss,
                    "STATUS ONLINE": Sum_Status
                }
            DATA_F = pd.DataFrame(CellBitError)
            DATA_F = DATA_F.drop_duplicates(keep='first')
            DATA_F.to_excel(f'CellBitError {Startime}.xlsx', index=False, header=True, sheet_name="BitError")
    except Exception as e:
        if int(len(Sum_CellName)) > 0:
            CellBitError={
                    "NE":Sum_CellName,
                    'WAN GATEWAY': Sum_Gateway,
                    "WANIP":Sum_IP,
                    "pingTimer": f'{int(pingTimer*60)}s',
                    "Package Loss %": Package_Loss,
                    "STATUS ONLINE": Sum_Status
                }
            DATA_F = pd.DataFrame(CellBitError)
            DATA_F = DATA_F.drop_duplicates(keep='first')
            DATA_F.to_excel(f'CellBitError {Startime}.xlsx', index=False, header=True, sheet_name="BitError")
        print("ERROR PLS")
        print(f"Error: {e}")
    finally:        
        ssh1.close()
        ssh2.close()
        
        
# clear the console screen
def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')
    else:  # for Unix-based systems
        os.system('clear')
        
def select_file():
    file_path = filedialog.askopenfilename()
    print("Selected file:", file_path)

    # Get the filename from the file path
    filename = os.path.basename(file_path)

    # Create a new tab and set its name to the filename
    result_frame = tk.Frame(notebook)
    notebook.add(result_frame, text=filename)

    # Create a Label widget to display the filename
    label = tk.Label(result_frame, text=filename)
    label.pack(expand=True)

    # Center the Label widget in the middle of the tab
    result_frame.update_idletasks()
    label.place(
        x=(result_frame.winfo_width() - label.winfo_width()) / 2,
        y=(result_frame.winfo_height() - label.winfo_height()) / 2
    )

    # Remove the border around the new tab
    style = ttk.Style()
    style.configure("TNotebook", borderwidth=0)

    # Disable the "Select" button
    select_button.config(state="disabled")

    # Switch to the new tab
    notebook.select(result_frame)

# def select_file():
#     file_path = filedialog.askopenfilename()
#     print("Selected file:", file_path)
#     return CheckLicense()
    

def set_theme(theme):
    if theme == "Eva Dark":
        window.config(bg="#2b2b2b")
        button.config(bg="#3d3d3d", fg="#ffffff", relief="flat", activebackground="#2b2b2b")
    elif theme == "Kimbie Dark":
        window.config(bg="#222222")
        button.config(bg="#383838", fg="#ffffff", relief="flat", activebackground="#222222")
    elif theme == "Monokai":
        window.config(bg="#272822")
        button.config(bg="#3c3d37", fg="#f8f8f2", relief="flat", activebackground="#272822")

    button_font = font.Font(family="Arial", size=18, weight="bold")
    button.config(font=button_font, height=1, width=10)


# Create a new window
window = tk.Tk()

notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Set the window size and title
window.geometry("600x400")
window.title("File Selector")

# Create a button to select a file
button = tk.Button(window, text="Select File", command=select_file)
button_font = font.Font(family="Arial", size=18, weight="bold")
button.config(font=button_font, height=1, width=10)
button.place(relx=0.5, rely=0.5, anchor='center')

# Create a menu bar
menu_bar = tk.Menu(window)

# Create a "Theme" menu
theme_menu = tk.Menu(menu_bar, tearoff=0)
theme_menu.add_command(label="Eva Dark", command=lambda: set_theme("Eva Dark"))
theme_menu.add_command(label="Kimbie Dark", command=lambda: set_theme("Kimbie Dark"))
theme_menu.add_command(label="Monokai", command=lambda: set_theme("Monokai"))
menu_bar.add_cascade(label="Theme", menu=theme_menu)

# Attach the menu bar to the window
window.config(menu=menu_bar)

# Set the initial theme
set_theme("Eva Dark")

# Run the application
window.mainloop()