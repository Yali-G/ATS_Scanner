# gemini_client.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import sys
load_dotenv()


def analyze_resume_with_gemini(job_description, resume_text):

    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={
                'response_mime_type': 'application/json',
                'max_output_tokens': 1024,
                'temperature': 0.7 
            }
        )
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    
        prompt_content = f"""
        You are an expert ATS (Applicant Tracking System) and a highly experienced career coach. Your task is to meticulously analyze a given job description and a resume.

        **Objective:**
        1. **FIRST, look ONLY at the following Job Description. Identify a list called 'keywords' containing the MOST essential ATS keywords.**
           - **IMPORTANT: 'keywords' MUST be a list of NO MORE THAN 15 WORDS. IT CAN BE LESS, BUT NEVER MORE THAN 15.**
           - DO NOT use phrases, only single words or short terms.
           - These should be the most critical skills, tools, and responsibilities that an Applicant Tracking System would strictly prioritize.
           - **DO NOT refer to the resume for this step.**
           - **ONCE YOU CHOOSE THESE KEYWORDS, DO NOT CHANGE THEM LATER.**
        This is the job description you should be looking at: {job_description}

        2. **THEN, ONLY after you have the 'keywords' list, analyze the resume.**
           - For each word in 'keywords', check if it is present in the resume.
           - **Split the 'keywords' list into two categories:**
             - **'present keywords': ONLY those words from 'keywords' that are found in the resume.**
             - **'missing keywords': ONLY those words from 'keywords' that are NOT found in the resume.**
           - **DO NOT add any words to 'present keywords' or 'missing keywords' that are not in your original 'keywords' list.**
           - **CRITICALLY IMPORTANT: IF ANY WORD IN 'missing keywords' IS ACTUALLY PRESENT IN THE RESUME, THE OUTPUT WILL BE REJECTED. DOUBLE CHECK THAT NO WORD IN 'missing keywords' APPEARS ANYWHERE IN THE RESUME.**
        This is the resume you need to analyze: {resume_text}

        3. Calculate a match score out of 100. Use the following criteria:

        **Scoring Criteria (out of 100):**
        * **Direct Keyword Matches (40%)**: How many exact or very close matches of essential skills, tools, and responsibilities are present in the resume from the job description.
        * **Semantic Relevance (30%)**: How well the resume demonstrates understanding and experience in the core areas mentioned, even if not using exact keywords (e.g., "managing teams" vs. "led a group of 5 engineers"). Use your discretion to determine if the candidate is a good fit.
        * **Quantifiable Achievements (15%)**: Presence of numbers, metrics, and results that demonstrate impact (e.g., "increased sales by 20%", "reduced bug reports by 15%").
        * **Overall Fit & Structure (10%)**: Professional formatting, clear sections, use of action verbs, conciseness, and relevance of experience.
        * **Missing Critical Skills (5% penalty)**: Significant points of disconnect or absolutely critical skills mentioned in the JD but missing from the resume. If these are not missing, then award the 5%.

        4. Provide detailed, actionable feedback to the user on how to improve their resume's ATS compatibility and overall effectiveness for this specific job. (Make sure to keep the feedback under 500 characters.)

        **Output Format:**
        Please provide your response in a JSON format. The JSON should have the following structure:

        ```json
        {{
          "match_score": 0, // Integer score out of 100
          "feedback": {{
            "overall_summary": "string", // Provide a concise analysis of the resume's alignment. This MUST be:
              // - Exactly 4 full sentences.
              // - Under 500 characters total (including spaces).
              // - Grammatically complete and coherent.
              // If these conditions are violated (e.g., too long, too short, sentence fragments), your entire output will be rejected. Do NOT truncate or cut off sentences. Think like an ATS that will discard invalid formats.

            "keywords": {{
              "found": ["keyword1", "keyword2"], // List of "present keywords": ONLY words from your original 'keywords' list that are found in the resume.
              "missing": ["keyword3", "keyword4"], // List of "missing keywords": ONLY words from your original 'keywords' list that are NOT found in the resume. **IF ANY WORD IN THIS LIST IS ACTUALLY PRESENT IN THE RESUME, THE OUTPUT WILL BE REJECTED.**
              "suggestions": "string" // Specific advice on how to integrate missing keywords contextually
            }},
            "formatting_suggestions": [ // List of general formatting and structural improvements. Be as specific as possible. Tell the user what they should do to improve their resume and where that might be.
              // The following are examples, but you should tailor them to the resume and job description. Only suggest formatting changes that you as an ATS would be looking for and that aren't already present in the resume.
              "Use strong action verbs at the beginning of bullet points like when you said 'Committed' or 'Driven' in your summary.",
              "Ensure consistent date formatting.",
              "Consider adding a summary/objective tailored to the job.",
              "Quantify achievements whenever possible (e.g., 'increased X by Y%')."
            ]
          }}
        }}
        ```

        **Important Considerations for Gemini:**
        * **'keywords' MUST be a list of NO MORE THAN 15 WORDS. IT CAN BE LESS, BUT NEVER MORE THAN 15.**
        * **'present keywords' and 'missing keywords' MUST ONLY contain words from your original 'keywords' list.**
        * **NO WORD IN 'missing keywords' CAN APPEAR IN THE RESUME. IF THIS HAPPENS, THE OUTPUT IS INVALID AND WILL BE REJECTED.**
        * Be highly accurate in identifying keywords.
        * Provide concrete and actionable advice.
        * Maintain a professional and helpful tone.
        * If the resume has significant formatting issues that would hinder ATS, mention them under `formatting_suggestions`.
        * **Crucially, ensure the JSON output is always complete and valid. Do not truncate any strings or the overall JSON structure.**
        * **The `overall_summary` field MUST be a concise, complete paragraph, exactly 4 sentences long and under 500 characters. No partial sentences or cut-offs.**
        """
        


        response = model.generate_content(prompt_content)
        
        # In JSON mode, response.text should already be valid JSON
        analysis_result = json.loads(response.text)
        return analysis_result

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from Gemini: {e}")
        print(f"Raw Gemini response: {response.text if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None