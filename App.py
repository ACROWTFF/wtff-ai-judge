import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="AWT Sporting Code Master", layout="wide")
st.title("🏆 AWT Official Analysis: Sporting Code Engine")
st.markdown("### RESTORED: Technicity (T) + Bonus (B) + Execution (E) Logic")

with st.sidebar:
    st.header("1. API & Quota")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Analysis Chunk (Minutes)", 15, 60, 45)
    
    st.header("2. AWT Grounding")
    st.info("Reference data from acroworldtour.com (Pilot | Official Score)")
    official_data = st.text_area("AWT Official Results", height=150)

# --- UTILITY: PARSE AI TABLE ---
def parse_ai_table(text):
    lines = [line.strip() for line in text.split('\n') if '|' in line and '---' not in line]
    if len(lines) < 2: return []
    data = []
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    for line in lines[1:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        if len(values) == len(headers):
            data.append(dict(zip(headers, values)))
    return data

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste YouTube Event URL")
    vid_hours = st.number_input("Video Length (Hours)", min_value=0.5, value=3.0)

    if event_url:
        if st.button("🚀 Execute Restoration Analysis"):
            all_rows = []
            total_mins = int(vid_hours * 60)
            progress_bar = st.progress(0)
            table_placeholder = st.empty()

            for start_m in range(0, total_mins, chunk_size):
                end_m = start_m + chunk_size
                
                # THE FOUNDATION PROMPT (Section 7 Protocol)
                prompt = f"""
                Watch the segment from {start_m}:00 to {end_m}:00.
                You are a Lead AWT Judge. Apply the official Sporting Code Section 7 formula.

                1. PILOT: Identify via bottom-left graphic. Cross-ref: {official_data}
                
                2. SCORING ENGINE (AWT 2026):
                   - TECHNICITY (T): Sum the K-factors of all maneuvers performed. 
                   - EXECUTION (E): Score 0-10. Deduct for line slack, collapses, and axis deviation.
                   - ARTISTRY/CHOREO (A): Score 0-10. Focus on box placement and variety.
                   - BONUS (B): Apply bonuses for twisted exits, complex connections, or innovative moves.
                
                3. FINAL CALCULATION: 
                   Use the raw Sporting Code summation. Final results must reflect the official AWT 9.0 - 15.5 scale.
                   If the math results in a higher/lower number, apply the competition normalization factor.

                RETURN ONLY A MARKDOWN TABLE:
                Pilot | Start | End | Maneuvers | Technicity (T) | Exec (E) | Art (A) | Bonus (B) | AI_Final | AWT_Official
                """

                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                    )

                    chunk_rows = parse_ai_table(response.text)
                    all_rows.extend(chunk_rows)
                    if all_rows:
                        table_placeholder.table(pd.DataFrame(all_rows).tail(10))

                    progress_bar.progress(min(end_m / total_mins, 1.0))
                    time.sleep(12)

                except Exception as e:
                    st.error(f"Error at {start_m}m: {e}")
                    break

            if all_rows:
                st.success("Analysis Restored and Complete!")
                df = pd.DataFrame(all_rows)
                st.download_button("📥 Download Master Report", df.to_csv(index=False).encode('utf-8'), "AWT_Master_Report.csv")
