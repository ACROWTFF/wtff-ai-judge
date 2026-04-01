# ... (rest of the Streamlit setup remains identical)

                try:
                    # THE 2026 SPORTING CODE PROMPT
                    prompt = f"""
                    Watch the segment from {start_m}:00 to {end_m}:00. 
                    Act as a Senior AWT Judge using the 2026 WTFF Sporting Code.

                    1. PILOT & RUN: Identify the name from the bottom-left graphic.
                    
                    2. MANEUVER LISTING (Sporting Code Terminology):
                       Identify only official maneuvers: Misty Flip, MacTwist, Infinity Tumble, 
                       Heli-to-Heli, Sat-to-Heli, Antirhythmic, etc. 

                    3. THE WTFF CALCULATION (Total 100):
                       A. Technical Difficulty (Max 35): Based on the k-factors of the maneuvers performed.
                       B. Execution (Max 35): Deduct for collapses, line tension loss, or poor rotations.
                       C. Choreography (Max 15): Flow, box placement, and variety.
                       D. Landing (Max 15): Precision on the target (15 = perfect, 0 = water/miss).
                       
                       FORMULA: (Tech + Execution + Choreo + Landing) - Penalties = FINAL SCORE.

                    4. GROUNDING: Compare your findings to these official results: {official_data}

                    RETURN ONLY A MARKDOWN TABLE:
                    Pilot | Start | End | Maneuvers | Tech | Exec | Choreo | Land | AI_TOTAL | AWT_OFFICIAL
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_text(text=f"VIDEO_SOURCE: {event_url}"),
                            prompt
                        ]
                    )

                    # ... (parsing and display code remains the same)
