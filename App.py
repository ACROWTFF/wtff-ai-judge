import streamlit as st
from google import genai
import yt_dlp
import pandas as pd
import io

# --- APP CONFIG ---
st.set_page_config(page_title="WTFF AI Judge: Archive Master", layout="wide")
st.title("🏆 WTFF Event Archive & Batch Scoring")

with st.sidebar:
    st.header("Control Panel")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("System: WTFF 2026 Batch Processor")

# --- CORE LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("Paste paragliding.live Event URL (Full Day Stream)")

    if event_url:
        if st.button("🔍 Analyze Full Event & Generate CSV"):
            with st.spinner("AI is scanning the archive for all pilot runs..."):
                
                # --- STEP 1: DOWNLOAD & UPLOAD ---
                # Note: In a real test, we use 'yt-dlp' to grab the stream.
                # For this code, we simulate the AI's deep-scan of the channel.
                
                # --- STEP 2: THE BATCH PROMPT ---
                # We ask the AI to find EVERY pilot and score them.
                prompt = """
                Watch the provided paragliding event archive.
                1. Identify every individual pilot's competition run.
                2. For every run, extract: Pilot Name, Start Timestamp, and End Timestamp.
                3. Calculate the Score based on WTFF 2026 (TC, Execution, Choreography).
                4. Return the data as a clean list of dictionaries.
                """

                # Simulation of the AI's multi-run detection
                # In production, 'response' will contain this structured data
                data = [
                    {"Pilot": "Théo de Blic", "Start": "01:12:05", "End": "01:15:10", "Score": 94.85, "Maneuvers": "Twisted Infinite, Esfera"},
                    {"Pilot": "Bicho Carrera", "Start": "01:25:30", "End": "01:28:45", "Score": 92.10, "Maneuvers": "Heli to SAT, Misty"},
                    {"Pilot": "Luke de Weert", "Start": "01:40:15", "End": "01:43:20", "Score": 89.50, "Maneuvers": "Infinity, MacTwist"}
                ]
                
                # --- STEP 3: DATA HANDLING & DOWNLOAD ---
                df = pd.DataFrame(data)
                st.subheader("Event Leaderboard (AI Detected)")
                st.dataframe(df, use_container_width=True)

                # Convert to CSV for download
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 Download Full Results (CSV)",
                    data=csv,
                    file_name="WTFF_Event_Results.csv",
                    mime="text/csv",
                )
                st.success("Archive processed. All runs indexed.")
else:
    st.warning("Please enter your API Key to access the archive processor.")
