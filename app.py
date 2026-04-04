import streamlit as st
from googletrans import Translator
from gtts import gTTS
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
    # Added 'translation' and 'count' keys to the dictionary
    st.session_state.word_data = [
        {"en": "Hello", "translation": "", "weight": 1, "count": 0},
        {"en": "Thank you", "translation": "", "weight": 1, "count": 0},
        {"en": "Where is the bathroom?", "translation": "", "weight": 1, "count": 0},
        {"en": "I am hungry", "translation": "", "weight": 1, "count": 0},
        {"en": "The bill, please", "translation": "", "weight": 1, "count": 0},
    ]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- HELPER FUNCTIONS ---
def adjust_weight(increase=True):
    idx = st.session_state.current_idx
    # Increment the "shown" count when the user provides feedback
    st.session_state.word_data[idx]['count'] += 1
    
    if increase:
        st.session_state.word_data[idx]['weight'] += 1
    else:
        st.session_state.word_data[idx]['weight'] = max(1, st.session_state.word_data[idx]['weight'] - 1)
    
    # Move to next word
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.word_data)

# --- UI LOGIC ---
current_word = st.session_state.word_data[st.session_state.current_idx]

st.subheader(f"Word {st.session_state.current_idx + 1} of {len(st.session_state.word_data)}")
st.info(f"Current English Phrase: **{current_word['en']}**")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔊 Translate & Play", type="primary", use_container_width=True):
        with st.spinner("Translating..."):
            try:
                # Translate
                res = translator.translate(current_word['en'], src='en', dest='km')
                
                # Save translation to state so it appears in the table later
                st.session_state.word_data[st.session_state.current_idx]['translation'] = res.text
                
                # Get Phonetics
                phonetic = res.pronunciation if res.pronunciation else "Check Google Translate"
                
                # Display
                st.write(f"🇰🇭 **Khmer:** {res.text}")
                st.write(f"🗣️ **Phonetic:** {phonetic}")

                # Audio
                audio_file = "temp_audio.mp3"
                tts = gTTS(text=res.text, lang='km')
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Translation Error: {e}")

with col2:
    encoded_query = current_word['en'].replace(" ", "%20")
    google_url = f"https://translate.google.com/?sl=en&tl=km&text={encoded_query}&op=translate"
    st.link_button("🌐 Google Translate", url=google_url, use_container_width=True)

st.divider()

# --- FEEDBACK BUTTONS ---
st.write("How well do you know this?")
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
st.subheader("Learning Progress")
# We display the translation only if it has been fetched at least once
sorted_data = sorted(st.session_state.word_data, key=lambda x: x['weight'], reverse=True)

# Formatting the table for better readability
st.table(sorted_data)