import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import re

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Archive Master", layout="wide")
st.title("🏆 WTFF Event Archive & Batch Scoring")

with st.sidebar:
    st.header("Control Panel")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("System: WTFF 2026 Batch Processor (YouTube Direct)")

# --- UTILITY: PARSE AI TABLE TO DATAFRAME ---
def parse_ai_table(text):
    """Simple parser to turn AI markdown tables into a downloadable format"""
    lines = [line.strip() for line in text.split('\n') if '|' in line and '---' not in line]
    if len(lines) < 2:
        return None
    
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
    event_url = st.text_input("Paste YouTube Event URL (e.g., paragliding.live stream)")

    if event_url:
        st.video(event_url) # Show the video in the app
        
        if st.button("🔍 Run Full Event Analysis"):
            with st.spinner("AI is analyzing the video. This takes ~30-60 seconds..."):
                try:
                    # PROMPT: Instructs the AI to be a judge
                    prompt = """
                    Watch this paragliding competition video. 
                    1. Identify every individual pilot run.
                    2. For each run, provide: Pilot Name, Start/End Timestamps, and Maneuvers.
                    3. Score each run (0-100) based on WTFF 2026 technical standards.
                    
                    RETURN ONLY A MARKDOWN TABLE with these columns: 
                    Pilot | Start | End | Maneuvers | WTFF_Score
                    """

                    # Calling the model with the YouTube URL directly
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[
                            types.Part.from_uri(
                                file_uri=event_url,
                                mime_type="video/webm" # Standard for YT processing
                            ),
                            prompt
                        ]
                    )

                    # Display Analysis
                    st.subheader("Final AI Judgment")
                    st.markdown(response.text)

                    # Create CSV Download
                    df = parse_ai_table(response.text)
                    if df is not None:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="WTFF_Event_Results.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter your API Key to start judging.")
