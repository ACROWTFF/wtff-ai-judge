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
    # Using Gemini 3 Flash - the 2026 standard for high-speed video processing
    st.success("System: Gemini 3 Flash (Production)")

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
    # Initialize the client with the modern SDK defaults
    client = genai.Client(api_key=api_key)
    
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Run Full Event Analysis"):
            with st.spinner("Gemini 3 is watching the video..."):
                try:
                    # PROMPT DESIGN: Explicitly requesting video-grounded analysis
                    # We use the new simplified 'contents' list format
                    response = client.models.generate_content(
                        model='gemini-3-flash',
                        contents=[
                            types.Part.from_uri(
                                file_uri=event_url,
                                mime_type="video/mp4" # Using mp4 as the universal video descriptor
                            ),
                            "Watch this video. Provide a markdown table of all pilot runs: Pilot | Start | End | Maneuvers | WTFF_Score."
                        ]
                    )

                    # Display the text response
                    st.markdown(response.text)
                    
                    # Process the CSV
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name="WTFF_Event_Report.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    # Specific help for the 400 error
                    if "400" in str(e):
                        st.error("API Protocol Error: The YouTube link format was rejected.")
                        st.info("Try using the 'Short' link (youtu.be) or ensure the video is not Age Restricted.")
                    else:
                        st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter your API Key.")
