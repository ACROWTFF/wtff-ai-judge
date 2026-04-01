import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AWT Analyzer", layout="wide")
st.title("🏆 WTFF Event Archive: Professional Judge")

with st.sidebar:
    st.header("1. API & Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Chunk Size (Minutes)", 15, 60, 45)
    
    st.header("2. AWT Official Results")
    st.info("Paste the results from acroworldtour.com to guide the AI.")
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
        if st.button("🚀 Run Full Competition Analysis"):
            all_rows = []
            total_mins = int(vid_hours * 60)
            progress_bar = st.progress(0)
            status_area = st.empty()
            table_placeholder = st.empty()

            for start_m in range(0, total_mins, chunk_size):
                end_m = start_m + chunk_size
                status_area.warning(f"Processing: {start_m}m to {end_m}m...")

                # THE SPORTING CODE PROMPT
                prompt = f"""
                Watch the video segment from {start_m}:00 to {end_m}:00.
                ACT AS A SENIOR AWT JUDGE using the WTFF 2026 Sporting Code.

                1. PILOT IDENTIFICATION: 
                   - Extract the name from the LOWER-LEFT screen graphic.
                   - Match against this Official List: {official_data}

                2. MANEUVER IDENTIFICATION (Sporting Code Terminology):
                   - Use official names: Misty Flip, MacTwist, Infinity Tumble, Helico, 
                     Sat-to-Heli, Antirhythmic, Esfera, etc.

                3. CALCULATION (100pt Scale):
                   - Technical Difficulty (Max 35): Sum of maneuver k-factors.
                   - Execution (Max 35): Deductions for collapses or poor rotation.
                   - Choreography (Max 15): Energy, flow, and box placement.
                   - Landing (Max 15): Accuracy on the target raft/pad.
                
                RETURN ONLY A MARKDOWN TABLE:
                Pilot | Start | End | Maneuvers | Tech | Exec | Choreo | Land | AI_Total | AWT_Official
                """

                try:
                    # We pass the URL as a text part to trigger the YouTube fetch tool
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"),
                            prompt
                        ]
                    )

                    new_data = parse_ai_table(response.text)
                    all_rows.extend(new_data)
                    
                    if all_rows:
                        table_placeholder.table(pd.DataFrame(all_rows))

                    progress_bar.progress(min(end_m / total_mins, 1.0))
                    # Wait 10s to stay under Paid Tier 1 "Tokens Per Minute" quota
                    time.sleep(10)

                except Exception as e:
                    st.error(f"Error at {start_m}m: {e}")
                    if "429" in str(e):
                        st.info("Quota limit reached. Waiting 60s...")
                        time.sleep(60)
                    else:
                        break

            if all_rows:
                st.success("Analysis Complete!")
                df = pd.DataFrame(all_rows)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Master CSV Report", csv, "AWT_Report.csv", "text/csv")
else:
    st.sidebar.warning("Please enter your Gemini API Key.")
