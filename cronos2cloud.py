import ftplib
import os, sys
import shutil
import time
from azure.storage.blob import BlockBlobService

https://dhpdataanalyticsstorage.blob.core.windows.net/yanar

# CONFIGURATION
cronos_ip = '192.168.100.133'
user = 'imc'
pw = 'imc'
cronos_dir = 'pcmcia/EMB_LRV_BRTB_10kN' # directory to read from
raspi_dir = '/home/pi/github_altug/raspberrypi' # directory in raspi to save the files

def cronos_connect(cronos_ip,user,pw):
    """ establish the FTP connection to cronos """
    try:
        ftp = ftplib.FTP(cronos_ip,user,pw)
        ftp.encoding = 'utf-8'
        print ("Connection established!")
        return ftp
    except ftplib.error_perm as e:
        print("Connection could not be established! Check IP, user and password.")

def pi_mkdir(directory):
    """ create directory in raspi """
    if not os.path.isdir(directory):
        oldmask = os.umask(000)
        os.makedirs(directory,mode=0o777)
        os.umask(oldmask)
        
def send2cloud_altug():
    """ send files to Azure cloud """
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
    
def get_content_altug():
    account_name = 'cronos2pi'
    account_key = 'dKjupim22gOrMOdYfY5cWZNDBzph3TJp+/qj6Z7JMZsXB7h/w31jRiZZ3owpiXhByzhMQ13eRAmbKrxrcdWwQw=='
    blob_container = 'cronos-test'
    block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
    return block_blob_service, blob_container

def get_content_achim():
    account_name = 'testbenchpi4'
    sas_token = "?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2023-08-09T17:30:05Z&st=2022-02-10T10:30:05Z&spr=https&sig=%2BkcIcyTpUK0tHDiSBW4gC%2FvZP%2BrvSa5YS2neC7X%2BnfM%3D"
    blob_container = 'achimpi4'
    block_blob_service = BlockBlobService(account_name=account_name, sas_token=sas_token)
    return block_blob_service, blob_container
    
def check_cloud_content(actual_data, cloud_name):
    if cloud_name == "Altug":
        block_blob_service, blob_container = get_content_altug()
    else:
        block_blob_service, blob_container = get_content_achim()
    blobContent = block_blob_service.list_blobs(blob_container)
    blobFiles = []
    for content in blobContent:
        content_name_raw = content.name
        if "pcmcia" in content_name_raw:
            content_name = content_name_raw.split('/', 4)[-2]
            blobFiles.append(content_name)
    if actual_data in blobFiles:
        print("Actual Cronos data is already in cloud!")
        return False
    else:
        print("Actual Cronos data is missing in cloud!")
        return True
        
def cronos2pi_all(cronos_dir,CRONOS_IP,user,pw):
    pi_mkdir(destination_dir + '/' + cronos_dir)
    ftp = cronos_connect(CRONOS_IP,user,pw)
    folders_cronos = ftp.nlst(cronos_dir)
    ftp.quit()
    for folder in folders_cronos:
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
        print("Raspi upload finished!")
        #send folder to cloud
        send2cloud_achim()
        print("Cloud upload finished!\n")
        shutil.rmtree(destination_folder)        
        ftp.quit()
    shutil.rmtree(destination_dir + '/pcmcia')
    
def get_actual_cronos_data(cronos_dir,CRONOS_IP,user,pw):
    pi_mkdir(destination_dir + '/' + cronos_dir)
    ftp = cronos_connect(CRONOS_IP,user,pw)
    folders_cronos = ftp.nlst(cronos_dir)
    actual_data = folders_cronos[-2]
    fileMissing = check_cloud_content(actual_data, "Achim")
    if fileMissing:
        print("Actual Cronos data is being uploaded in cloud...")
        destination_folder = destination_dir + '/' + cronos_dir + '/' + actual_data
        pi_mkdir(destination_folder)
        ftp.cwd(cronos_dir + '/' + actual_data)
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
        send2cloud()
        print("Actual Cronos data is uploaded in cloud!\n")
        shutil.rmtree(destination_dir + '/pcmcia')        
    ftp.quit()   
    
    
get_actual_cronos_data(cronos_dir,CRONOS_IP,user,pw)
sys.exit()





    

