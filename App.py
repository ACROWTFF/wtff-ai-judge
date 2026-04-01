import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge 2026", layout="wide")
st.title("🏆 WTFF Event Archive: 3.1 Flash Analysis")

with st.sidebar:
    st.header("Billing: ENABLED")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # Updated to the new 3.1 series
    st.success("Model: Gemini 3.1 Flash (Latest)")

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

if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Run Analysis"):
            with st.spinner("Gemini 3.1 is processing video frames..."):
                try:
                    # PROMPT: We add a 'Strict Grounding' instruction to stop hallucinations
                    prompt = """
                    VIDEO ANALYSIS TASK:
                    1. Watch this paragliding competition video.
                    2. IGNORE any pre-existing knowledge of drone racing.
                    3. Identify the ACTUAL paragliding pilots shown on screen (check jerseys, graphics, or commentator mentions).
                    4. Create a table: Pilot | Start_Time | End_Time | Maneuvers | WTFF_Score
                    
                    Return ONLY the markdown table. If you cannot see a pilot name, write 'Unknown'.
                    """

                    response = client.models.generate_content(
                        model='gemini-3.1-flash-preview', # THE FIXED MODEL ID
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
                        st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "WTFF_Results.csv")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key.")
