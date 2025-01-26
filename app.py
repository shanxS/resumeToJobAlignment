import streamlit as st
from anthropic import Anthropic
import PyPDF2
import requests
from bs4 import BeautifulSoup
import io

st.title("Resume-Job Matcher")
st.markdown("""
    Upload your resume and job posting URL to get:
    - **Match Score**
    - **Matching Skills Analysis**
    - **Missing Skills Identification**
    - **Improvement Suggestions**
    [Code](https://github.com/shanxS/resumeToJobAlignment)
""")

api_key = st.text_input("Enter Anthropic API Key", type="password")
if api_key:
   st.session_state['api_key'] = api_key

resume = st.file_uploader("Upload Resume", type=["pdf"])
job_url = st.text_input("Job Posting URL")

if resume and job_url and st.session_state.get('api_key'):
   if st.button("Analyze Match"):
       with st.spinner('Analyzing...'):
           # Process resume
           pdf_reader = PyPDF2.PdfReader(resume)
           resume_text = ""
           for page in pdf_reader.pages:
               resume_text += page.extract_text()

           # Fetch job posting
           response = requests.get(job_url)
           soup = BeautifulSoup(response.text, 'html.parser')
           job_text = soup.get_text()

           # Call Claude
           client = Anthropic(api_key=st.session_state['api_key'])
           message = client.messages.create(
               model="claude-3-5-sonnet-20241022",
               max_tokens=1000,
               messages=[{
                   "role": "user", 
                   "content": f"Compare this resume:\n{resume_text}\n\nWith this job posting:\n{job_text}\n\nProvide:\n1. Match score (0-100)\n2. Matching skills\n3. Missing skills\n4. Improvement suggestions"
               }]
           )

           # Update the display part in app.py
           if message.content:
               # Create sections
               st.header("Analysis Results")

               # Extract sections using string manipulation
               sections = message.content[0].text.split('\n\n')

               for section in sections:
                   if 'Match Score' in section:
                       st.metric("Match Score", section.split(': ')[1])
                   elif 'Matching Skills' in section:
                       st.subheader("Matching Skills")
                       skills = section.split('\n- ')[1:]
                       for skill in skills:
                           st.write(f"✅ {skill}")
                   elif 'Missing Skills' in section:
                       st.subheader("Missing Skills/Gaps")
                       skills = section.split('\n- ')[1:]
                       for skill in skills:
                           st.write(f"❌ {skill}")
                   elif 'Improvement Suggestions' in section:
                       st.subheader("Suggestions")
                       suggestions = section.split('\n1. ')[1].split('\n2. ')
                       for suggestion in suggestions:
                           st.write(f"💡 {suggestion}")
