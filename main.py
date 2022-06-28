def retrieve_all_folders(api_ref):
    """
    Return a dictionary with all folders IDs mapped to their parent folder IDs. 
    Basically flatten the entire folder structure.
    """
    folders_dict = {}
    page_token = None
    max_allowed_page_size = 1000
    query = "trashed = false and mimeType = 'application/vnd.google-apps.folder'"

    # As long as the API indicates that there is a next page...
    while True:
        # https://developers.google.com/drive/api/v3/reference/files/list
        results = api_ref.files().list(
            pageSize=max_allowed_page_size,
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
