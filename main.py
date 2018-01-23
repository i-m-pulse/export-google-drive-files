from gdrive import gdrive
from config import Config

#Instantiate an object
foo = gdrive(Config)

## Authenticating

# Get inital code to access token
code = foo.getCode()
#Access the access_token and refresh_token
foo.writeToken(code)

# Get fileid for your file
src_filename = 'your Google Drive filename Google Spreadsheet'
file_id = foo.getFileId(src_filename)

# Download the file to your local folder
dst_filename = 'test.csv'
dst_mimetype = 'text/csv'
foo.downloadFile(file_id, dst_mimetype, dst_filename)
