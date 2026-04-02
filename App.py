import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import re

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF 2026 Official Engine", layout="wide")
st.title("🛡️ WTFF Sporting Code: Top-3 Technicity & Scorer")

with st.sidebar:
    st.header("1. Organizer Overrides")
    st.info("Correct an AI misidentification to force a Technicity recalculation.")
    manual_pilot = st.text_input("Pilot Name (to override)")
    manual_tricks = st.text_area("Correct Maneuver List (e.g., Misty, Heli, SAT)")
    
    st.header("2. Logic Constraints")
    st.write("✅ **Technicity:** Average of TOP 3 K-factors.")
    st.write("✅ **Math:** (Technicity * (Technical/10)) + Choreo + Landing + Bonus")

# --- MAIN INTERFACE ---
api_key = st.text_input("Enter Gemini API Key", type="password")
event_url = st.text_input("Paste YouTube Event URL Here") # RESTORED URL INPUT

if api_key and event_url:
    client = genai.Client(api_key=api_key)
    
    if st.button("🚀 Run Full WTFF Analysis"):
        with st.spinner("Analyzing maneuvers & calculating Top 3 Average..."):
            try:
                # THE "WTFF TRUTH" PROMPT
                prompt = f"""
                WATCH THIS VIDEO. ACT AS A WTFF JUDGE. 
                STRICT COMPLIANCE WITH WTFF SPORTING CODE SECTION 7.

                1. IDENTIFY: Every maneuver performed by every pilot.
                2. SYNC: Cross-reference acroworldtour.com for this specific event's official maneuver list.
                3. CALCULATE TECHNICITY: Find the K-factors for ALL moves. Identify the TOP 3. Calculate their AVERAGE.
                4. CALCULATE TECHNICAL: Score execution 0-10.
                5. THE MATH PROBLEM: (Technicity_Avg * (Technical_Score/10)) + Choreo + Landing + Bonus.
                6. PILOT FEEDBACK: List specific faults for every trick (e.g., 'Asymmetric exit', 'Low energy').

                OVERRIDE DATA (IF ANY): {manual_pilot}: {manual_tricks}

                OUTPUT FORMAT (Markdown Table):
                Pilot | Top 3 K-Factors | Technicity (Avg) | Technical (E) | Choreo (C) | Landing (L) | Bonus (B) | AI_Final | Pilot Feedback (Faults)
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                )

                # Robust Data Parser
                lines = [l.strip() for l in response.text.split('\n') if l.count('|') > 7]
                if lines:
                    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                    data_rows = [l for l in lines[1:] if not re.match(r'^[|\s\-:]+$', l)]
                    
                    table_data = []
                    for row in data_rows:
                        vals = [v.strip() for v in row.split('|') if v.strip()]
                        if len(vals) == len(headers):
                            table_data.append(dict(zip(headers, vals)))
                    
                    df = pd.DataFrame(table_data)
                    st.table(df)
                    st.download_button("📥 Export WTFF Results", df.to_csv(index=False).encode('utf-8'), "WTFF_Analysis.csv")
                else:
                    st.error("Protocol Error: AI output failed to generate table. Raw response below:")
                    st.code(response.text)

            except Exception as e:
                st.error(f"System Error: {e}")
else:
    st.info("Please enter your API Key and a YouTube URL to begin.")
