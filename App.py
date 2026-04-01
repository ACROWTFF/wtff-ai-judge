import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="AWT 2026 Pro Analyzer", layout="wide")
st.title("🏆 Acro World Tour: Professional AI Judge")
st.markdown("### Powered by Gemini 2.5 Flash + Official AWT Grounding")

with st.sidebar:
    st.header("1. API & Quota Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Processing Chunk (Minutes)", 15, 60, 45)
    
    st.header("2. Official AWT Data")
    st.info("Paste the results table from acroworldtour.com below to prevent hallucinations.")
    official_data = st.text_area("Paste Official Results Here", height=200, 
                                placeholder="Rank | Pilot | Score\n1 | Théo de Blic | 94.5\n2 | Luke de Weert | 92.1...")

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
    
    col1, col2 = st.columns([2, 1])
    with col1:
        event_url = st.text_input("Paste YouTube Event URL")
    with col2:
        vid_hours = st.number_input("Video Length (Hours)", min_value=0.5, value=3.0)

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Start Full Archive Analysis"):
            all_rows = []
            total_mins = int(vid_hours * 60)
            progress_bar = st.progress(0)
            status_text = st.empty()
            table_placeholder = st.empty()

            for start_m in range(0, total_mins, chunk_size):
                end_m = start_m + chunk_size
                status_text.warning(f"🔍 Analyzing {start_m}m to {end_m}m...")

                # THE MASTER PROMPT
                prompt = f"""
                Watch the segment from {start_m}:00 to {end_m}:00.
                You are an expert AWT Judge. Follow these instructions STICKLY:

                1. PILOT IDENTIFICATION (OCR): 
                   - Look at the BOTTOM-LEFT corner of the screen for the lower-third name graphic.
                   - Extract that exact name. 
                
                2. DATA GROUNDING:
                   - Use these official results as your Truth Source: {official_data if official_data else 'No data provided.'}
                   - Match the pilot on screen to a pilot in the official list.

                3. WTFF 2026 SCORING (100pt Scale):
                   - Technical (40 pts): Difficulty/execution of acro maneuvers.
                   - Choreography (40 pts): Flow, placement, and energy.
                   - Landing (20 pts): Precision on the target.
                   - CALCULATE: AI_Total = Tech + Choreo + Landing.

                RETURN ONLY A MARKDOWN TABLE:
                Pilot_Name | Start | End | Maneuvers | AI_Tech | AI_Choreo | AI_Landing | AI_Total | Official_AWT_Score
                """

                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/mp4"),
                            prompt
                        ]
                    )

                    # Extract and merge
                    chunk_rows = parse_ai_table(response.text)
                    all_rows.extend(chunk_rows)
                    
                    # Update live view
                    if all_rows:
                        table_placeholder.table(pd.DataFrame(all_rows).tail(15))

                    progress_bar.progress(min(end_m / total_mins, 1.0))
                    
                    # Tier 1 Quota Protection (10s delay)
                    time.sleep(10)

                except Exception as e:
                    if "429" in str(e):
                        st.error("Quota Exhausted. Waiting 60s to resume...")
                        time.sleep(60)
                    else:
                        st.error(f"Error at {start_m}m: {e}")
                        break

            # FINAL EXPORT
            if all_rows:
                st.success("🎯 Analysis Complete!")
                df = pd.DataFrame(all_rows)
                
                # Cleanup: Ensure scores are numeric for a quick variance check
                st.subheader("Performance Analytics")
                st.write("Below is your consolidated event report.")
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Master CSV Report", csv, "AWT_Full_Report.csv", "text/csv")
else:
    st.warning("Please enter your Gemini API Key in the sidebar.")
