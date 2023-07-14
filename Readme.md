# Google Docs Anonymizer

Google Docs Anonymizer is a Python application that processes all Google Docs files in a specified Google Drive folder, anonymizes personally identifiable information (PII) using Natural Language Processing, and stores the anonymized files in a separate folder.

This process is not 100% effective!  You should check the results brfor relying on the output!

In addition, this code will create a correspoding Google Sheet for each document showing what was sanitsed and provide data to reverse the process should this be needed.  A use case for this might be sending some data for external analysis and de-obfuscating when the results are received back.

## Getting Started

### Prerequisites

- Python 3.7+
- Google API Python Client
- google-auth-httplib2
- google-auth-oauthlib
- google-auth
- spacy
- re

### Installing

To install the prerequisites, run:

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib google-auth spacy

#### Google Cloud Platform Configuration
Before running the script, you need to create a project on Google Cloud Platform (GCP), enable necessary APIs for the project, and generate OAuth 2.0 credentials.

#### Create a Google Cloud Project
- Visit the Google Cloud Console at https://console.cloud.google.com/.
If you have not created a project before, you might only see a button that says "Create Project". If you have created projects before, select the project dropdown and then click on "New Project".
- Enter a project name and optionally edit the Project ID (you will need this later if you choose to enable APIs using the CLI).
- Click "Create".
#### Enable the Google Docs and Drive API
- In the Google Cloud Console, select your project.
- Navigate to the "Library" page using the left-side menu navigation.
- In the "Library", search for "Google Docs API" and click on it. On the API page, click "Enable". Do the same for "Google Drive API".
- Repeat the process for "Google Sheets API".
#### Create OAuth 2.0 Credentials
- Navigate to the "Credentials" page using the left-side menu navigation.
- Click "Create Credentials" and select "OAuth client ID".
- If you have not configured the OAuth consent screen before, you will be asked to do so. On the OAuth consent screen, only the "Application name" is required, and you can enter a name of your choice. Save the settings.
- On the "Create OAuth client ID" page, select "Desktop app" for the Application type, and create a name.
- Click "Create". Your Client ID and Client Secret will be displayed. Click "OK".
- On the Credentials page, you will see the OAuth 2.0 Client IDs you just created. On the right side of the row, click the download icon to download your credentials in a JSON file.
- Update Configuration
- Rename the downloaded JSON file to google-client.json and place it in the project directory.

These steps will get you set up with a GCP project and the necessary API credentials.

Please note, this process is likely to change from time to time!

## Configuration

1. Save your Google API credentials in a `google-client.json` file in the project directory.
2. Rename the `config_example.json` to `config.json`
3. Update the `config.json` file with your input and output folder IDs from Google Drive.

## Usage

Run the script using Python:

python3 GoogleDocSanitise.py


## How It Works

1. The script scans all files in the specified input folder on Google Drive.
2. For each Google Docs file in the folder, the script retrieves the file and reads its content.
3. The script uses spaCy's Named Entity Recognition (NER) to identify and replace PII.
4. The script creates a new Google Docs file with the anonymized content in the specified output folder.

## Limitations

This script is intended to work with English language documents and may not accurately recognize and anonymize PII in other languages.

## License

This project is licensed under the MIT License - see the LICENSE file for details
