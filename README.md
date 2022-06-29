# python-google-drive-api

Python script to recursively list all files from a target folder in Google Drive.

Install dependencies:

```shell
$ pip install -r requirements.txt
```

To run the script, you need to enable access to the Google Drive API and download the access credentials.

Access this [link](https://console.cloud.google.com/apis/dashboard) and authenticate with the desired account.

Google will give you the option to download in a JSON file. 

After that, move the file to the project folder and rename it to **credentials.json**.

Another important point: it's necessary to provide the ID of a folder that will be used as a starting point to recover the files.

This ID must be placed in the variable **ROOT_FOLDER_TO_SEARCH**.

Run the script:

```shell
$ python main.py
```

At the end of the execution, the script will create a file with the list of all folders and another file with the list of all files.
