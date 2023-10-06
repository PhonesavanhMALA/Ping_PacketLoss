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


import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
import subprocess
import threading
import platform






cwd = os.getcwd()
output = 'csbLiKdofanny/OOP/Schema/akkop/one_jqu/oplak/AUTOPING.xlsx'

# Create a new window
root = tk.Tk()
root.geometry('400x300')

# Create a Text widget to display the output
text = tk.Text(root, wrap='word')
text.pack(fill='both', expand=True)

# Create a notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)



    

def ping_host():

    
    host = "10.39.31.3"
    username = "comba"
    Combapassword = "2WSXzaq1"
    # Ask the user to browse for a file
    file_path = filedialog.askopenfilename()
    ### GET BSCIP
    fileName = str(file_path)
    # Get the file name from the file path
    file_name = file_path.split('/')[-1]
    # Ask the user for input to name the new tab
    name = file_name.split(".")[0]
    print(file_name)
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
    
    ### Get from file
    BSCIP = pd.read_excel(f'{fileName}', sheet_name="BSCIP", dtype=str)
    bscIP = BSCIP['BSCIP'][0]
    passwordBSC = BSCIP['bscPassword'][0]
    
    
    
    ## Connect to NMS
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh1.connect(host, username=username, password=Combapassword)
    # Connect to BSC. Depends on bsc or IP
    ssh2 = ssh1.invoke_shell()
    ssh2.send(f'ssh root@{bscIP}\n')
    time.sleep(2)
    # Check if the security warning message is being displayed
    if ssh2.recv_ready():
        output = ssh2.recv(4096).decode()
        if "Are you sure you want to continue connecting" in output:
            print("Security warning message detected.")
            ssh2.send(f'yes\n')
        else:
            ssh2.send(f'{passwordBSC}\n')
    time.sleep(1)
    if ssh2.recv_ready():
        ssh2.send(f'{passwordBSC}\n')
        
    else:
        ssh2 = ssh1.invoke_shell()
        ssh2.send(f'ssh root@{bscIP}\n')
        
    # Check if the SSH connection is still active
    transport = ssh2.get_transport()
    if transport and transport.is_active():
        print('SSH connection is active')
        ### Get time
        startTime = getTime()
        
        ### ASK USER AUTO OR MANUAL
        modePing = simpledialog.askstring('SELECT MODE', 'ENTER AUTO OR MANUAL')
        modePing = str(modePing).upper()
        if modePing[0] == "A":
            PackageSize = 3000
            pingTimer = 1000
            pingTimer = int(pingTimer)
            ### Username and Password use for login COMBA NMS AND BSC
            command = "df"
            rootBSC = f"ssh root@{bscIP}"
            bscPassword = passwordBSC
        elif modePing[0] == "M":
            PackageSize = str(input("PLEASE ENTER PACKET SIZE : "))
            # Ask the user for input to connect to the remote host
            username = simpledialog.askstring('SSH Connection', 'Enter your username on the remote host:')
            Combapassword = simpledialog.askstring('SSH Connection', 'Enter your password on the remote host:', show='*')
            rootBSC = f"ssh root@{bscIP}"
            bscPassword = passwordBSC
        else:
            error_input = input("INPUT WAS WRONG! ENTER TO EXIT......")
        
        
        ###############################
        time.sleep(0.2)
        try:
            ### Prepaire information to Ping
            print("HERE...")
            checkClearCommand = 0
            MainData = pd.read_excel(f'{fileName}', dtype=str)
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
                

            
            # Run a command on the second server and capture the output
            while True:
                # Start the Tkinter event loop
                
                i = 0
                TotalCheck = 0
                checkWriteFile = 0
                length_of_sites = int(len(IPAddresses))
                startPingTime = []
                endPingTime = []
                ### Declar params
                Sum_CellName = []
                Sum_IP = []
                Package_Loss = []
                Sum_Status = []
                Sum_Gateway = []
                for ip in IPAddresses:
                    gST_Ping = getTime()
                    TotalCheck += 1
                    command = f"ping {ip} -s {PackageSize} -i 0.1 -c {pingTimer}"
                    ssh2.send(f'{command}\n')
                    
                    # Wait for the command output to appear
                    channel_buffer = ''
                    while not channel_buffer.endswith('# '):
                        channel_buffer = ssh2.recv(1024).decode()
                        print(f'BSCIP:{bscIP}, {channel_buffer}')
                        # Insert the string into the Text widget
                        text.insert('end', channel_buffer)
                        text.see('end')
                    
                    

                    try:
                        # Extract the packet loss from the command output
                        packet_loss = re.search(r'(\d+)% packet loss', channel_buffer)
                        val_packetLoss = int(packet_loss.group(1))
                        gEnd_Ping = getTime()
                        if val_packetLoss > 0 and str(List_STATUS[i])[0].upper() != "N":
                            checkWriteFile += 1
                            ### Add information to list
                            Sum_CellName.append(CellNames[i])
                            Sum_IP.append(ip)
                            Package_Loss.append(val_packetLoss)
                            Sum_Status.append(List_STATUS[i])
                            Sum_Gateway.append(wanGateway[i])
                            startPingTime.append(str(gST_Ping))
                            endPingTime.append(str(gEnd_Ping))
                            
                        ### To clear monitor
                        if checkClearCommand >= 3:
                            # use the clear_screen() function to clear the console screen
                            clear_screen()
                            checkClearCommand = 0
                    except Exception:
                        pass
                    
                    print("************************************************")
                    print(f"CellName: {CellNames[i]}, STATUS: {List_STATUS[i]}")
                    print(f"TOTAL OF BIT-ERRORs: {len(Sum_CellName)} SITES")
                    print(f"TOTAL HAS CHECKED: {TotalCheck} SITES")
                    time.sleep(0.5)
                    os.system('cls')
                    ### Plus 1 each loop
                    checkClearCommand +=1
                    i+=1
                    length_of_sites -= 1
                    if checkWriteFile == 10:
                        time.sleep(0.5)
                        endTime = getTime()
                        CellBitError={
                                "NE":Sum_CellName,
                                'WAN GATEWAY': Sum_Gateway,
                                "WANIP":Sum_IP,
                                "pingTimer": f'{(pingTimer)}',
                                "Package Loss %": Package_Loss,
                                "STATUS ONLINE": Sum_Status,
                                "START TIME": startPingTime,
                                "END TIME": endPingTime
                            }
                        DATA_F = pd.DataFrame(CellBitError)
                        DATA_F = DATA_F.drop_duplicates(keep='first')
                        DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
                        checkWriteFile = 0
                    elif length_of_sites == 0:
                        if int(len(Sum_CellName)) > 0:
                            time.sleep(0.5)
                            endTime = getTime()
                            CellBitError={
                                    "NE":Sum_CellName,
                                    'WAN GATEWAY': Sum_Gateway,
                                    "WANIP":Sum_IP,
                                    "pingTimer": f'{pingTimer}',
                                    "Package Loss %": Package_Loss,
                                    "STATUS ONLINE": Sum_Status,
                                    "START TIME": startPingTime,
                                    "END TIME": endPingTime
                                }
                            DATA_F = pd.DataFrame(CellBitError)
                            DATA_F = DATA_F.drop_duplicates(keep='first')
                            DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
                            checkWriteFile = 0
        except Exception as e:
            print("Exception")
            time.sleep(0.5)
            endTime = getTime()
            print("ERROR PLS at Exception")
            print(f"Error: {e}")
        finally:
            print("FINAL:::")
            if int(len(Sum_CellName)) > 0:
                
                time.sleep(1)
                endTime = getTime()
                CellBitError={
                            "NE":Sum_CellName,
                            'WAN GATEWAY': Sum_Gateway,
                            "WANIP":Sum_IP,
                            "pingTimer": f'{pingTimer}',
                            "Package Loss %": Package_Loss,
                            "STATUS ONLINE": Sum_Status,
                            "START TIME": startPingTime,
                            "END TIME": endPingTime
                        }
                DATA_F = pd.DataFrame(CellBitError)
                DATA_F = DATA_F.drop_duplicates(keep='first')
                DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
                checkWriteFile = 0
            ssh1.close()
            ssh2.close()
    
    
    
    
    
      

    


