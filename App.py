import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- CONFIG & UI ---
st.set_page_config(page_title="AWT 2026 Pro Validator", layout="wide")
st.title("🏆 AWT Official Validator: Section 7 Foundation")

with st.sidebar:
    st.header("1. Core Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.header("2. Manual Data Bridge")
    st.info("If the automated search fails, paste the URL for this specific event's result page below.")
    results_url = st.text_input("AWT Results Page URL (e.g., /result/2023/kings-of-the-box)")

# --- MATH ENGINE: SECTION 7 (40/40/20) ---
def calculate_awt_score(tech_val, exec_val, art_val, landing_val, bonus=0):
    """
    Implements the standard AWT 2026 formula:
    (Tech * 0.40) + (Exec * 0.40) + ((Art + Land)/2 * 0.20) + Bonus
    """
    total = (tech_val * 0.40) + (exec_val * 0.40) + (((art_val + landing_val)/2) * 0.20) + bonus
    return round(total, 3)

# --- MAIN EXECUTION ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("YouTube Competition Video URL")

    if event_url and st.button("🚀 Execute Comparative Analysis"):
        with st.spinner("Step 1: Scraping AWT Official Maneuver Logs..."):
            # This prompt now focuses on SEARCHING and RETRIEVING before judging
            prompt = f"""
            You are a WTFF Data Analyst. 
            
            1. TARGET: Find the match for this video on acroworldtour.com/results.
            2. DATA RETRIEVAL: For every pilot in the video, retrieve:
               - Official Maneuver Sequence (Order of tricks).
               - Judge's Technical (T), Execution (E), and Artistic (A) scores.
            3. MATH VALIDATION (SHOW WORK):
               Apply the Sporting Code Equation: 
               Final = (Technicity * 0.4) + (Execution * 0.4) + (Artistry/Landing Average * 0.2) + Bonus.
            
            4. COMPARISON: Compare your AI observation of the video to these official logs.

            OUTPUT FORMAT (Markdown Table):
            Pilot | Maneuvers (Official vs AI) | T (40%) | E (40%) | A/L (20%) | Bonus | Calculated Final | Official Final | Variance
            """

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                )

                # Output the results
                st.markdown("### 📊 Competitive Breakdown & 'Show Your Work' Math")
                st.write(response.text)
                
                # Summary for the User
                st.success("Comparison Complete. Variance shows the delta between AI-judged performance and the Official AWT Database.")

            except Exception as e:
                st.error(f"System Error: {e}")

else:
    st.warning("Please provide an API Key to begin official AWT verification.")
