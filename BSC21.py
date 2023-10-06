import paramiko
import time
import re


command = "df"
host = "10.39.31.3"
username = "comba"
Combapassword = "2WSXzaq1"

rootBSC = "ssh root@10.39.21.1"
bscPassword = "17518@Comba"
# bschost = '10.39.21.1'

pingTimer = 0.2
try:
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh1.connect(host, username=username, password=Combapassword)
    # Establish an SSH connection to the second server through the first server
    ssh2 = ssh1.invoke_shell()
    ssh2.send('ssh root@10.39.21.1\n')
    time.sleep(2)
    ssh2.send('17518@Comba\n')
    # Wait for the command prompt to appear
    channel_buffer = ''
    while not channel_buffer.endswith('# '):
        print("CHECKING THE NETWORK AND WAITING CONNECTED")
        channel_buffer = ssh2.recv(1024).decode()
    print(channel_buffer)
    # Run a command on the second server and capture the output
    ip = '10.36.73.58'
    command = f"ping -c {pingTimer*60} -s 3000 {ip}"
    ssh2.send(f'{command}\n')
    # Wait for the command output to appear
    channel_buffer = ''
    while not channel_buffer.endswith('# '):
        channel_buffer = ssh2.recv(1024).decode()
        print(channel_buffer)
    # Extract the packet loss from the command output
    packet_loss = re.search(r'(\d+)% packet loss', channel_buffer)
    val_packetLoss = int(packet_loss.group(1))
    if packet_loss:
        print(f"Packet loss: {packet_loss.group(1)}%")
    
except Exception as e:
    print("ERROR PLS")
    print(f"Error: {e}")
finally:
    ssh1.close()
    ssh2.close()

