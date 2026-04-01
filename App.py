import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF Sporting Code Judge", layout="wide")
st.title("🏆 WTFF / AWT 2026: Sporting Code Foundation")

with st.sidebar:
    st.header("API & Grounding")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # Grounding info is now used ONLY to verify names/AWT results, not to build the math.
    official_data = st.text_area("AWT Official Results (Reference)", height=150)

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste YouTube Event URL")

    if event_url:
        if st.button("🚀 Run Sporting Code Analysis"):
            with st.spinner("Applying WTFF Section 6 Math..."):
                try:
                    # THE SPORTING CODE PROMPT: This is the 'Foundation'
                    prompt = f"""
                    You are an official AWT Judge. The WTFF Sporting Code is your absolute foundation.
                    
                    TASK: Analyze the video and calculate scores using the AWT 2026 Regulation.
                    
                    1. PILOT: Read the name from the bottom-left graphic.
                    
                    2. CALCULATION PROTOCOL (9.0 - 15.5 SCALE):
                       - TECHNICITY (T): Identify each maneuver (e.g. Misty, Infinity, SAT) and apply its 2026 K-factor.
                       - EXECUTION (E): Start at 10.0. Deduct for slack, collapses, or axis errors.
                       - ARTISTIC (A): Start at 10.0. Score for flow, rhythm, and box placement.
                       - FINAL MATH: Apply the Sporting Code formula: T + ((E + A) / 2) adjusted to the AWT competition scale.
                    
                    3. MANEUVER VALIDATION: Use ONLY official WTFF nomenclature. 
                       (Twisted MacTwist, Joker, Esferis, etc.)

                    REFERENCE DATA FOR NAME MATCHING ONLY: {official_data}

                    RETURN ONLY A MARKDOWN TABLE:
                    Pilot | Start | End | Maneuvers | Technicity | Exec | Art | AI_FINAL | AWT_OFFICIAL
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"),
                            prompt
                        ]
                    )

                    # Simple table parsing logic
                    lines = [l.strip() for l in response.text.split('\n') if '|' in l and '---' not in l]
                    if len(lines) > 1:
                        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                        rows = [[v.strip() for v in l.split('|') if v.strip()] for l in lines[1:]]
                        df = pd.DataFrame(rows, columns=headers)
                        st.table(df)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download Final AWT Results", csv, "AWT_SportingCode_Report.csv")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")
