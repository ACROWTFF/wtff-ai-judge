import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import time
import io

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF Sporting Code Analyzer", layout="wide")
st.title("🏆 WTFF / AWT 2026: Professional Judge Tool")
st.markdown("### Official Sporting Code Logic (Tech / Exec / Choreo / Land)")

with st.sidebar:
    st.header("1. API Authentication")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    chunk_size = st.slider("Analysis Window (Minutes)", 15, 60, 45)
    
    st.header("2. AWT Ground Truth")
    st.info("Paste official scores from acroworldtour.com here to calibrate the AI.")
    official_data = st.text_area("Paste Official Results (Pilot | Score)", height=200)

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
    
    col1, col2 = st.columns([3, 1])
    with col1:
        event_url = st.text_input("Paste YouTube Event URL")
    with col2:
        vid_hours = st.number_input("Video Length (Hrs)", min_value=0.5, value=3.0)

    if event_url:
        st.video(event_url)
        
        if st.button("🚀 Execute Sporting Code Analysis"):
            all_rows = []
            total_mins = int(vid_hours * 60)
            progress_bar = st.progress(0)
            status_text = st.empty()
            table_placeholder = st.empty()

            for start_m in range(0, total_mins, chunk_size):
                end_m = start_m + chunk_size
                status_text.warning(f"⚖️ Judging Segment: {start_m}m to {end_m}m...")

                # THE SPORTING CODE PROMPT
                # Forces specific terminology (Misty, Infinity, Heli) and 4-pillar math
                prompt = f"""
                Watch the segment from {start_m}:00 to {end_m}:00.
                You are a WTFF Head Judge. Use the 2026 Sporting Code.

                1. PILOT IDENTIFICATION: 
                   - Scan the BOTTOM-LEFT corner for name graphics. 
                   - Ground names against this AWT list: {official_data}

                2. MANEUVER IDENTIFICATION (Use Sporting Code Terms):
                   - Identify: Infinity Tumble, Rhythmic SAT, Esferis, Misty Flip, 
                     MacTwist to Helico, Twister, etc.

                3. SCORING PILLARS (Total 100):
                   - TECHNICAL DIFFICULTY (Max 35): Based on K-factors of maneuvers.
                   - EXECUTION (Max 35): Deduct for collapses, line slack, or poor axis.
                   - CHOREOGRAPHY (Max 15): Box placement, flow, and variety.
                   - LANDING (Max 15): Precision on target (Raft/Pad).
                
                4. CALCULATION: (Tech + Exec + Choreo + Land) = FINAL SCORE.

                RETURN ONLY A MARKDOWN TABLE:
                Pilot | Start | End | Maneuvers | Tech | Exec | Choreo | Land | AI_Total | Official_Score
                """

                try:
                    # Using Part.from_text for the URL triggers the internal video fetcher
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"),
                            prompt
                        ]
                    )

                    new_rows = parse_ai_table(response.text)
                    all_rows.extend(new_rows)
                    
                    if all_rows:
                        table_placeholder.table(pd.DataFrame(all_rows).tail(10))

                    progress_bar.progress(min(end_m / total_mins, 1.0))
                    
                    # Pause to stay under Tier 1 Paid TPM limits
                    time.sleep(12)

                except Exception as e:
                    if "429" in str(e):
                        st.error("Quota full. Waiting 60s to resume...")
                        time.sleep(60)
                    else:
                        st.error(f"Error at {start_m}m: {e}")
                        break

            if all_rows:
                st.success("🎯 Analysis Complete!")
                df = pd.DataFrame(all_rows)
                
                # Show full results
                st.dataframe(df, use_container_width=True)
                
                # Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Official AWT Comparison Report", csv, "AWT_Judge_Report.csv", "text/csv")
else:
    st.warning("Please enter your Gemini API Key to unlock professional judging.")
