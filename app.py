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
    initial_phrases = ["Hello", "Thank you", "Where is the bathroom?", "I am hungry", "The bill, please"]
    st.session_state.word_data = [
        {"en": p, "translation": "", "phonetic": "", "weight": 1, "count": 0} 
        for p in initial_phrases
    ]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

def adjust_weight(increase=True):
    idx = st.session_state.current_idx
    st.session_state.word_data[idx]['count'] += 1
    if increase:
        st.session_state.word_data[idx]['weight'] += 1
    else:
        st.session_state.word_data[idx]['weight'] = max(1, st.session_state.word_data[idx]['weight'] - 1)
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.word_data)

# --- UI ---
current_word = st.session_state.word_data[st.session_state.current_idx]
st.subheader(f"Phrase {st.session_state.current_idx + 1} of {len(st.session_state.word_data)}")
st.info(f"English: **{current_word['en']}**")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔊 Translate & Play", type="primary", use_container_width=True):
        with st.spinner("Processing..."):
            try:
                res = translator.translate(current_word['en'], src='en', dest='km')
                khmer_text = res.text
                
                # --- PHONETIC EXTRACTION FIX ---
                # Attempt 1: Google Pronunciation
                phonetic = res.pronunciation if res.pronunciation else ""
                
                # Attempt 2: Dig into extra_data (the nested internal response)
                if not phonetic:
                    try:
                        # Indexing into Google's raw response structure for transliteration
                        phonetic = res.extra_data['translation'][1][3]
                    except:
                        phonetic = None
                
                # Attempt 3: If still NA, mark as "Listen to Audio" 
                # (Khmer transliteration is complex; audio is the source of truth)
                if not phonetic or phonetic == khmer_text:
                    phonetic = "🔊 Use Audio for Pronunciation"

                st.session_state.word_data[st.session_state.current_idx]['translation'] = khmer_text
                st.session_state.word_data[st.session_state.current_idx]['phonetic'] = phonetic
                
                st.success(f"Khmer: {khmer_text}")
                st.write(f"Phonetic: *{phonetic}*")

                # Audio Generation
                tts = gTTS(text=khmer_text, lang='km')
                tts.save("speech.mp3")
                st.audio("speech.mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    q = current_word['en'].replace(" ", "%20")
    st.link_button("🌐 Google Translate", url=f"https://translate.google.com/?sl=en&tl=km&text={q}&op=translate")

st.divider()

# Feedback
f_col1, f_col2 = st.columns(2)
with f_col1:
    if st.button("✅ I know this", use_container_width=True):
        adjust_weight(False)
        st.rerun()
with f_col2:
    if st.button("❌ Need practice", use_container_width=True):
        adjust_weight(True)
        st.rerun()

# --- TABLE ---
st.write("### 📊 Learning Progress")
df = pd.DataFrame(st.session_state.word_data)
df.columns = ['English', 'Khmer', 'Phonetic', 'Weight', 'Shows']
st.dataframe(df.sort_values("Weight", ascending=False), use_container_width=True, hide_index=True)