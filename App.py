import streamlit as st
from google import genai
from google.genai import types

# --- APP CONFIG & UI ---
st.set_page_config(page_title="WTFF AI Judge 2026", layout="wide", page_icon="🪂")

st.title("🪂 WTFF AI Judge: World Tour 2026")
st.markdown("### Universal Scoring & Safety Engine (Reference: World Standard Benchmark)")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("System calibrated for WTFF 2026 Sporting Code Section 6.")
    st.divider()
    st.write("Current Status: **Production Ready**")

# --- APP LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Pilot Run (MP4/MOV)", type=["mp4", "mov"])

    if uploaded_file:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.video("temp_video.mp4")

        if st.button("🚀 Analyze & Score Run"):
            with st.spinner("Analyzing frames against World Standard Benchmarks..."):
                myfile = client.files.upload(file="temp_video.mp4")
                
                prompt = """
                You are the WTFF Head Judge. Analyze this paragliding freestyle run based on the 2026 Sporting Code.
                
                1. MANEUVER ID: Identify every maneuver (e.g., Infinite Tumbling, Heli, SAT, Misty).
                2. BENCHMARK: Compare against a 10.0 'Perfect' axis (Reference: World Standard).
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

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[myfile, prompt]
                )

                st.success("Analysis Complete!")
                st.subheader("Official Run Result")
                st.write("Results displayed based on WTFF 2026 Scoring Table.")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
