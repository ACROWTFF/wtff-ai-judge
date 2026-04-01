import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Chunk Processor", layout="wide")
st.title("🏆 WTFF Event Archive: Multi-Heat Processor")

with st.sidebar:
    st.header("Control Panel")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.warning("Free Tier: Processing in 30-min chunks is recommended to avoid Quota Errors.")

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
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        # --- CHUNK SELECTION ---
        st.subheader("Select Heat Window")
        col1, col2 = st.columns(2)
        start_min = col1.number_input("Start Minute", min_value=0, value=0)
        end_min = col2.number_input("End Minute", min_value=1, value=30)

        if st.button(f"🔍 Analyze Minutes {start_min} to {end_min}"):
            with st.spinner(f"Analyzing segment..."):
                try:
                    # We tell the AI exactly which window to look at to save 'Tokens'
                    prompt = f"""
                    Focus ONLY on the video segment from {start_min}:00 to {end_min}:00.
                    1. Identify every pilot run in this specific window.
                    2. Provide: Pilot Name, Exact Timestamp, Maneuvers, and WTFF Score (0-100).
                    
                    RETURN ONLY A MARKDOWN TABLE: 
                    Pilot | Timestamp | Maneuvers | WTFF_Score
                    """

                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/webm"),
                            prompt
                        ]
                    )

                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download This Chunk (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name=f"WTFF_Minutes_{start_min}_to_{end_min}.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    if "429" in str(e):
                        st.error("Quota Exceeded. Please wait 60 seconds before trying the next chunk.")
                    else:
                        st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key.")
