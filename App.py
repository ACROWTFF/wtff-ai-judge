import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="AWT 2026 Pro Analyzer", layout="wide")
st.title("🏆 Acro World Tour: Professional AI Judge")

with st.sidebar:
    st.header("1. API & Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Processing Chunk (Minutes)", 15, 60, 45)
    
    st.header("2. Official AWT Data")
    official_data = st.text_area("Paste Official Results Here", height=150)

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
        if st.button("🚀 Start Analysis"):
            # STEP 1: Process the URL (The AI needs the video "attached", not just a link)
            with st.spinner("Preparing video for analysis (this avoids the 400 error)..."):
                try:
                    # In 2026, we pass the URL directly as a string part for YouTube 
                    # This lets the model's 'Video Tool' handle the fetch.
                    video_part = types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}")
                    
                    all_rows = []
                    total_mins = int(vid_hours * 60)
                    progress_bar = st.progress(0)
                    table_placeholder = st.empty()

                    for start_m in range(0, total_mins, chunk_size):
                        end_m = start_m + chunk_size
                        
                        prompt = f"""
                        Watch the video segment from {start_m}:00 to {end_m}:00.
                        1. IDENTIFY pilot names from the BOTTOM-LEFT screen graphic.
                        2. COMPARE against these official results: {official_data}
                        3. SCORE (100pt Scale): Tech (40), Choreo (40), Landing (20).
                        
                        Return ONLY a markdown table:
                        Pilot | Start | End | AI_Total | Official_Score | Maneuvers
                        """

                        # FIXED: We send the prompt and the URL reference as separate parts
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[video_part, prompt]
                        )

                        chunk_rows = parse_ai_table(response.text)
                        all_rows.extend(chunk_rows)
                        if all_rows:
                            table_placeholder.table(pd.DataFrame(all_rows))

                        progress_bar.progress(min(end_m / total_mins, 1.0))
                        time.sleep(10) # Quota protection

                    if all_rows:
                        st.success("Analysis Complete!")
                        st.download_button("📥 Download CSV", pd.DataFrame(all_rows).to_csv(index=False).encode('utf-8'), "Report.csv")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")
