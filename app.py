import streamlit as st
from streamlit_oauth import OAuth2Component
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 1. Configuration (Set these in Streamlit Secrets!)
CLIENT_ID = st.secrets["AUTH"]["CLIENT_ID"]
CLIENT_SECRET = st.secrets["AUTH"]["CLIENT_SECRET"]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Use the URL where your app is hosted
REDIRECT_URI = "https://hello-world-app-htf3pcrkd598aic2zm8ewj.streamlit.app/" # Change to your Streamlit Cloud URL for deployment

st.title("📝 Save Text to Your Google Drive")

# 2. Setup OAuth Component
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, "")

if "auth" not in st.session_state:
    # Show Login Button
    result = oauth2.authorize_button(
        name="Login with Google",
        scope="https://www.googleapis.com/auth/drive.file",
        redirect_uri=REDIRECT_URI,
    )
    if result:
        st.session_state.auth = result
        st.rerun()
else:
    # User is Logged In
    st.success("Logged in successfully!")
    
    # 3. User Interface
    user_text = st.text_area("Enter text to save to your Drive:", "Hello from Streamlit!")
    file_name = st.text_input("File Name:", "my_text_file.txt")

    if st.button("🚀 Save to My Drive"):
        try:
            # Build the Drive service using the user's token
            token = st.session_state.auth['token']['access_token']
            from google.oauth2.credentials import Credentials
            creds = Credentials(token)
            service = build('drive', 'v3', credentials=creds)

            # Prepare the file content
            file_metadata = {'name': file_name}
            media = MediaIoBaseUpload(io.BytesIO(user_text.encode()), mimetype='text/plain')

            # Upload to Drive
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            st.balloons()
            st.success(f"File saved! File ID: {file.get('id')}")
            
        except Exception as e:
            st.error(f"Error saving to Drive: {e}")

    if st.button("Logout"):
        del st.session_state.auth
        st.rerun()