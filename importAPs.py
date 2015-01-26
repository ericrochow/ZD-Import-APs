#!/usr/bin/python
from csv import DictReader
from re import sub
tla = raw_input("What is the site's TLA? ")
zone = raw_input("What is the zone's TLA? ")
csvfile = tla.lower() + 'APs.csv'
zd = DictReader(open(csvfile, 'rb'), delimiter=',', quotechar='"')
f = open('%sAPcommands.txt' % tla.lower(),'w')
#Add line at beginning of file to enter enable mode
f.write("enable\n")
#Cycle through contents of CSV to create config lines for each AP
for row in zd:
    row['mac'] = sub('[^A-Za-z0-9]+', '', row['mac'])
    row['mac'] = sub(r'(..)(..)(..)(..)(..)(..)',r'\1:\2:\3:\4:\5:\6',row['mac'].lower())
    f.write("config\n")
    f.write("ap %s\n" % row['mac'])
    f.write("devname %s\n" % row['name'])
    f.write("group name %s Zone\n" % zone.upper())
    f.write("location \"%s %s\"\n" % (tla.upper(), row['location']))
    f.write("description \"%s %s\"\n" % (tla.upper(), row['location']))
    f.write("end\n")
    f.write("quit\n")
f.close()
ssh = raw_input("Would you like to automatically add these APs to the Zone Director? ")
if ssh.lower() == "yes" or ssh.lower() == "y":
    import paramiko
    from getpass import getpass
    from time import sleep
    #Prompt for ZD login info
    ip = raw_input("Zone Director IP: ")
    username = raw_input ("Username: ")
    passwd = getpass()
    f = open('%sAPcommands.txt' % tla.lower(),'r')
    commands = f.read()

    #Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    #Automatically add untrusted hosts
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Initiate SSH connection
    remote_conn_pre.connect(ip, username=username, password=passwd)
    print "SSH connection established to %s" % ip
    
    #Establish an interactive session
    remote_conn = remote_conn_pre.invoke_shell()
    print "Interactive SSH session established"
    
    #Wait for prompt, then send commmands in the file
    sleep(2)
    remote_conn.send(commands)
    sleep(30)
    
    #Print output to the console
    print(remote_conn.recv())
    
else:
    print "Goodbye"