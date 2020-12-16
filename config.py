api_base = "https://my.remarkable.com/token/json/2/device/new"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoMC11c2VyaWQiOiJhdXRoMHw1ZTA5ZTc4NjU3N2FmOTBlY2E4YWZmMjIiLCJkZXZpY2UtZGVzYyI6ImRlc2t0b3AtbWFjb3MiLCJkZXZpY2UtaWQiOiI3MDFjMzc1Mi0xMDI1LTQ3NzAtYWY0My01ZGRjZmE0ZGFiYjIiLCJpYXQiOjE1ODIyMDU4NjIsImlzcyI6InJNIFdlYkFwcCIsImp0aSI6ImNrMHRtOGFBN0NnPSIsIm5iZiI6MTU4MjIwNTg2Miwic3ViIjoick0gRGV2aWNlIFRva2VuIn0.dDScCFTPpY5G9dVCHWnWiqCoSCpZpr5hdsubzW68D_g"

import os
import json

def get_config_path() -> str:
    '''Returns the location of the configuration file'''
    
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_path =  os.path.join(config_dir, 'config_remarkable.rm')
    print('Configuration path: ', config_path)
    return config_path

def load_config() -> dict:
    '''Load a configuration file'''
    
    config_path = get_config_path()
    with open(config_path, 'r') as file:
        data =  json.loads(file.read())

    return data    


def write_config(config: dict) -> None:
    '''Writes a configuration file
    
    Args:
        config: a dictionary containing the configuration data
    ''' 

    config_path = get_config_path()
    data = json.dumps(config)
   
    with open(config_path, 'w') as file:
        file.write(data)

