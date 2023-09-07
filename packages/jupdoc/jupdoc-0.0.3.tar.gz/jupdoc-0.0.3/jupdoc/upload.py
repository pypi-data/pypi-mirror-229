import os
import logging, coloredlogs
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

def upload_file(file_name, 
                folder_id, 
                local_path='.',
                mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                creds_path='client_secrets.json'):
    """
    description:
        Uploads a file to Google Drive if it doesn't already exist, else updates the existing file.
    args:
        file_name: name of the file to be uploaded
        folder_id: ID of the folder to upload the file to
        mime_type: MIME type of the file
    output:
        None
    """

    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    local_file_path = os.path.join(local_path, file_name)
    existing_file_id = None

    results = drive_service.files().list(
        q=f"parents='{folder_id}' and name='{file_name}'"
    ).execute()

    files = results.get('files', [])
    if files:
        logging.info(f'File "{file_name}" already exists in Google Drive, updating it...')
        existing_file_id = files[0]['id']

    media = MediaFileUpload(local_file_path, mimetype=mime_type)

    if existing_file_id:
        drive_service.files().update(
            fileId=existing_file_id,
            media_body=media
        ).execute()
        logging.info(f'File "{file_name}" updated in Google Drive with ID: {existing_file_id}')
    
    else:
        logging.info(f'File "{file_name}" does not exist in Google Drive, uploading it...')
        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
        }
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
        ).execute()
        logging.info(f'File "{file_name}" uploaded to Google Drive with ID: {uploaded_file["id"]}')


if __name__ == "__main__":
    file_name = "config_model.docx"
    folder_id = '1Qlw7SxdPr4Ag1mKl4-cTrjgJPgZyzzYb'
    local_path = './docs_test'
    upload_file(file_name, folder_id, local_path)