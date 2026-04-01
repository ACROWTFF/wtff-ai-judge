import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge Pro", layout="wide")
st.title("🏆 WTFF Event Archive: Full Analysis")

with st.sidebar:
    st.header("Billing Status: ACTIVE")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # Updated to the 2026 Production Stable model
    st.success("System: Gemini 2.5 Pro")

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
    # Use default settings - the SDK handles versioning automatically
    client = genai.Client(api_key=api_key)
    
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Run Full Event Analysis"):
            with st.spinner("Analyzing..."):
                try:
                    # SIMPLIFIED PROMPT: We include the URL directly in the contents
                    # Gemini 2.5 Pro is native-multimodal and "fetches" the URL context
                    prompt = f"""
                    Watch this YouTube video: {event_url}
                    
                    1. Identify every individual pilot run.
                    2. Provide a table with: Pilot | Start_Time | End_Time | Maneuvers | WTFF_Score
                    
                    Return ONLY the markdown table.
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=prompt
                    )

                    st.markdown(response.text)
                    
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name="WTFF_Event_Report.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.info("Check if the YouTube video is Public or Unlisted (Private videos won't work).")
else:
    st.warning("Please enter your API Key.")
