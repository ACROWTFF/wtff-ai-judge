import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF Batch Judge 2026", layout="wide")
st.title("🏆 WTFF Event Archive: 2.5 Flash Batch Processor")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    # 45 mins is the 'sweet spot' for Tier 1 Paid accounts
    chunk_size = st.slider("Chunk Size (Minutes)", 15, 60, 45)
    st.success("Model: Gemini 2.5 Flash (Stable)")

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
    event_url = st.text_input("Paste YouTube URL")
    vid_length_hours = st.number_input("Video Length (Hours)", min_value=0.5, value=3.0, step=0.5)

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Start Full Analysis"):
            all_rows = []
            total_minutes = int(vid_length_hours * 60)
            
            progress_bar = st.progress(0)
            status_area = st.empty()
            table_area = st.empty()

            for start_m in range(0, total_minutes, chunk_size):
                end_m = start_m + chunk_size
                status_area.warning(f"Processing segment: {start_m} to {end_m} minutes...")
                
                try:
                    prompt = f"""
                    Watch the segment from {start_m}:00 to {end_m}:00.
                    1. Identify every paragliding run. 
                    2. Return a table: Pilot | Start | End | Maneuvers | WTFF_Score.
                    Respond ONLY with the markdown table.
                    """

                    # UPDATED MODEL ID: gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/mp4"),
                            prompt
                        ]
                    )

                    new_data = parse_ai_table(response.text)
                    all_rows.extend(new_data)
                    
                    if all_rows:
                        table_area.table(pd.DataFrame(all_rows).tail(10))
                    
                    progress_perc = min((end_m / total_minutes), 1.0)
                    progress_bar.progress(progress_perc)

                    # Pause to stay under the 1M tokens-per-minute limit
                    time.sleep(10)

                except Exception as e:
                    if "404" in str(e):
                        st.error("Model Error: Please ensure you are using 'gemini-2.5-flash'.")
                    elif "429" in str(e):
                        st.info("Quota limit reached. Auto-waiting 60s...")
                        time.sleep(60)
                    else:
                        st.error(f"Error at {start_m}m: {e}")
                    break

            if all_rows:
                st.success("✅ Analysis Complete!")
                final_df = pd.DataFrame(all_rows)
                csv_buffer = io.BytesIO()
                final_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Full CSV",
                    data=csv_buffer.getvalue(),
                    file_name="WTFF_Event_Master.csv",
                    mime="text/csv",
                )
else:
    st.warning("Please enter your API Key.")
