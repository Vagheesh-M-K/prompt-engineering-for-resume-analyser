import streamlit as st
import numpy as np
import re
from PyPDF2 import PdfReader
import docx2txt
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

st.header('For the jobs you truly deserve')
job_profile = st.text_area('Paste the Job Description Text')
resume = st.file_uploader(label='Upload your Resume')


if resume :
    name_of_the_resume_file = resume.name

    if re.search(r'.doc',name_of_the_resume_file) is not None :
        resume_data_as_str = docx2txt.process(resume)

    elif re.search(r'.pdf',name_of_the_resume_file) is not None :
        object = PdfReader(resume)
        resume_data_as_str = "\n\n".join([page.extract_text() for page in object.pages])
        
    else :
        st.write('Your resume should be uploaded as a .docx or a .pdf file')


def google_llm(temperature, max_output_tokens, top_p) :
    import os
    from google import generativeai
    generativeai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    generation_config = {"temperature": temperature, 
                        "max_output_tokens": max_output_tokens, 
                        "top_p" : top_p,
                        "response_mime_type": "text/plain"}
    return generativeai.GenerativeModel(model_name="gemini-1.5-pro",
                                generation_config=generation_config)

llm = google_llm(temperature=0.25, max_output_tokens=1000, top_p = 0.5)
## NOTE I HAVE REMOVED top_p from LLM just as a part of testing.
## I CAN ADD IT BACK WHENEVER I WANT

prompt2 = """Given below are 3 portions of text namely INSTRUCTIONS, RESUME, JD.
RESUME is the candidate's resume , JD is job profile which describes what the
employer seeks or what the job demands from the candidate. INSTRUCTIONS are series
of steps you do using the RESUME and JD.

Follow the INSTRUCTIONS to help the candidate accurately asses 
all that match and all that is missing between a candidate's resume (skills,
experience, capability, background) and the job profile


JD
'''{jd}'''

RESUME
'''{resume}'''

<INSTRUCTIONS>
{instructions}
</INSTRUCTIONS>
"""
instruction3 = """**Steps to follow:**


1. **Extract the job profile:**

2. **Extract the candidate's resume:**

3. **Match the candidate's resume  to the job profile:**
   - Compare the candidate's skills, experience, and education and other relevant information to the job profile.
   - Identify the relationships between candidate's resume and the job profile
   - Identify the match as well as mismatch between candidate's resume and job profile.

4. **Generate a report:**
   - Summarize the candidate's resume and the job profile 
   - Highlight the match as well as mis-match between candidate's resume and job profile.
   - Provide recommendations for how the candidate can become a better fit for the job."""



pr_template = PromptTemplate.from_template(prompt2)
if st.button("Analyze") :
    prompt_final = pr_template.format(instructions = instruction3, jd =job_profile,  
                                    resume = resume_data_as_str)

    aaa = llm.generate_content(contents=prompt_final)
    aaa_as_text = aaa._result.candidates[0].content.parts[0].text

    st.write(aaa_as_text)