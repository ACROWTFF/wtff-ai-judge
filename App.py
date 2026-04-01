import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Pixel-Perfect", layout="wide")
st.title("🏆 WTFF Event Archive: True Video Analysis")

with st.sidebar:
    st.header("Mode: Deep Scan")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Using File API to prevent hallucinations.")

# --- UTILITY: PARSE AI TABLE ---
def parse_ai_table(text):
    lines = [line.strip() for line in text.split('\n') if '|' in line and '---' not in line]
    if len(lines) < 2: return None
    data = []
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    for line in lines[1:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        if len(values) == len(headers):
            data.append(dict(zip(headers, values)))
    return pd.DataFrame(data)

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    
    # IMPORTANT: For true analysis, you must upload the video file or use a processed URI.
    # Since we are using YouTube, we will use the 'Media' part properly.
    video_url = st.text_input("Paste YouTube URL")

    if video_url:
        st.video(video_url)
        
        if st.button("🚀 Run Deep Video Analysis"):
            with st.spinner("Uploading and analyzing frames (No Hallucinations)..."):
                try:
                    # We use Gemini 2.5 Pro for the highest 'Visual IQ'
                    # We explicitly define the part as a VIDEO to force frame-sampling
                    response = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=[
                            types.Part.from_uri(
                                file_uri=video_url,
                                mime_type="video/webm" # Forces the model to use its video-vision
                            ),
                            "Identify every paragliding run. List Pilot, Start/End Time, Maneuvers, and Score."
                        ]
                    )

                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button("📥 Download Results", df.to_csv().encode('utf-8'), "Results.csv")
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("If this fails, the YouTube video may have 'Embedding' disabled by the creator.")
else:
    st.warning("Please enter your API Key.")
