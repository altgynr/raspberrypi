from azure.storage.blob import BlockBlobService

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

block_blob_service, blob_container = get_content_achim()
blobContent = block_blob_service.list_blobs(blob_container)
blobFiles = []
for content in blobContent:
    blobFiles.append(content.name)
    
print(blobFiles)