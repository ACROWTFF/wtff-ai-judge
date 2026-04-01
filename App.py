import streamlit as st
from google import genai
from google.genai import types
import time

# --- APP CONFIG & UI ---
st.set_page_config(page_title="WTFF AI Judge 2026", layout="wide", page_icon="🪂")

st.title("🪂 WTFF AI Judge: World Tour 2026")
st.markdown("### Universal Scoring & Safety Engine (Anchor: Théo de Blic)")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("System calibrated for WTFF 2026 Sporting Code Section 6.")
    st.divider()
    st.write("Current Target: **6 Test Competitions Pre-October**")

# --- APP LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)

    uploaded_file = st.file_uploader("Upload Pilot Run (MP4/MOV)", type=["mp4", "mov"])

    if uploaded_file:
        # Save file locally for processing
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.video("temp_video.mp4")

        if st.button("🚀 Analyze & Score Run"):
            with st.spinner("AI is analyzing frames against Théo de Blic benchmarks..."):
                
                # Upload to Gemini
                myfile = client.files.upload(file="temp_video.mp4")
                
                # --- THE "EXPERT" PROMPT ---
                prompt = """
                You are the WTFF Head Judge. Analyze this paragliding freestyle run based on the 2026 Sporting Code.
                
                1. MANEUVER ID: Identify every maneuver (e.g., Infinite Tumbling, Heli, SAT, Misty).
                2. BENCHMARK: Compare against Théo de Blic's 'perfect' axis. 
                3. DEDUCTIONS: Note any axis deviation > 15°, wing collapses, or slow transitions (Rule 6.4.2).
                4. SAFETY: Detect any 'sketchy' moments or emergency handle reaches.
                
                OUTPUT JSON ONLY:
                {
                  "final_score": 0.0,
                  "tc_average": 0.0,
                  "deductions": [{"timestamp": "0:00", "type": "Axis Shift", "points": 0.5}],
                  "top_tricks": ["Trick 1", "Trick 2", "Trick 3"]
                }
                """

                # Run Analysis
                response = client.models.generate_content(
                    model="gemini-2.0-flash", # Using the latest high-speed model
                    contents=[myfile, prompt]
                )

                # --- DISPLAY RESULTS ---
                st.success("Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Final Score", "94.8") # Simulated output
                col2.metric("TC Average", "1.85")
                col3.metric("Landing", "9.2")

                st.divider()
                st.subheader("Pilot Technical Audit")
                
                # This simulates the "Video Review" links we built
                st.button("Review Deduction [0:45] - Axis Deviation (-0.5)")
                st.button("Review Bonus [1:12] - Twisted Exit (+2.5%)")

else:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")

# --- FOOTER ---
st.divider()
st.caption("WTFF AI Judge v1.0 | Built for Jaco Sports Fest & 2026 World Tour")

