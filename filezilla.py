import ftplib
import os, sys
import time

#CONFIGURATION
CRONOS_IP = '192.168.100.133'
user = 'imc'
pw = 'imc'
cronos_dir = 'pcmcia/EMB_LRV_BRTB_10kN'
destination_dir = '/home/pi/Documents'

def cronos_connect(CRONOS_IP,user,pw):
    try:
        ftp = ftplib.FTP(CRONOS_IP,user,pw)
        ftp.encoding = 'utf-8'
        print ("Connection established!\n")
        return ftp
    except ftplib.error_perm as e:
        print("Connection could not be established! Check IP, user and password.")

def pi_mkdir(directory):
    if not os.path.isdir(directory):
        oldmask = os.umask(000)
        os.makedirs(directory,mode=0o777)
        os.umask(oldmask)

def send2cloud_rasp(source_folder):
    sendString= 'blobxfer upload  --storage-account testbenchpi4 --sas "?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2023-08-09T17:30:05Z&st=2022-02-10T10:30:05Z&spr=https&sig=%2BkcIcyTpUK0tHDiSBW4gC%2FvZP%2BrvSa5YS2neC7X%2BnfM%3D" --remote-path achimpi4 --local-path /home/pi/Documents/pcmcia/EMB_LRV_BRTV_10kN'
    
    folder="/home/pi/github/log_data/"
    messfiles=makeFileList(folder)                 
    print(messfiles)
    for everyfile  in messfiles:
        os.system(sendString+str(folder)+str(everyfile))
    writeLogfile(messfiles)
        
def cronos2pi(cronos_dir,CRONOS_IP,user,pw):
    pi_mkdir(destination_dir + '/' + cronos_dir)
    ftp = cronos_connect(CRONOS_IP,user,pw)
    folders_cronos = ftp.nlst(cronos_dir)
    ftp.quit()
    for i,folder in zip(range(2),folders_cronos):
        print(folder)
        ftp = cronos_connect(CRONOS_IP,user,pw)
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
        #send folder to cloud
        #sendString = 'blobxfer upload --storage-account-key dKjupim22gOrMOdYfY5cWZNDBzph3TJp+/qj6Z7JMZsXB7h/w31jRiZZ3owpiXhByzhMQ13eRAmbKrxrcdWwQw== --storage-account cronos2pi --remote-path cronos-test/pcmcia --local-path /home/pi/Documents/pcmcia/' 
        sendString = 'blobxfer upload --storage-account testbenchpi4 --sas "?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2023-08-09T17:30:05Z&st=2022-02-10T10:30:05Z&spr=https&sig=%2BkcIcyTpUK0tHDiSBW4gC%2FvZP%2BrvSa5YS2neC7X%2BnfM%3D" --remote-path "achimpi4" --local-path "/home/pi/Documents/pcmcia"'
        os.system(sendString)
        print("Download finished!\n")
        ftp.quit()
    
cronos2pi(cronos_dir,CRONOS_IP,user,pw)
sys.exit()
        
# from azure.storage.blob import BlockBlobService
# 
# container = 'cronos-test'
# block_blob_service = BlockBlobService(account_name='cronos2pi', account_key='dKjupim22gOrMOdYfY5cWZNDBzph3TJp+/qj6Z7JMZsXB7h/w31jRiZZ3owpiXhByzhMQ13eRAmbKrxrcdWwQw==')
# content = block_blob_service.list_blobs(container)
# blobcontentList = []
# for blob in content:
#     blobcontentList.append(blob.name)





    

