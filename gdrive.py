
from config import Config

import requests
import json
import csv
import sys
import os

class gdrive:
    def __init__(self, config):
        """
        Config: Contains GDrive & S3 authentication details
        """
        #S3 Credentials
        self.config = config
        self.s3_client_id = config.S3_CLIENT_ID
        self.s3_client_secret = config.S3_CLIENT_SECRET
        self.s3_host = config.S3_HOST
        
        #Google Drive Credentials
        self.drive_client_id = config.DRIVE_CLIENT_ID
        self.drive_client_secret = config.DRIVE_CLIENT_SECRET
        self.drive_redirect_uri = config.DRIVE_REDIRECT_URI
        self.drive_token_file = 'auth-token.json'
        
        #Drive Urls
        self.scope = 'https://www.googleapis.com/auth/drive'
        self.google_account_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.drive_auth_url = 'https://www.googleapis.com/oauth2/v4/token'
        self.drive_base_url = 'https://www.googleapis.com/drive/v3'
        self.list_url = '/files'
        
    # Google Authentication Steps: https://developers.google.com/identity/protocols/OAuth2InstalledApp
    
    def getCode(self):
        parameters = {
                'client_id' : self.drive_client_id,
                'redirect_uri' : self.drive_redirect_uri,
                'response_type': 'code',
                'scope' : self.scope,
                }
        r = requests.post(self.google_account_url, params=parameters)
        print("Please go to the following link to get access code:")
        print(r.url)
        code = input("Enter the access code here:")
        return code
    
    def writeToken(self, code):
        parameters = {
                'code' : code,
                'client_id' : self.drive_client_id,
                'client_secret' : self.drive_client_secret,
                'redirect_uri' : self.drive_redirect_uri,
                'grant_type' : 'authorization_code'
                }
        headers = {'content-type':'application/x-www-form-urlencoded'}
        r = requests.post(self.drive_auth_url, data=parameters, headers=headers) 
        r_json = json.loads(r.text)
        token = r_json.get('access_token')
        with open(self.drive_token_file, "w+", encoding="utf-8") as write_f:
            print("Writing access token to file "+ self.drive_token_file)
            write_f.write(token)
        self.drive_refresh_token = r_json.get('refresh_token')
        return
                
    def checkToken(self):
        """
        Checks for the token file, if not available, fetches it and writes it to the file
        """
        try:
            token_f = open(self.drive_token_file, 'r+')
        except FileNotFoundError:
            self.refreshToken()
        else:
            token = token_f.read()
            if not token:
                self.refreshToken()
        return
        
    def refreshToken(self):
        """
        Refreshes the authentication token using refresh token, when the last token expires
        """
        parameters = {
                'client_id' : self.drive_client_id,
                'client_secret' : self.drive_client_secret,
                'refresh_token' : self.drive_refresh_token,
                'grant_type' : 'refresh_token'
                }
        headers = {'content-type':'application/x-www-form-urlencoded'}
        r = requests.post(self.drive_auth_url, data=parameters, headers=headers)
        r_json = json.loads(r.text)
        token = r_json.get('access_token')
        with open(self.drive_token_file, "w+", encoding="utf-8") as write_f:
            print("Writing access token to file "+ self.drive_token_file)
            write_f.write(token)
            return
        
    def getFileId(self, filename):   
        """
        Given a filename, send a GET request to the Files LIST API to list the file metadata.
        API reference: https://developers.google.com/drive/v3/reference/files/list
        Args:
            filename (str): Name of the Google Spreadsheet file whose fileid is needed
        Returns:
            Str: Google FileId
        """
        self.checkToken()
        with open(self.drive_token_file, 'r') as token_f:
            token = token_f.read()
        parameters = {
                'access_token' : token,
                'q': "name = " + "\'" + filename + "\'",
                }
        response = requests.get(self.drive_base_url + self.list_url, params = parameters)

        if response.status_code == 401: 
            #re-authenticating
            new_access_token = self.refreshToken()
            self.drive_access_token = new_access_token
            parameters['access_token'] = self.drive_access_token
            response = requests.get(self.drive_base_url + self.list_url, params = parameters)        
        try:
            response_json = json.loads(response.text)
            file_id = response_json.get('files')[0].get('id')
            print("File ID for file %s is %s" %(filename, file_id))
            return file_id
        except:
            e = sys.exc_info()[0]
            print("Unexpected error: " + e)
            return response
    
    def downloadFile(self, file_id, mimetype, filename):
        """
        Given a fileId, mimetype, send a GET request to the Files Export API to get all
        the file content and dump it in the filename provided.
        API reference: https://developers.google.com/drive/v3/reference/files/export
        
        Args:
            file_id (str): Google FileId of the file to be exported
            mimetype (str): Type of the exported file
            filename (str): Name of the downloaded file
        Returns:
            None
        """
        self.checkToken()
        with open(self.drive_token_file, 'r') as token_f:
            token = token_f.read()
        parameters = {
                'access_token' : token,
                'mimeType': mimetype
                }        
        #Exporting the data from the GDrive file
        response = requests.get(self.drive_base_url + self.list_url + '/' + file_id + '/export/', params = parameters)        
        if response.status_code == 401 or response.status_code == 400:
            #Re-authenticating
            new_access_token = self.refreshToken()
            self.drive_access_token = new_access_token
            parameters['access_token'] = self.drive_access_token
            response = requests.get(self.drive_base_url + self.list_url + '/' + file_id + '/export/', params = parameters)        
        try:
            data = response.text
        except:
            e = sys.exc_info()[0]
            print("Unexpected error: " + e)
            return        
        #Writing data into a CSV
        reader = csv.reader(data.splitlines())
        with open(filename,'w', newline='') as outfile:
            writer = csv.writer(outfile)
            print("Writing file %s to current folder" %filename)
            writer.writerows(reader)
            return
        



        
    

