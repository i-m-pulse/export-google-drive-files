# export-google-drive-files
Python script to access Google files and export them to your preferred location 

## Overview
This script helps in authenticating Google Drive access without user intervention, suitable for Web/Mobile Apps. It allows for files to be exported to your preferred location by accessing the Google Drive APIs 

## Installation 

1. Install a virtual environment of your choice

2. Execute pip install -r requirements.txt

3. Authorize requests with OAuth 2.0 for Mobile & Desktop Apps
Go to https://developers.google.com/identity/protocols/OAuth2InstalledApp and follow the Prerequisites

4. Update the config.py file with the Client ID, Secret and Scope for Google Drive

5. For the next step to obtain OAuth 2.0 access tokens, follow:
    - For Step 1-4 in https://developers.google.com/identity/protocols/OAuth2InstalledApp - Use getCode() method
    - For Step 5 - Use writeToken() method
    - For Refreshing a token after expiry - Use refreshToken()

6. To export, edit main.py with your filename of your google file, new filetype and new filename.

Feel free to submit changes.

Cheers!
Shraddha