def getTime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M-%S")
    current_time = f'{current_time}'
    return current_time
    


def CheckLicense():
    print("RUNNING CHECKING")
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
            return ping_host()
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
        # os.system('cls')
        print(e)
        x = input("ENTER TO EXIT: ")
    
def runPing():  
    time.sleep(0.2)
    try:
        ### Prepaire information to Ping
        checkClearCommand = 0
        MainData = pd.read_excel(f'{fileName}.xlsx', dtype=str)
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
        while True:
            i = 0
            TotalCheck = 0
            checkWriteFile = 0
            length_of_sites = int(len(IPAddresses))
            startPingTime = []
            endPingTime = []
            ### Declar params
            Sum_CellName = []
            Sum_IP = []
            Package_Loss = []
            Sum_Status = []
            Sum_Gateway = []
            for ip in IPAddresses:
                gST_Ping = getTime()
                TotalCheck += 1
                command = f"ping {ip} -s {PackageSize} -i 0.1 -c {pingTimer}"
                ssh2.send(f'{command}\n')
                
                # Wait for the command output to appear
                channel_buffer = ''
                while not channel_buffer.endswith('# '):
                    channel_buffer = ssh2.recv(1024).decode()
                    print(f'BSCIP:{bscIP}, {channel_buffer}')

                try:
                    # Extract the packet loss from the command output
                    packet_loss = re.search(r'(\d+)% packet loss', channel_buffer)
                    val_packetLoss = int(packet_loss.group(1))
                    gEnd_Ping = getTime()
                    if val_packetLoss > 0 and str(List_STATUS[i])[0].upper() != "N":
                        checkWriteFile += 1
                        ### Add information to list
                        Sum_CellName.append(CellNames[i])
                        Sum_IP.append(ip)
                        Package_Loss.append(val_packetLoss)
                        Sum_Status.append(List_STATUS[i])
                        Sum_Gateway.append(wanGateway[i])
                        startPingTime.append(str(gST_Ping))
                        endPingTime.append(str(gEnd_Ping))
                        
                    ### To clear monitor
                    if checkClearCommand >= 3:
                        # use the clear_screen() function to clear the console screen
                        clear_screen()
                        checkClearCommand = 0
                except Exception:
                    pass
                
                print("************************************************")
                print(f"CellName: {CellNames[i]}, STATUS: {List_STATUS[i]}")
                print(f"TOTAL OF BIT-ERRORs: {len(Sum_CellName)} SITES")
                print(f"TOTAL HAS CHECKED: {TotalCheck} SITES")
                time.sleep(0.5)
                os.system('cls')
                ### Plus 1 each loop
                checkClearCommand +=1
                i+=1
                length_of_sites -= 1
                if checkWriteFile == 10:
                    time.sleep(0.5)
                    endTime = getTime()
                    CellBitError={
                            "NE":Sum_CellName,
                            'WAN GATEWAY': Sum_Gateway,
                            "WANIP":Sum_IP,
                            "pingTimer": f'{(pingTimer)}',
                            "Package Loss %": Package_Loss,
                            "STATUS ONLINE": Sum_Status,
                            "START TIME": startPingTime,
                            "END TIME": endPingTime
                        }
                    DATA_F = pd.DataFrame(CellBitError)
                    DATA_F = DATA_F.drop_duplicates(keep='first')
                    DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
                    checkWriteFile = 0
                elif length_of_sites == 0:
                    if int(len(Sum_CellName)) > 0:
                        time.sleep(0.5)
                        endTime = getTime()
                        CellBitError={
                                "NE":Sum_CellName,
                                'WAN GATEWAY': Sum_Gateway,
                                "WANIP":Sum_IP,
                                "pingTimer": f'{pingTimer}',
                                "Package Loss %": Package_Loss,
                                "STATUS ONLINE": Sum_Status,
                                "START TIME": startPingTime,
                                "END TIME": endPingTime
                            }
                        DATA_F = pd.DataFrame(CellBitError)
                        DATA_F = DATA_F.drop_duplicates(keep='first')
                        DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
                        checkWriteFile = 0
    except Exception as e:
        print("Exception")
        time.sleep(0.5)
        endTime = getTime()
        print("ERROR PLS at Exception")
        print(f"Error: {e}")
    finally:
        print("FINAL:::")
        if int(len(Sum_CellName)) > 0:
            
            time.sleep(1)
            endTime = getTime()
            CellBitError={
                        "NE":Sum_CellName,
                        'WAN GATEWAY': Sum_Gateway,
                        "WANIP":Sum_IP,
                        "pingTimer": f'{pingTimer}',
                        "Package Loss %": Package_Loss,
                        "STATUS ONLINE": Sum_Status,
                        "START TIME": startPingTime,
                        "END TIME": endPingTime
                    }
            DATA_F = pd.DataFrame(CellBitError)
            DATA_F = DATA_F.drop_duplicates(keep='first')
            DATA_F.to_excel(f'RESULT EXCEL FILE/{bscName} CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
            checkWriteFile = 0
        ssh1.close()
        ssh2.close()
        
# def makeDataframe(Sum_CellName,Sum_Gateway,Sum_IP,pingTimer,Package_Loss,Sum_Status):
#     CellBitError={
#                     "NE":Sum_CellName,
#                     'WAN GATEWAY': Sum_Gateway,
#                     "WANIP":Sum_IP,
#                     "pingTimer": f'{pingTimer}',
#                     "Package Loss %": Package_Loss,
#                     "STATUS ONLINE": Sum_Status
#                 }
#             DATA_F = pd.DataFrame(CellBitError)
#             DATA_F = DATA_F.drop_duplicates(keep='first')
#             DATA_F.to_excel(f'CellBitError {startTime} - {endTime}.xlsx', index=False, header=True, sheet_name="BitError")
#     return DATA_F
# clear the console screen
def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')
    else:  # for Unix-based systems
        os.system('clear')
        
# CheckLicense()

# Create a button to execute the remote commands
button = tk.Button(root, text='Execute Remote Commands', command=CheckLicense)
button.pack()

root.mainloop()

