import streamlit as st
from google import genai
from google.genai import types
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Stable Pro", layout="wide")
st.title("🏆 WTFF Event Archive: Pro Analysis")

with st.sidebar:
    st.header("Billing Status: ACTIVE")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # This model is the 2026 production workhorse
    st.success("Model: Gemini 2.5 Pro (Stable)")

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
        
        if st.button("🚀 Run Analysis"):
            with st.spinner("Analyzing video... This can take up to 3 minutes for long streams."):
                try:
                    # PROMPT: Specific instructions to avoid drone-racing hallucinations
                    prompt = """
                    Watch this paragliding competition archive. 
                    1. Focus ONLY on the paragliding runs. 
                    2. Identify the ACTUAL pilot names from the video graphics or commentator.
                    3. Create a table: Pilot | Start | End | Maneuvers | WTFF_Score.
                    
                    Return ONLY the markdown table.
                    """

                    # FIXED: Using the production 2.5 Pro model and correct FileData structure
                    response = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=[
                            types.Part.from_uri(
                                file_uri=event_url,
                                mime_type="video/mp4"
                            ),
                            types.Part.from_text(text=prompt)
                        ]
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
                    if "404" in str(e):
                        st.info("Note: Ensure your API key is from a region where Gemini 2.5 is available (US/EU).")
else:
    st.warning("Please enter your API Key.")
