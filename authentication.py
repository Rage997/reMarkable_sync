from uuid import uuid4

api_base = "https://my.remarkable.com/token/json/2/device/new"

def authenticate(self):
    '''
    Authenticate with the remarkable cloud and write the 
    token key in a configuration file inside the working directory
    '''        

    auth_code = 'ukcqshzd' #one-time authentication code

    payload = {
        "code": auth_code,
        "deviceDesc": "desktop-macos",
        "deviceID": str(uuid4())
    }
    '''
    - code is the authentication code generated at https://my.remarkable.com/connect/remarkable
    - deviceDesc is a brief desription of the device
    -  deviceID is a Universally unique identifier(https://en.wikipedia.org/wiki/Universally_unique_identifier)
    '''
    r = requests.post(api_base, data=json.dumps(payload))

    # print(r.status_code, r.text, r.headers)

    if r.status_code == 200:
        self.token = r.text
    else:
        r.raise_for_status()

    # Write the token key to the configuration file
    
    configuration = {
        'token': self.token
    }
    
    from config import write_config

    write_config(configuration)
    
def renew_token(self):
    '''Before using the token, it needs to be renewed'''
    header = {'Authorization': 'Bearer ' + str(self.token)}
    r = requests.post(
                    'https://my.remarkable.com/token/json/2/user/new',
                        headers=header)

    print(r.status_code, r.text, r.headers)