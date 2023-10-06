import paramiko
import sys
import re
import pandas as pd
import os

host = "10.39.31.3"
username = "comba"
password = "2WSXzaq1"

Sum_CellName = []
Sum_IP = []
Package_Loss = []
PingTime = "5s"
Sum_Status = []
Sum_Gateway = []

### Create DATAFRAME

def PingComba_Function():
    checkClearCommand = 0
    MainData = pd.read_excel('2GCOMBA_IP.xlsx', dtype=str)
    print(MainData)
    CellNames = MainData['CELLNAME'].tolist()
    IPAddresses = MainData['WANIP'].tolist()
    List_STATUS = MainData['Current STATUS'].tolist()
    wanGateway = MainData['WAN GATEWAY'].tolist()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # perform ssh login to host/device
    try:
        ssh.connect(host, port=22, username='comba', password='2WSXzaq1', look_for_keys=False, allow_agent=False)
        
        # exit upon exception
    except paramiko.SSHException:
        print("Connection Failed")
        quit()

    # Issue commands on host/device after login, for eg ping
    # command="ping 10.39.67.42"
    i = 0
    for ip in IPAddresses:
        checkClearCommand += 1
        command = f"ping -c 5 -s 9000 {ip}"
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

        output = ssh_stdout.read()
        error = ssh_stderr.read()
        # print(output)
        # print(error)

        list_output = str(output).split(",")
        # print(list_output)
        packet_loss = list_output[2].split('packet loss')
        # print(packet_loss[0])
        # print(type(packet_loss[0]))
        val_PackageLoss = packet_loss[0].split("%")[0]
        val_PackageLoss = int(val_PackageLoss)
        # print(int(val_PackageLoss))
        # return
        # if packet_loss[0] != "0":
        #     print("****************************     FAILED   ****************************")
        #     print(f"CELLNAME: {CellNames[i]} with IP: {ip}")
        #     print("PACKET LOSS: ",packet_loss[0])
        # else:
        #     print("****************************     WORKING NORMAL   ****************************")
        #     print(f"CELLNAME: {CellNames[i]} with IP: {ip}")
        #     print("PACKET LOSS: ",packet_loss[0])
        
        # print(i)
        # print(int(packet_loss[0]))
        if val_PackageLoss > 0:
            Sum_CellName.append(CellNames[i])
            Sum_IP.append(ip)
            Package_Loss.append(packet_loss[0])
            Sum_Status.append(List_STATUS[i])
            Sum_Gateway.append(wanGateway[i])
            
            print("\n\n****************************     FAILED   ****************************")
            print(f"CELLNAME: {CellNames[i]} with IP: {ip} PACKET LOSS: {packet_loss[0]}")
            print(f"TOTAL OF BIT-ERRORs: {len(Sum_CellName)} SITES")
            print(f"TOTAL HAS CHECKED: {i} SITES")
        if checkClearCommand > 15:
            os.system('cls')
            checkClearCommand = 0
        if int(len(Sum_CellName)) == 5:
            CellBitError={
                "NE":Sum_CellName,
                'WAN GATEWAY': Sum_Gateway,
                "WANIP":Sum_IP,
                "PingTime": PingTime,
                "Package Loss %": Package_Loss,
                "STATUS ONLINE": Sum_Status
            }
            print(CellBitError)
            DATA_F = pd.DataFrame(CellBitError)
            print(type(DATA_F))
            DATA_F = DATA_F.drop_duplicates(keep='first')
            DATA_F.to_excel(f'CellBitError.xlsx', index=False, header=True, sheet_name="BitError")
            
        i+=1
    if int(len(Sum_CellName)) > 0:
        CellBitError={
                "NE":Sum_CellName,
                'WAN GATEWAY': Sum_Gateway,
                "WANIP":Sum_IP,
                "PingTime": PingTime,
                "Package Loss %": Package_Loss,
                "STATUS ONLINE": Sum_Status
            }
        DATA_F = pd.DataFrame(CellBitError)
        DATA_F = DATA_F.drop_duplicates(keep='first')
        DATA_F.to_excel(f'CellBitError.xlsx', index=False, header=True, sheet_name="BitError")
        
    
PingComba_Function()