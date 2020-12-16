import requests 
import json
import zipfile
from uuid import uuid4
import os
from config import get_config_path, write_config, load_config
from utils import delete_directory
from config import write_config

'''
The remarkable api is splitted into multiple endpoints: AUTH_API, SERVICE_DISCOVERY_API, STORAGE_API
Ref: https://github.com/splitbrain/ReMarkableAPI/wiki
'''

AUTH_API = "https://my.remarkable.com/token/json/2/device/new"
SERVICE_DISCOVERY_API = 'https://service-manager-production-dot-remarkable-production.appspot.com'
STORAGE_API = 'https://document-storage-production-dot-remarkable-production.appspot.com'

class RMClient():

    def __init__(self, directory='/home'):
        
        self.init_docs_folder(directory)

        if not os.path.exists(get_config_path()):
            self.authenticate()

        self.token = load_config()['token']

    def init_docs_folder(self, directory):
        if not os.path.exists(directory):
            raise FileNotFoundError        
        
        self.root = os.path.join(directory, 'RM_docs')
        try:
            os.mkdir(self.root)
        except FileExistsError:
            # there's already a local copy of the remarkable cloud
            pass

    def authenticate(self, auth_code):
        '''
        Authenticate with the remarkable cloud and write the 
        token key in a configuration file inside the working directory
        '''
        # TODO this code changes each time
        # THis code has been moved to authentication.py (?)
        # Do something like this: if first use, ask for it in the terminal
        auth_code = 'mmrkbahp' #one-time verification code

        payload = {
            "code": auth_code,
            "deviceDesc": "desktop-macos",
            "deviceID": str(uuid4())
        }
        '''
        - "code" is the authentication code generated at https://my.remarkable.com/connect/remarkable
        - "deviceDesc" is a brief desription of the device
        -  "deviceID" is a Universally unique identifier(https://en.wikipedia.org/wiki/Universally_unique_identifier)
        '''
        r = requests.post(AUTH_API, data=json.dumps(payload))

        # print(r.status_code, r.text, r.headers)

        if r.status_code == 200:
            self.token = r.text
        else:
            r.raise_for_status()

        # Write the token key to the configuration file
        configuration = {
            'token': self.token
        }
        write_config(configuration) #writes configuration json
        
    def renew_token(self):
        '''Renews a token to authorization'''
        header = {'Authorization': 'Bearer ' + str(self.token)}
        r = requests.post(
                        'https://my.remarkable.com/token/json/2/user/new',
                         headers=header)
        self.tmp_token = r.text

    def get_docs_raw(self) -> []:
        '''Get the documents in the remarkable cloud as an array of json'''
        # TODO find out why is not returning all the documents
        base_url = 'https://document-storage-production-dot-remarkable-production.appspot.com/document-storage/json/2/docs'
        header = {'Authorization': 'Bearer ' + str(self.tmp_token), 'user-agent': 'desktop-macos'}
        params = {'withBlob': True}
        r = requests.get(base_url, headers=header, params=params)
        documents_raw = json.loads(r.text)
        return documents_raw

    def get_download_link_doc(self, doc_id) -> str:
        '''Gets the download link of a single document'''
        base_url = 'https://document-storage-production-dot-remarkable-production.appspot.com/document-storage/json/2/docs'
        header = {'Authorization': 'Bearer ' + str(self.tmp_token), 'user-agent': 'desktop-macos'}
        params = {'withBlob': True, 'doc': doc_id}
        r = requests.get(base_url, headers=header, params=params)
        return json.loads(r.text)

    def get_path(self, doc):
        '''
        Returns the path to a file or directory in the remarkable cloud
        If a file is inside the trash bin it returns None
        '''
        path = ''
        while doc['Parent']: # gather the paths along the route to the root  
            if doc['Parent'] == 'trash':
                return None 
            doc_parent = self.search_doc_by_id(doc['Parent'], self.raw_documents)
            path = os.path.join(doc_parent['VissibleName'], path)
            doc = doc_parent
        return path

    def copy_to_pc(self):
        '''
        Copies all the documents from the remarakble cloud into the the root directory
        '''
        self.raw_documents = self.get_docs_raw()
        for doc in self.raw_documents:
            name = doc['VissibleName']
            file_path = self.get_path(doc)
            if file_path:
                dir_path = os.path.join(self.root, file_path)
            else:
                # TODO Not a good code flow: workaround for files in the trash bin
                break
            if doc['Type'] == 'CollectionType':
                path = os.path.join(dir_path, name)
            elif doc['Type'] == 'DocumentType':
                # If the document is a file create the filesystem and download the file
                path = dir_path
            if not os.path.isdir(path): #if the directory already exist do not create it
                os.makedirs(path)
            
            # If the document is a file, then download it
            if doc['Type'] == 'DocumentType':
                download_link = doc['BlobURLGet']
                if not download_link:
                    # Try to query a new download link
                    doc_id = doc['ID']
                    download_link = self.get_download_link_doc(doc_id)
                self.download_document(download_link, os.path.join(path, name))

    def download_document(self, url, dest) -> None:
        '''
        Downloads a document from the remarkable cloud.
        The response is a zip file containing 
        args
            url: the download link
            dest: the destination where to download the file 
        '''

        header = {'Authorization': 'Bearer ' + str(self.tmp_token), 'user-agent': 'desktop-macos'}
         
        r = requests.get(url, headers=header, stream=True)        
        print(r)
        with open(dest, 'wb') as f:
            for chucnk in r.iter_content(chunk_size=256):
                f.write(chucnk)

        dir = os.path.split(dest)[0]
        #unzip file
        with zipfile.ZipFile(dest, 'r') as zip_file:
            zip_file.extractall(path=os.path.join(dir, 
                os.path.split(dest)[1] + '1') )
        
        os.remove(dest)  # remove the zip
        # Organise files 
        # I dont know the id....
        # os.replace(dest, os.path.join(dir, url))
        # TODO find out how to combine the informationa bout the file and get pdf with annotations

    def search_doc_by_id(self, doc_ID, raw_documents):
        '''Helper function to search a document by ID in the response json from remarkable cloud'''
        for doc in raw_documents:
            if doc['ID'] == doc_ID:
                return doc
        return None

    def create_file_system(self) -> json:
        '''
        Create a json which links local files in the machine to the remarkable cloud
        '''
        # Is this really useful? maybe store for each file name its id
        return {}

    def sync_docs(self):
        '''
        Syncs the documents on my machine with the remarkable cloud
        '''
        # TODO extrapolate information about the last time a document has been modified
        
        # os.path.getmtime('pathtofile')
        
        # with os.scandir() as dir_entries:
        #     for entry in dir_entries:
        #         print(os.path.getmtime(entry))
        #         info = entry.stat()
        #         print(info) 
        0
    
    def clean(self):
        delete_directory(self.root)
        
