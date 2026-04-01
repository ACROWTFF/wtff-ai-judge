import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- APP CONFIG ---
st.set_page_config(page_title="AWT Sporting Code Master", layout="wide")
st.title("🏆 AWT Official Analysis")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    official_data = st.text_area("AWT Official Results (For Name Matching)", height=150)

# --- REPAIRED UTILITY: STRENGTHENED PARSER ---
def parse_ai_table(text):
    import re
    # Find all lines that look like table rows (contain multiple pipes)
    raw_lines = [l.strip() for l in text.split('\n') if l.count('|') > 4]
    if not raw_lines:
        return []
    
    # Filter out header separators (e.g., |---|---|)
    data_lines = [l for l in raw_lines if not re.match(r'^[|\s\-:]+$', l)]
    
    # Extract headers from the first valid-looking line
    headers = [h.strip() for h in data_lines[0].split('|') if h.strip()]
    
    rows = []
    for line in data_lines[1:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        # If the AI hallucinated extra columns or missed some, we pad/trim to match headers
        if len(values) >= len(headers):
            rows.append(dict(zip(headers, values[:len(headers)])))
    return rows

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("YouTube URL")

    if event_url and st.button("🚀 Execute Analysis"):
        with st.spinner("Processing..."):
            try:
                # REFINED PROMPT: Extreme focus on the Table format
                prompt = f"""
                Watch this video and act as a WTFF Judge. 
                Foundation: WTFF Sporting Code Section 7.
                Scale: 9.0 - 15.5.
                
                Calculate: 
                1. Technicity (T): K-factor sum.
                2. Execution (E): 0-10.
                3. Artistry (A): 0-10.
                4. Bonus (B): Twisted/Connection adds.
                5. AI_Final: T + ((E+A)/2) normalized to AWT scale.

                Reference Scores: {official_data}

                OUTPUT ONLY THE MARKDOWN TABLE. NO PROSE. NO EXPLANATIONS.
                Table Columns: Pilot | Start | End | Maneuvers | Technicity | Exec | Art | Bonus | AI_Final | AWT_Official
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                )

                # Use the new robust parser
                data = parse_ai_table(response.text)
                
                if data:
                    df = pd.DataFrame(data)
                    st.table(df)
                    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "AWT_Results.csv")
                else:
                    st.error("AI returned data but the table parser failed. Raw output below:")
                    st.code(response.text)

            except Exception as e:
                st.error(f"Error: {e}")
