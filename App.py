import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import re

# --- APP CONFIG ---
st.set_page_config(page_title="AWT Sporting Code Master", layout="wide")
st.title("🏆 AWT Official Analysis: Full Event Batch")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # 30-minute chunks are the "Sweet Spot" for detail vs speed
    chunk_size = st.slider("Analysis Window (Minutes)", 15, 60, 30)
    official_data = st.text_area("AWT Official Results (Reference)", height=150)

# --- REPAIRED UTILITY: STRENGTHENED PARSER ---
def parse_ai_table(text):
    # Matches lines with at least 5 pipes
    raw_lines = [l.strip() for l in text.split('\n') if l.count('|') > 5]
    if not raw_lines: return []
    
    # Filter out markdown separators
    data_lines = [l for l in raw_lines if not re.match(r'^[|\s\-:]+$', l)]
    if not data_lines: return []
    
    headers = [h.strip() for h in data_lines[0].split('|') if h.strip()]
    
    rows = []
    for line in data_lines[1:]:
        values = [v.strip() for v in line.split('|') if v.strip()]
        if len(values) >= len(headers):
            rows.append(dict(zip(headers, values[:len(headers)])))
    return rows

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    col1, col2 = st.columns([3, 1])
    with col1:
        event_url = st.text_input("YouTube URL")
    with col2:
        vid_hours = st.number_input("Video Length (Hours)", min_value=0.5, value=3.0)

    if event_url and st.button("🚀 Run Full Competition Analysis"):
        all_data = []
        total_mins = int(vid_hours * 60)
        progress_bar = st.progress(0)
        table_placeholder = st.empty()
        
        # WE LOOP IN CHUNKS TO ENSURE EVERY PILOT IS SEEN
        for start_m in range(0, total_mins, chunk_size):
            end_m = start_m + chunk_size
            st.write(f"🔍 Judging Segment: {start_m}m to {end_m}m...")
            
            try:
                prompt = f"""
                Watch ONLY the segment from {start_m}:00 to {end_m}:00.
                You are a WTFF Judge. Foundation: Sporting Code Section 7.
                Identify EVERY pilot run in this {chunk_size}-minute window.

                1. PILOT: Read name from bottom-left graphic.
                2. SCORING (9.0 - 15.5 Scale):
                   - Technicity (T): K-factor sum.
                   - Execution (E) & Artistry (A): 0-10.
                   - Bonus (B): Connections/Twisted.
                   - AI_Final: T + ((E+A)/2) normalized.

                Reference: {official_data}

                OUTPUT ONLY THE MARKDOWN TABLE.
                Cols: Pilot | Start | End | Maneuvers | Technicity | Exec | Art | Bonus | AI_Final | AWT_Official
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                )

                chunk_rows = parse_ai_table(response.text)
                if chunk_rows:
                    all_data.extend(chunk_rows)
                    # Update the live table display
                    table_placeholder.table(pd.DataFrame(all_data))
                
                progress_bar.progress(min(end_m / total_mins, 1.0))
                time.sleep(12) # Quota protection

            except Exception as e:
                st.error(f"Error at {start_m}m: {e}")
                continue

        if all_data:
            st.success("Full Event Analysis Complete!")
            final_df = pd.DataFrame(all_data)
            st.download_button("Download Full CSV", final_df.to_csv(index=False).encode('utf-8'), "AWT_Full_Event.csv")
