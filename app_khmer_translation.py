import streamlit as st
from googletrans import Translator
from gtts import gTTS
import urllib.parse
import os

# Set up the page
st.set_page_config(page_title="English to Khmer Tool", page_icon="🇰🇭")
st.title("--- 🇰🇭 English to Khmer Tool ---")

# Initialize the translator
@st.cache_resource
def get_translator():
    return Translator()

translator = get_translator()

# 1. UI Elements - Text Input
en_text = st.text_input("English:", value="Where can I find good food?")

# Create a layout for our buttons
col1, col2 = st.columns([1, 1])

# Generate the Google Translate URL for the backup button
query = urllib.parse.quote(en_text)
google_url = f"https://translate.google.com/?sl=en&tl=km&text={query}&op=translate"

# 2. Backup Button (Streamlit handles external links natively)
with col2:
    st.link_button("🌐 Open in Google Translate", url=google_url)

# 3. Translation Function & Button
with col1:
    if st.button("🔊 Translate & Play", type="primary"):
        if not en_text.strip():
            st.warning("Please enter some text to translate.")
        else:
            with st.spinner("Translating..."):
                try:
                    # Translate text
                    res = translator.translate(en_text, src='en', dest='km')

                    # Robust phonetic check
                    phonetic = res.pronunciation
                    if not phonetic:
                        try:
                            phonetic = res.extra_data['translation'][1][3]
                        except:
                            phonetic = "Click 'Open in Google Translate' to see phonetics!"

                    # Display results
                    st.success("Translation Complete!")
                    st.write(f"🇰🇭 **Khmer:** {res.text}")
                    st.write(f"🗣️ **Phonetic:** {phonetic}")

                    # Generate and play audio
                    audio_file = "final_audio.mp3"
                    tts = gTTS(text=res.text, lang='km')
                    tts.save(audio_file)
                    
                    # Streamlit's native audio player with autoplay
                    st.audio(audio_file, format="audio/mp3", autoplay=True)

                except Exception as e:
                    st.error(f"Connection error. Try the Google Translate button! Error: {e}")