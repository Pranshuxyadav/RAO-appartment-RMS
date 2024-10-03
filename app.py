from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with your actual secret key

# Step 1: Set the path to your OAuth credentials file and define the Google Drive scopes
CLIENT_SECRETS_FILE = r'api\client_secret_136430012746-ps6moqo0t3g7bfnqaun81c0vdmsr9unq.apps.googleusercontent.com.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Define the relative path for the callback route (use relative path for Flask routes)
REDIRECT_URI = '/callback'

# Step 2: OAuth flow initialization
@app.route('/')
def index():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

# Step 3: OAuth callback to retrieve credentials
@app.route(REDIRECT_URI)
def callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('callback', _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('otp_login'))

# Step 4: Function to load data from Google Drive
def load_data_from_drive(file_id):
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)

    # Download the file from Google Drive
    request = drive_service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    file_io.seek(0)
    df = pd.read_excel(file_io)
    return df

# Step 5: OTP verification route
@app.route('/otp', methods=['GET'])
def otp_login():
    otp = request.args.get('otp')
    print(f"Received OTP: {otp}")
    
    if otp:
        # Use Google Drive file ID for the room_data.xlsx
        file_id = '1cH_bH3ev1xEc9LJFJbbzd73E6acStnMB'
        df = load_data_from_drive(file_id)
        
        if df is None:
            return "Error: Data file not found.", 500

        df['OTP'] = df['OTP'].astype(str).str.lower().str.strip()
        otp = otp.lower().strip()
        
        print(f"OTP column from DataFrame: {df['OTP'].tolist()}")

        tenant_data = df[df['OTP'] == otp]

        if not tenant_data.empty:
            tenant = tenant_data.iloc[0].to_dict()
            return render_template('room_data.html', tenant=tenant, room_no=tenant['Room No.'])
        else:
            return "Invalid OTP. Please try again.", 400
    return "OTP is required", 400

# Step 6: Utility function to store credentials in session
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
