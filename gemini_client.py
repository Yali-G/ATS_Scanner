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
        1.  **FIRST, from the Job Description ONLY, identify up to 10 (MAX 10, NO MORE. BUT IT CAN BE LESS) highly essential ATS keywords.** These should include critical skills, tools, and responsibilities that an Applicant Tracking System would strictly prioritize. Do NOT refer to the resume yet for this step.
        2.  **THEN, using ONLY the MAX 15 keywords you just identified, compare them against the provided Resume. Split the keywords into two categories:
        The keywords should be derived from the job description and should not exceed 10 in total. If the total number of keywords in 'found' + 'missing' is not exactly 10, your output will be rejected.
            - **Found:** Keywords that are present in the resume.
            - **Missing:** Keywords that are absent from the resume.
        3.  Calculate a match score out of 100.
        4.  Provide detailed, actionable feedback to the user on how to improve their resume's ATS compatibility and overall effectiveness for this specific job. (Make sure to keep the feedback under 500 characters.)

        **Scoring Criteria (out of 100):**
        * **Direct Keyword Matches (40%):** How many exact or very close matches of essential skills, tools, and responsibilities are present in the resume from the job description.
        * **Semantic Relevance (30%):** How well the resume demonstrates understanding and experience in the core areas mentioned, even if not using exact keywords (e.g., "managing teams" vs. "led a group of 5 engineers").
        * **Quantifiable Achievements (15%):** Presence of numbers, metrics, and results that demonstrate impact (e.g., "increased sales by 20%", "reduced bug reports by 15%").
        * **Overall Fit & Structure (10%):** Professional formatting, clear sections, use of action verbs, conciseness, and relevance of experience.
        * **Missing Critical Skills (5% penalty):** Significant points of disconnect or absolutely critical skills mentioned in the JD but missing from the resume.

        **Job Description:**
        ```
        {job_description}
        ```

        **Resume:**
        ```
        {resume_text}
        ```

        **Output Format:**
        Please provide your response in a JSON format. The JSON should have the following structure:

        ```json
        {{
        "match_score": 0, // Integer score out of 100
        "feedback": {{
            "overall_summary": "string" // Provide a concise analysis of the resume's alignment. This MUST be:
            - Exactly 4 full sentences.
            - Under **500 characters total** (including spaces).
            - Grammatically complete and coherent.
            If these conditions are violated (e.g., too long, too short, sentence fragments), your entire output will be rejected. Do NOT truncate or cut off sentences. Think like an ATS that will discard invalid formats.

            "keywords": {{
                //Make sure that the total number of keywords in 'found' + 'missing' is exactly 10.
            "found": ["keyword1", "keyword2"], // List of **Found:** ATS keywords that you created earlier
            "missing": ["keyword3", "keyword4"], //  List of **Missing:** ATS keywords that you created earlier
            "suggestions": "string" // Specific advice on how to integrate missing keywords contextually
            }},
            "formatting_suggestions": [ // List of general formatting and structural improvements be as specific as possible. Tell the user what they should do to improve their resume and where that might be.
            //The following are examples, but you should tailor them to the resume and job description. Only suggest formatting changes that you as an ATS would be looking for and that aren't already present in the resume. :
            "Use strong action verbs at the beginning of bullet points like when you said 'Committed' or 'Driven' in your summary.",
            "Ensure consistent date formatting.",
            "Consider adding a summary/objective tailored to the job.",
            "Quantify achievements whenever possible (e.g., 'increased X by Y%')."
            ],
        }}
        }}
        ```

        **Important Considerations for Gemini:**
        * Be highly accurate in identifying keywords.
        * Provide concrete and actionable advice.
        * Maintain a professional and helpful tone.
        * If the resume has significant formatting issues that would hinder ATS, mention them under `formatting_suggestions`.
        * **Crucially, ensure the JSON output is always complete and valid. Do not truncate any strings or the overall JSON structure.**
        * **The `overall_summary` field MUST be a concise, complete paragraph, exactly 4 sentences long and under 500 characters. No partial sentences or cut-offs.**
        * **For the 'keywords' section: Identify a maximum of 15 essential keywords ONLY from the Job Description first. Then, ONLY use these 15 keywords to populate the 'found' and 'missing' lists. The sum of 'found' and 'missing' keywords MUST be exactly 15.**
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