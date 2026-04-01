import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge Pro", layout="wide")
st.title("🏆 WTFF Event Archive: Pro Analysis")

with st.sidebar:
    st.header("Billing Status: ACTIVE")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.success("System: Gemini 2.5 Pro (Standard Tier)")

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
    # We initialize with the production 'v1' version
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1")
    )
    
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Analyze Full Event"):
            with st.spinner("Gemini 2.5 Pro is processing the video..."):
                try:
                    prompt = """
                    Watch this entire paragliding competition video.
                    Identify every individual pilot run and provide a table with:
                    Pilot | Start_Time | End_Time | Maneuvers | WTFF_Score (0-100)
                    
                    Respond ONLY with the markdown table.
                    """

                    # UPDATED MODEL ID for 2026 Stable
                    response = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/webm"),
                            prompt
                        ]
                    )

                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download Full Results (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name="WTFF_Event_Report.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter your API Key.")
