from __future__ import print_function

import os.path
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If you change scope or credentials the token.json file must be deleted before running the script
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Replace with the ID of the folder that will be the root for the search for the files
ROOT_FOLDER_TO_SEARCH = '<ID>'

MAX_PARENTS = 500

MAX_PAGE_SIZE = 1000

def retrieve_all_folders():
    """
    Return a dictionary with all folders IDs mapped to their parent folder IDs. 
    Basically flatten the entire folder structure.
    """
    folders_dict = {}
    page_token = None
    query = "trashed = false and mimeType = 'application/vnd.google-apps.folder'"

    # As long as the API indicates that there is a next page with folders...
    while True:
        # https://developers.google.com/drive/api/v3/reference/files/list
        results = api_ref.files().list(
            pageSize=MAX_PAGE_SIZE,
            fields="nextPageToken, files(id, name, mimeType, parents)",
            includeItemsFromAllDrives=True, supportsAllDrives=True,
            pageToken=page_token,
            q=query).execute()

        folders = results.get('files', [])

        page_token = results.get('nextPageToken', None)

        for folder in folders:
            # Here the script ignores the folders that are in the root of your Google Drive
            if 'parents' in folder:
                folders_dict[folder['id']] = folder['parents'][0]

        if page_token is None:
            break

    return folders_dict


def retrieve_subfolders(target_root_folder, folders_dict):
    """
    Yield recursively subfolders of the target root folder.
    :param folders_dict: The dictionary returned by `retrieve_all_folders`.
    """
    aux_folders_list = [key for key, value in folders_dict.items() if value == root_target_folder]
    for sub_folder in aux_folders_list:  # For each subfolder...
        yield sub_folder
        yield from retrieve_subfolders(sub_folder, folders_dict)


def get_files_in_folders(filter):
    """
    Return a dictionary with all files IDs mapped to their filenames.
    """
    folder_files_dict = {}
    page_token = None
    query_files = f"mimeType != 'application/vnd.google-apps.folder' and trashed = false and ({filter})"

    # As long as the API indicates that there is a next page with files...
    while True:
        results = api_ref.files().list(
            pageSize=MAX_PAGE_SIZE,
            fields="nextPageToken, files(id, name, mimeType, parents)",
            includeItemsFromAllDrives=True, supportsAllDrives=True,
            pageToken=page_token,
            q=query_files).execute()

        files = results.get('files', [])

        page_token = results.get('nextPageToken', None)

        for file in files:
            folder_files_dict[file['id']] = file['name']

        if page_token is None:
            break

    return folder_files_dict


def retrieve_files_in_folders(selected_folders):
    """
    Get files under a tree of folders.
    """
    files = {}
    chunk_of_folders = [selected_folders[i:i + MAX_PARENTS] for i in range(0, len(selected_folders), MAX_PARENTS)]
    for folder_list in chunk_of_folders:
        filter = ' in parents or '.join('"{0}"'.format(f) for f in folder_list) + ' in parents'
        files.update(get_files_in_folders(filter))
    return files


if __name__ == "__main__":
    creds = None

    """
    The file token.json stores the user's access and refresh tokens, and is created 
    automatically when the authorization flow completes for the first time.
    """
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        api_ref = build('drive', 'v3', credentials=creds)

        print(f'Querying all folders: {datetime.now()}')
        
        all_folders_dict = retrieve_all_folders()

        a_file = open("folders.json", "w", encoding='utf-8')
        json.dump(all_folders_dict, a_file, ensure_ascii=False)

        print(f'Total of folders: {len(all_folders_dict)}')

        print(f'Retrieving folders of interest: {datetime.now()}')

        relevant_folders_list = [ROOT_FOLDER_TO_SEARCH]

        for folder in retrieve_subfolders(ROOT_FOLDER_TO_SEARCH, all_folders_dict):
           relevant_folders_list.append(folder)

        print(f'Total of folders of interest: {len(relevant_folders_list)}')

        print(f'Retrieving files from selected folders: {datetime.now()}')

        all_files_dict = retrieve_files_in_folders(relevant_folders_list)

        print(f'Total of files: {len(all_files_dict)}')

        b_file = open("files.json", "w", encoding='utf-8')
        json.dump(all_files_dict, b_file, ensure_ascii=False)

        print(f'Finishing the job: {datetime.now()}')

    except HttpError as error:
        print(f'An error occurred: {error}')
