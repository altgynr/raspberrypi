import ftplib
import os, sys
import time

#CONFIGURATION
CRONOS_IP = '192.168.100.133'
user = 'imc'
pw = 'imc'
cronos_dir = 'pcmcia/EMB_LRV_BRTB_10kN'
destination_dir = '/home/pi/github_altug/raspberrypi'

def cronos_connect(CRONOS_IP,user,pw):
    try:
        ftp = ftplib.FTP(CRONOS_IP,user,pw)
        ftp.encoding = 'utf-8'
        print ("Connection established!")
        return ftp
    except ftplib.error_perm as e:
        print("Connection could not be established! Check IP, user and password.")

def pi_mkdir(directory):
    if not os.path.isdir(directory):
        oldmask = os.umask(000)
        os.makedirs(directory,mode=0o777)
        os.umask(oldmask)
        
def send2cloud():
    account_name = 'cronos2pi'
    account_key = 'dKjupim22gOrMOdYfY5cWZNDBzph3TJp+/qj6Z7JMZsXB7h/w31jRiZZ3owpiXhByzhMQ13eRAmbKrxrcdWwQw=='
    remote_path = 'cronos-test/pcmcia'
    local_path = '/home/pi/github_altug/raspberrypi/pcmcia/'
    sendString = 'blobxfer upload --storage-account-key {} --storage-account {} --remote-path {} --local-path {}'.format(account_key, account_name, remote_path, local_path)
    os.system(sendString)
    
def send2cloud_achim():
    local_path = '/home/pi/github_altug/raspberrypi/pcmcia/'
    sendString= 'blobxfer upload  --storage-account testbenchpi4 --sas "?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2023-08-09T17:30:05Z&st=2022-02-10T10:30:05Z&spr=https&sig=%2BkcIcyTpUK0tHDiSBW4gC%2FvZP%2BrvSa5YS2neC7X%2BnfM%3D" --remote-path achimpi4/pcmcia --local-path '
    os.system(sendString+local_path)
        
def cronos2pi(cronos_dir,CRONOS_IP,user,pw):
    pi_mkdir(destination_dir + '/' + cronos_dir)
    ftp = cronos_connect(CRONOS_IP,user,pw)
    folders_cronos = ftp.nlst(cronos_dir)
    ftp.quit()
    for i,folder in zip(range(5),folders_cronos):
        ftp = cronos_connect(CRONOS_IP,user,pw)
        print(folder)
        destination_folder = destination_dir + '/' + cronos_dir + '/' + folder
        pi_mkdir(destination_folder)
        ftp.cwd(cronos_dir + '/' + folder)
        files_in_folder = []
        ftp.dir(files_in_folder.append)
        for file in files_in_folder:
            filename = file.split(None, 8)[-1]
            if filename != 'DirClosed': #this is a random empty file
                # download the file
                local_filepath = os.path.join(destination_folder, filename)
                lf = open(local_filepath, "wb")
                ftp.retrbinary("RETR " + filename, lf.write)
                lf.close()   
        ftp.quit()
    print("Raspi upload finished!\n")
    #send folder to cloud
    send2cloud_achim()
    print("Cloud upload finished!\n")
    
cronos2pi(cronos_dir,CRONOS_IP,user,pw)
sys.exit()





    

