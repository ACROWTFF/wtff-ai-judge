import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Paid Pro", layout="wide")
st.title("🏆 WTFF Full Event Analyzer")

with st.sidebar:
    st.header("Status: PAID TIER")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.success("High-Capacity Mode Enabled")

# --- PARSING LOGIC ---
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

# --- MAIN APP ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste YouTube URL (Full Archive)")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Analyze Full Video Now"):
            with st.spinner("Processing full stream. This may take 2-4 minutes..."):
                try:
                    # PROMPT: Optimized for 2.5 Flash's long-context logic
                    prompt = """
                    Watch this entire paragliding competition. 
                    - Scan the full duration for every individual pilot run.
                    - Identify pilots by on-screen graphics or commentator names.
                    - Generate a table: Pilot | Start | End | Maneuvers | WTFF_Score.
                    - Respond ONLY with the table.
                    """

                    # Using 2.5 Flash for the best speed/token-limit balance
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/mp4"),
                            prompt
                        ]
                    )

                    st.subheader("Event Summary")
                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button("📥 Download Master CSV", df.to_csv(index=False).encode('utf-8'), "WTFF_Master.csv")

                except Exception as e:
                    if "429" in str(e):
                        st.error("Even on Paid Tier 1, a 3-hour video is slightly too large for one 'instant' request.")
                        st.info("Try the 'Batch Mode' code I gave you previously—it's the only way to bypass Google's Tier 1 pipe limits.")
                    else:
                        st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key.")
