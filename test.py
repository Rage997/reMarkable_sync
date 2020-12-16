from RMClient import RMClient

client = RMClient('./')
client.renew_token()
client.clean()
client.copy_to_pc()