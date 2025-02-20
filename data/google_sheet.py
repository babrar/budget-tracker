import os
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Get the spreadsheet ID and range from environment variables
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = os.getenv('RANGE_NAME')

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDENTIALS_FILE = "credentials/credentials.json"
TOKEN_FILE = "token.json"


def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())
    return creds


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = authorize()
    return creds


def read_sheet():
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    values = result.get("values", [])

    if not values:
        return pd.DataFrame()
    else:
        # Warning: headers cannot have whitespace. Trim and rename.
        header = values[0]
        data = values[1:]
        return pd.DataFrame(data, columns=header)
