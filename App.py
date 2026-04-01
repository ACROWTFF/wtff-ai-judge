import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Pro Edition", layout="wide")
st.title("🏆 WTFF Event Archive: Full Video Analysis")

with st.sidebar:
    st.header("Billing Status: PAID")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.success("Pay-as-you-go enabled: Full video processing active.")

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
    event_url = st.text_input("Paste YouTube Event URL (e.g., Grandvillard, Acro Game, etc.)")

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Analyze Entire Event (All Pilots)"):
            with st.spinner("Gemini is watching the full event. This can take 1-2 minutes for long streams..."):
                try:
                    # PROMPT: Now we ask for EVERYTHING
                    prompt = """
                    Watch this entire paragliding event video. 
                    1. Create a comprehensive log of every pilot run shown.
                    2. For each run, identify: 
                       - Pilot Name (listen to commentator/check graphics)
                       - Timestamp (Start to End of the run)
                       - Maneuvers performed
                       - Technical Score (0-100) based on WTFF 2026 standards
                    
                    RETURN ONLY A MARKDOWN TABLE: 
                    Pilot | Start_Time | End_Time | Maneuvers | WTFF_Score
                    """

                    # Using the direct YouTube URI
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/webm"),
                            prompt
                        ]
                    )

                    st.subheader("Complete Event Results")
                    st.markdown(response.text)
                    
                    # Create the Master CSV
                    df = parse_ai_table(response.text)
                    if df is not None:
                        st.download_button(
                            label="📥 Download Full Event Results (CSV)",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name="WTFF_Full_Event_Results.csv",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter your API Key to unlock pro features.")
