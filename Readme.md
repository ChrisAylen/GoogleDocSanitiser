# Google Docs Anonymizer

Google Docs Anonymizer is a Python application that processes all Google Docs files in a specified Google Drive folder, anonymizes personally identifiable information (PII) using Natural Language Processing, and stores the anonymized files in a separate folder.

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


## Configuration

1. Save your Google API credentials in a `google-client.json` file in the project directory.
2. Update the `config.json` file with your input and output folder IDs from Google Drive.

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
