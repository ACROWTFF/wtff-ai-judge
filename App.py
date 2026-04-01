import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF Batch Judge", layout="wide")
st.title("🏆 WTFF Event Archive: Auto-Batch Processor")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Chunk Size (Minutes)", 15, 60, 45)
    st.info("Strategy: Loops through the video in segments to avoid Tier 1 Quota errors.")

# --- UTILITY: PARSE AI TABLE ---
def parse_ai_table(text):
    """Extracts markdown table data into a list of dicts"""
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
    # Ask for duration so the loop knows when to stop
    vid_length_hours = st.number_input("Approximate Video Length (Hours)", min_value=0.5, value=3.0, step=0.5)

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Start Full Multi-Hour Analysis"):
            all_rows = []
            total_minutes = int(vid_length_hours * 60)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_area = st.empty()
            table_area = st.empty()

            for start_m in range(0, total_minutes, chunk_size):
                end_m = start_m + chunk_size
                status_area.warning(f"Processing segment: {start_m} to {end_m} minutes...")
                
                try:
                    # Requesting the specific window
                    prompt = f"""
                    Watch the segment from {start_m}:00 to {end_m}:00.
                    1. Identify every individual paragliding run.
                    2. Provide: Pilot | Start | End | Maneuvers | WTFF_Score.
                    Return ONLY a markdown table.
                    """

                    response = client.models.generate_content(
                        model='gemini-2.0-flash', # Fastest for batching
                        contents=[
                            types.Part.from_uri(file_uri=event_url, mime_type="video/mp4"),
                            prompt
                        ]
                    )

                    # Parse results from this chunk
                    new_data = parse_ai_table(response.text)
                    all_rows.extend(new_data)
                    
                    # Live update the UI with what we found
                    if all_rows:
                        table_area.table(pd.DataFrame(all_rows).tail(10)) # Show last 10 found
                    
                    # Progress update
                    progress_perc = min((end_m / total_minutes), 1.0)
                    progress_bar.progress(progress_perc)

                    # CRITICAL: Sleep for 5 seconds to let the 'Tokens Per Minute' quota reset
                    time.sleep(5)

                except Exception as e:
                    st.error(f"Error at minute {start_m}: {e}")
                    if "429" in str(e):
                        st.info("Quota hit. Waiting 60 seconds to resume...")
                        time.sleep(60)
                    else:
                        break

            # Final Summary
            if all_rows:
                st.success("✅ Analysis Complete!")
                final_df = pd.DataFrame(all_rows)
                
                # Create a download button for the full consolidated CSV
                csv_buffer = io.BytesIO()
                final_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download COMPLETE Event Results (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name="WTFF_Full_Event_Master.csv",
                    mime="text/csv",
                )
else:
    st.warning("Please enter your API Key to begin.")
