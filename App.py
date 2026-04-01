import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge Pro", layout="wide")
st.title("🏆 WTFF Event Archive: Pro Analysis")

with st.sidebar:
    st.header("Billing: ACTIVE")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # Using 2.5 Flash - The stable 2026 production model
    st.success("Model: Gemini 2.5 Flash")

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
    # We initialize the client without version overrides for maximum stability
    client = genai.Client(api_key=api_key)
    
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Run Full Event Analysis"):
            with st.spinner("Analyzing full stream..."):
                try:
                    # PROMPT: Explicit grounding instructions
                    prompt = """
                    Watch this paragliding competition video.
                    1. Identify every pilot run shown.
                    2. Extract: Pilot Name, Start/End Timestamps, Maneuvers, and WTFF Score (0-100).
                    3. Stay strictly grounded to the video frames (no drone racing hallucinations).
                    
                    Return ONLY a markdown table.
                    """

                    # FIXED: Sending URL and Prompt as a simple list of parts
                    # This avoids the 'fileData' JSON error
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_uri(
                                file_uri=event_url,
                                mime_type="video/mp4"
                            ),
                            prompt
                        ]
                    )

                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name="WTFF_Event_Results.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter your API Key.")
