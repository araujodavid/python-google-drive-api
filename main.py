
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
