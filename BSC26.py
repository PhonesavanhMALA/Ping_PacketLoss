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
        # os.system('cls')
        print(e)
        x = input("ENTER TO EXIT: ")
    
def runPing():
    
    ### GET BSCIP
    fileName = str(input("\nPLEASE ENTER FILE NAME .XLSX : "))
    looper = str(input("\nDO YOU WANT TO ALWAYS LOOP? : "))
    ### ASK USER AUTO OR MANUAL
    modePing = str(input("\nENTER AUTO OR MANUAL: ")).upper()
    if modePing[0] == "A":
        PackageSize = 3000
        pingTimer = 1000        
    elif modePing[0] == "M":
        PackageSize = str(input("\nPLEASE ENTER PACKET SIZE : "))
        #### Time use to ping (received)
        pingTimer = input("\nENTER NUMBER HOW LONG YOU WANT TO PING/CELL: ")
    else:
        error_input = input("\nINPUT WAS WRONG! ENTER TO EXIT......")
    pingTimer = int(pingTimer)
    BSCIP = pd.read_excel(f'{fileName}.xlsx', sheet_name="BSCIP", dtype=str)
    bscIP = BSCIP['BSCIP'][0]
    passwordBSC = BSCIP['bscPassword'][0]
    
    
    
    ### Username and Password use for login COMBA NMS AND BSC
    command = "df"
    host = "10.39.31.3"
    username = "comba"
    Combapassword = "2WSXzaq1"
    rootBSC = f"ssh root@{bscIP}"
    bscPassword = passwordBSC
    
    ### TXT NAME
    txt_BSC21 = "BSC21-BitError.txt"
    txt_BSC22 = "BSC22-BitError.txt"
    txt_BSC23 = "BSC23-BitError.txt"
    txt_BSC24 = "BSC24-BitError.txt"
    txt_BSC25 = "BSC25-BitError.txt"
    txt_BSC26 = "BSC26-BitError.txt"

    


    ### Connect to NMS
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


    
    bscName = str(fileName)
    ### Check time
    os.system('cls')
    received = "received"
    # if pingTimer <= 1:
    #     minute = "received"
    # else:
    #     minute = "received"
    print(f"\n\nYou have input: {pingTimer} {received}")
    time.sleep(0.2)
    try:
        # Run a command on the second server and capture the output
        while True:
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
        
        
            ### Get time
            startTime = getTime()
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
                command = f"ping {ip} -s {PackageSize} -i 0.01 -c {pingTimer}"
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
                    if val_packetLoss > 0 and val_packetLoss < 100 and str(List_STATUS[i])[0].upper() != "N":
                        checkWriteFile += 1
                        ### Add information to list
                        Sum_CellName.append(CellNames[i])
                        Sum_IP.append(ip)
                        Package_Loss.append(val_packetLoss)
                        Sum_Status.append(List_STATUS[i])
                        Sum_Gateway.append(wanGateway[i])
                        startPingTime.append(str(gST_Ping))
                        endPingTime.append(str(gEnd_Ping))
                        
                except Exception:
                    pass
                print("ERROR-1")
                ### Check how many cells        
                if int(len(Sum_CellName)) <=1:
                    msgCellName = "CELL"
                else:
                    msgCellName = "CELL"
                    
                if TotalCheck <= 1:
                    msgTotalCheck = "CELL"
                else:
                    msgTotalCheck = "CELLS"
                
                os.system('cls')
                print("************************************************")
                print(f"CellName: {CellNames[i]}, STATUS: {List_STATUS[i]}")
                print(f"TOTAL OF BIT-ERRORs: {len(Sum_CellName)} {msgCellName}")
                print(f"TOTAL HAS CHECKED: {TotalCheck} {msgTotalCheck}")
                time.sleep(10)
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
            ### To run one loop
            if looper[0].upper() == "Y":
                pass
            else:
                break
                ### To shutdown after finish running
                # os.system("shutdown /s /t 1")
            
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
        
CheckLicense()

