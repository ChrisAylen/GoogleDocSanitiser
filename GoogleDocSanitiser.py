from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from spacy.matcher import Matcher
import os
import json
import spacy
import pickle
import re
import uuid

# UK Phone number regex
pattern = r"\+44\s?7\d{3,4}\s?\d{6}|0\d{10}|0\d{4}\s\d{6}"
matcher = re.compile(pattern)


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']

def read_structured_document(document):
    content = ""
    for element in document['body']['content']:
        if 'paragraph' in element:
            for text_run in element['paragraph']['elements']:
                if 'textRun' in text_run:
                    content += text_run['textRun']['content']
    return content

import uuid

def anonymize_content(content):
    nlp = spacy.load('en_core_web_lg')
    matcher = Matcher(nlp.vocab)
    # pattern to match email addresses
    pattern = [{"LIKE_EMAIL": True}]
    matcher.add("EMAIL", [pattern])
    # pattern to match URLs
    pattern = [{"LIKE_URL": True}]
    matcher.add("URL", [pattern])

    # Anonymize phone numbers first
    content, phone_anonymization_dict = anonymize_phone_numbers(content)

    doc = nlp(content)
    anonymized_text = content

    anonymization_dict = {}

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:
            if ent.text not in anonymization_dict:
                anonymization_dict[ent.text] = f"{ent.label_}_{uuid.uuid4()}"
            anonymized_text = anonymized_text.replace(ent.text, anonymization_dict[ent.text])
    
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if span.text not in anonymization_dict:
            anonymization_dict[span.text] = f'{string_id}_{uuid.uuid4()}'
        anonymized_text = anonymized_text.replace(span.text, anonymization_dict[span.text])

    anonymization_dict.update(phone_anonymization_dict)

    return anonymized_text, anonymization_dict



def get_folder_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items

def process_all_files_in_folder(docs_service, drive_service, sheets_service,  folder_id, output_folder_id):
    files = get_folder_files(drive_service, folder_id)
    for file in files:
        # Check if the file is a Google Document
        if file.get('mimeType') == 'application/vnd.google-apps.document':
            print(f'Processing file: {file.get("name")}')
            # Read the document
            document = docs_service.documents().get(documentId=file.get('id')).execute()
            content = read_structured_document(document)
            # Anonymize the content
            anonymized_content, anonymization_dict = anonymize_content(content)
            # Create a new document with the anonymized content
            new_file_title = f"Anonymized - {file.get('name')}"
            new_file = create_google_document(docs_service, drive_service, new_file_title, anonymized_content, output_folder_id)
            print(f'Created anonymized file: {new_file.get("name")}')
             # Create a new Google Sheet with the anonymization dictionary
            dict_file_name = f"{new_file_title} - Dictionary"
            create_anonymization_sheet(sheets_service, drive_service, dict_file_name, anonymization_dict, output_folder_id)

def create_google_document(docs_service, drive_service, name, content, folder_id):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]  # specify the folder ID here
    }
    file = drive_service.files().create(body=file_metadata).execute()
    document_id = file.get('id')
    
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': content
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()

    return file

def create_anonymization_sheet(sheets_service, drive_service, name, anonymization_dict, folder_id):
    # Create a new Google Sheet file
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata).execute()

    # Get the ID of the new Google Sheet
    spreadsheet_id = file.get('id')

    # Prepare the values to be inserted into the Google Sheet
    values = [["Text", "Anonymized Text"]] + list(anonymization_dict.items())

    # Create the body for the batchUpdate request
    body = {
        'values': values
    }

    # Insert the values into the Google Sheet
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body).execute()
    
    print(f'Created anonymization dictionary file: {file.get("name")}')
    return file


def anonymize_phone_numbers(text):
    pattern = r"\+44\s?7\d{1,4}(\s?\d{1,3}){1,3}|0\s?\d{4}(\s?\d{1,3}){1,3}"
    matcher = re.compile(pattern)

    anonymization_dict = {}
    for match in matcher.finditer(text):
        phone_number = match.group(0)
        if phone_number not in anonymization_dict:
            anonymization_dict[phone_number] = f"[PHONE_{uuid.uuid4()}]"
        text = text.replace(phone_number, anonymization_dict[phone_number])

    return text, anonymization_dict


def main():

    with open('config.json') as f:
        config = json.load(f)
    
    creds = None
    if os.path.exists('token.pickle') and os.path.getsize('token.pickle') > 0:
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google-client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    folder_id = config['input_folder_id']  # replace with your actual folder ID
    output_folder_id = config['output_folder_id']  # ID of the folder to store anonymized documents
    
    process_all_files_in_folder(docs_service, drive_service, sheets_service, folder_id, output_folder_id)

if __name__ == '__main__':
    main()
