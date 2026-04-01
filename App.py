import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Pro v1.5", layout="wide")
st.title("🏆 WTFF Event Archive: Full Video Analysis")

with st.sidebar:
    st.header("Billing Status: PAID")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.success("Using Gemini 1.5 Pro - High Capacity Mode")

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
    # Initialize the client
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Run Full Archive Analysis"):
            with st.spinner("Gemini 1.5 Pro is analyzing the full stream. This may take 2-3 minutes..."):
                try:
                    prompt = """
                    Watch this entire paragliding competition archive. 
                    1. Identify every pilot's competition run.
                    2. For each run, extract: 
                       - Pilot Name
                       - Start and End Timestamps
                       - List of maneuvers performed
                       - WTFF 2026 Technical Score (0-100)
                    
                    RETURN ONLY A MARKDOWN TABLE: 
                    Pilot | Start_Time | End_Time | Maneuvers | WTFF_Score
                    """

                    # UPDATED MODEL: gemini-1.5-pro-latest
                    response = client.models.generate_content(
                        model='gemini-1.5-pro-latest',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/webm"),
                            prompt
                        ]
                    )

                    st.subheader("Event Leaderboard & Log")
                    st.markdown(response.text)
                    
                    # CSV Generation
                    df = parse_ai_table(response.text)
                    if df is not None:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv,
                            file_name="WTFF_Event_Results.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.info("Tip: If the video is over 4 hours, try analyzing in 2-hour segments.")
else:
    st.warning("Please enter your API Key.")
