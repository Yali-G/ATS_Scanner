# app.py
import streamlit as st
from parsers import extract_text_from_pdf, extract_text_from_docx
from gemini_client import analyze_resume_with_gemini
from dotenv import load_dotenv

load_dotenv()

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Gemini ATS Resume Analyzer", layout="wide")

st.title("🚀 Gemini ATS Resume Analyzer")
st.write("Upload your resume and paste a job description to get an ATS match score and personalized improvement suggestions powered by Google Gemini.")

# --- Input Section ---
st.header("1. Provide Job Description")
job_description = st.text_area(
    "Paste the Job Description here:",
    height=300,
    placeholder="e.g., 'We are looking for a highly motivated Software Engineer with experience in Python, AWS, and Agile methodologies...'"
)

st.header("2. Upload Your Resume")
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

resume_text = ""
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "pdf":
        # Pass the uploaded_file object directly to the parser
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        # Pass the uploaded_file object directly to the parser
        resume_text = extract_text_from_docx(uploaded_file)

    if resume_text:
        st.success("Resume uploaded and parsed successfully!")
    else:
        st.error("Could not parse resume. Please try a different file or format.")
else:
    st.info("Please upload your resume to proceed.")

# --- Analysis Button ---
if st.button("Analyze Resume", type="primary"):
    if job_description and resume_text:
        with st.spinner("Analyzing your resume... This may take a moment."):
            analysis_result = analyze_resume_with_gemini(job_description, resume_text)

        if analysis_result:
            st.success("Analysis Complete!")
            st.header("3. Your ATS Analysis Results")

            # --- Displaying the Analysis ---

            # 1. Match Score
            st.subheader("🌟 ATS Match Score")
            score = analysis_result.get('match_score', 'N/A')
            if score != 'N/A':
                # Use a progress bar or metric for visual appeal
                st.metric(label="Overall Match", value=f"{score}%")
                # Optional: Add a simple color indicator based on score
                if score >= 80:
                    st.success("Excellent alignment! Your resume is highly compatible with this job description.")
                elif score >= 60:
                    st.warning("Good alignment, but there's room for improvement to boost your ATS score.")
                else:
                    st.error("Your resume needs significant improvements for this job description's ATS compatibility.")
            else:
                st.info("Match score could not be determined.")

            # 2. Overall Summary
            st.subheader("📝 Overall Summary")
            st.write(analysis_result.get('feedback', {}).get('overall_summary', 'No overall summary provided.'))

            # 3. Keyword Analysis (Using Columns for better layout)
            st.subheader("🔑 ATS Keyword Analysis")
            keywords_feedback = analysis_result.get('feedback', {}).get('keywords', {})
            found_keywords = keywords_feedback.get('found', [])
            missing_keywords = keywords_feedback.get('missing', [])
            keyword_suggestions = keywords_feedback.get('suggestions', 'No specific keyword suggestions provided.')

            col1, col2 = st.columns(2) # Create two columns

            with col1:
                st.markdown("##### Keywords Found in Your Resume ✅")
                if found_keywords:
                    for keyword in found_keywords:
                        st.markdown(f"- **`{keyword}`**") # Use markdown for bolding keywords
                else:
                    st.info("No specific keywords identified as found. This might indicate low relevance.")

            with col2:
                st.markdown("##### Key Keywords to Add/Integrate ❌")
                if missing_keywords:
                    for keyword in missing_keywords:
                        st.markdown(f"- **`{keyword}`**")
                else:
                    st.success("Great! All key keywords from the job description appear to be present or semantically covered.")

            st.markdown("---") # Separator for clarity
            st.markdown("##### Suggestions for Integrating Missing Keywords:")
            st.info(keyword_suggestions)

            # 4. Formatting and General Improvement Suggestions
            st.subheader("💡 Formatting & General Improvement Suggestions")
            formatting_suggestions = analysis_result.get('feedback', {}).get('formatting_suggestions', [])
            if formatting_suggestions:
                for suggestion in formatting_suggestions:
                    st.write(f"- {suggestion}")
            else:
                st.info("Your resume formatting appears to be generally good for ATS compatibility.")

            # 5. Additional Tips
            st.subheader("✨ Additional Tips")
            additional_tips = analysis_result.get('feedback', {}).get('additional_tips', 'No additional tips provided.')
            st.write(additional_tips)

        else:
            st.error("Failed to get analysis from Gemini. Please check your inputs and API key.")
            st.info("If the issue persists, check your terminal for more specific error messages from the Gemini API.")
    else:
        st.warning("Please provide both a job description and upload your resume to start the analysis.")

st.markdown("---")
st.caption("Powered by Google Gemini API")