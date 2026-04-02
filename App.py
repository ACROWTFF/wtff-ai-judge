import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import re

# --- APP CONFIG ---
st.set_page_config(page_title="AWT 2026 Pro Validator", layout="wide")
st.title("🏆 AWT Official Judge & Validator")
st.markdown("#### Section 7 Foundation: (40% Tech | 40% Exec | 20% Artistic & Landing)")

with st.sidebar:
    st.header("1. Authentication")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.header("2. Data Source")
    st.info("The AI will attempt to find the season and year matching the video.")
    manual_year = st.selectbox("Select Competition Year", [2023, 2024, 2025, 2026], index=0)

# --- MATH ENGINE: SHOW YOUR WORK ---
def format_calculation(pilot, t, e, a, l, bonus):
    # Standard AWT Section 7: (T*0.4) + (E*0.4) + ((A+L)/2 * 0.2) + B
    tech_part = float(t) * 0.4
    exec_part = float(e) * 0.4
    art_land_part = ((float(a) + float(l)) / 2) * 0.2
    final = tech_part + exec_part + art_land_part + float(bonus)
    
    work_str = f"({t}x0.4) + ({e}x0.4) + (({a}+{l})/2 x 0.2) + {bonus}"
    return round(final, 3), work_str

# --- MAIN LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    event_url = st.text_input("YouTube Event URL")

    if event_url and st.button("🚀 Run Official Comparison"):
        with st.spinner(f"Accessing AWT {manual_year} Archives..."):
            try:
                # PROMPT: Explicit instructions to use AWT Website logic
                prompt = f"""
                You are a WTFF Judge. Access the AWT digital archives for {manual_year}.
                
                1. MATCH: Find the event in the video (Location/Season).
                2. DATA: For every pilot, pull the Official Maneuver Sequence from the AWT results page.
                3. EVALUATE: Compare the AI video observation against the official maneuver order.
                
                4. CALCULATION (Show Your Work):
                   Use the 40/40/20 formula from the Sporting Code.
                   - Technicity (T): 40% weight
                   - Execution (E): 40% weight
                   - Artistic/Landing (A/L): 20% weight
                   - Bonus (B): Additive
                
                OUTPUT TABLE COLUMNS:
                Pilot | Official Maneuvers | T(40%) | E(40%) | A/L(20%) | Bonus | AI_Work | AI_Final | Official_Score
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"), prompt]
                )

                # Robust Parser for the complex table
                raw_text = response.text
                lines = [l.strip() for l in raw_text.split('\n') if l.count('|') > 5]
                
                if lines:
                    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                    data_rows = [l for l in lines[1:] if not re.match(r'^[|\s\-:]+$', l)]
                    
                    rows = []
                    for row in data_rows:
                        vals = [v.strip() for v in row.split('|') if v.strip()]
                        if len(vals) >= len(headers):
                            rows.append(dict(zip(headers, vals[:len(headers)])))
                    
                    df = pd.DataFrame(rows)
                    st.table(df)
                    
                    st.download_button("📥 Download AWT Comparative Report", df.to_csv(index=False).encode('utf-8'), "AWT_Validation.csv")
                else:
                    st.warning("AI analyzed the video but could not format the table. Raw output:")
                    st.write(raw_text)

            except Exception as e:
                st.error(f"Critical Failure: {e}")
else:
    st.warning("Please enter your API Key and ensure requirements.txt is uploaded to GitHub.")
