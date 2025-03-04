import os
import time
import streamlit as st
import google.generativeai as genai

# Configure Google Gemini API
GEMINI_API_KEY = "AIzaSyCmWlJgNd6MZAVwe8a8-VC5wYbrk7sTJDg"
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is not set in the environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

def upload_to_gemini(path, mime_type="application/pdf"):
    """Uploads the given PDF file to Gemini API."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_files_active(files):
    """Waits for files to be processed by Gemini API."""
    for file in files:
        while True:
            file_status = genai.get_file(file.name)
            if file_status.state.name == "ACTIVE":
                break
            elif file_status.state.name != "PROCESSING":
                st.error(f"File {file.name} failed to process.")
                return False
            time.sleep(5)
    return True

def process_pdf(file_path):
    """Processes the uploaded PDF using Gemini API."""
    uploaded_file = upload_to_gemini(file_path)
    if wait_for_files_active([uploaded_file]):
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat_session = model.start_chat()
        response = chat_session.send_message(
            [
                uploaded_file,
                """
                1. Check if the document belongs to the current year. If not, state "Yes" or "No" and mention the document's year and month.
                2. Verify if the "Opinion" section on the first page mentions "profit". If it does, confirm what it says about the profit.
                3. Extract the NET PROFIT AFTER TAX amount from the Standalone Statement of Profit and Loss (Note: Not mention like million).
                4. Confirm if the section "Annexure B" of the Independent Auditor’s Report contains 20 points, numbered in Roman numerals.
                5. Check if the value of 'Property, plant, and equipment' in the Standalone Balance Sheet matches the 'Total Property, Plant, and Equipment' value in the 'PROPERTY, PLANT, AND EQUIPMENT AND INTANGIBLE ASSETS' table.
                """,
            ]
        )
        return response.text
    return None

# Streamlit UI
st.title("Financial Document Verification")

uploaded_file = st.file_uploader("Upload your financial PDF", type=["pdf"])
if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("Processing the document...")
    result = process_pdf("temp.pdf")
    if result:
        st.subheader("Verification Results:")
        st.text(result)
    else:
        st.error("Failed to process the document.")