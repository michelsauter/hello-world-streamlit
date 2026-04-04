import streamlit as st
from googletrans import Translator
from gtts import gTTS
import pandas as pd
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Khmer Weighted Learner", page_icon="🇰🇭")
st.title("🇰🇭 Khmer Vocabulary Trainer")

# Initialize Translator
@st.cache_resource
def get_translator():
    return Translator()

translator = get_translator()

# --- INITIAL DATA & STATE ---
if 'word_data' not in st.session_state:
    # Starting list of phrases
    initial_phrases = [
        "Hello", 
        "Thank you", 
        "Where is the bathroom?", 
        "I am hungry", 
        "How much does this cost?"
    ]
    # CRITICAL FIX: Initialize with all keys present from the start
    st.session_state.word_data = [
        {
            "en": phrase, 
            "translation": "", 
            "phonetic": "", # Ensure this key exists immediately
            "weight": 1, 
            "count": 0
        } 
        for phrase in initial_phrases
    ]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- HELPER FUNCTIONS ---
def adjust_weight(increase=True):
    idx = st.session_state.current_idx
    st.session_state.word_data[idx]['count'] += 1
    
    if increase:
        st.session_state.word_data[idx]['weight'] += 1
    else:
        st.session_state.word_data[idx]['weight'] = max(1, st.session_state.word_data[idx]['weight'] - 1)
    
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.word_data)

# --- UI LOGIC ---
current_word = st.session_state.word_data[st.session_state.current_idx]

st.subheader(f"Phrase {st.session_state.current_idx + 1} of {len(st.session_state.word_data)}")
st.info(f"Translate this: **{current_word['en']}**")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔊 Translate & Play", type="primary", use_container_width=True):
        with st.spinner("Fetching translation..."):
            try:
                res = translator.translate(current_word['en'], src='en', dest='km')
                
                # Extract Phonetics
                phonetic_text = res.pronunciation if res.pronunciation else ""
                if not phonetic_text:
                    try:
                        phonetic_text = res.extra_data['translation'][1][3]
                    except:
                        phonetic_text = "Phonetic N/A"

                # Update Session State
                st.session_state.word_data[st.session_state.current_idx]['translation'] = res.text
                st.session_state.word_data[st.session_state.current_idx]['phonetic'] = phonetic_text
                
                st.success(f"**Khmer:** {res.text}")
                st.caption(f"**Pronunciation:** {phonetic_text}")

                audio_file = "temp_audio.mp3"
                tts = gTTS(text=res.text, lang='km')
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    encoded_query = current_word['en'].replace(" ", "%20")
    google_url = f"https://translate.google.com/?sl=en&tl=km&text={encoded_query}&op=translate"
    st.link_button("🌐 View on Google Translate", url=google_url, use_container_width=True)

st.divider()

# --- FEEDBACK BUTTONS ---
st.write("Do you know this phrase?")
f_col1, f_col2 = st.columns(2)

with f_col1:
    if st.button("✅ I know this", use_container_width=True):
        adjust_weight(increase=False)
        st.rerun()

with f_col2:
    if st.button("❌ Need more practice", use_container_width=True):
        adjust_weight(increase=True)
        st.rerun()

# --- PROGRESS TRACKER ---
st.write("### 📊 Your Learning Progress")

# Create DataFrame
df = pd.DataFrame(st.session_state.word_data)

# Since we initialized correctly, these keys are guaranteed to exist
columns_order = ['en', 'translation', 'phonetic', 'weight', 'count']
df_display = df[columns_order].copy()

# Rename for UI
df_display.columns = ['English', 'Khmer', 'Phonetic', 'Weight', 'Times Shown']

st.dataframe(
    df_display.sort_values(by="Weight", ascending=False), 
    use_container_width=True, 
    hide_index=True
)

if st.sidebar.button("Reset Progress"):
    st.session_state.clear()
    st.rerun()