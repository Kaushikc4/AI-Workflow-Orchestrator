import streamlit as st
import requests
import pdfplumber
import docx2txt
import tempfile

API_BASE = 'http://127.0.0.1:8000/api'

st.title("AI Workflow Pipeline UI")

st.header("Create a Pipeline")

# with st.form('pipeline_form'):
input_text = st.text_area('Input Text')
uploaded_file = st.file_uploader("Upload a document: ", type=["pdf", "txt", "docx"])
extracted_text = ""
step_options = ['SUMMARIZE', 'SCRAPE', 'TRANSLATE', 'NOTIFY']
selected_option = st.multiselect('Choose Steps', step_options)

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    try:
        if file_ext == "pdf":
            with pdfplumber.open(temp_path) as pdf:
                extracted_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

        elif file_ext == "docx":
            extracted_text = docx2txt.process(temp_path)

        elif file_ext == "txt":
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()

        else:
            st.error("Unsupported file type")

        input_text = extracted_text
        st.success("Document uploaded and text extracted successfully!")

    except Exception as e:
        st.error(f"Error extracting text: {e}")

if st.button("Next"):
    st.session_state["selected_steps"] = selected_option

step_data = []
input_data = []
if "selected_steps" in st.session_state:
    for step in selected_option:
        if step == 'SCRAPE':
            url = st.text_input(f"Enter url for {step}")
            step_data.append({
                "step_type": step,
                "input_data": {
                    "input_text": input_text
                }
            })
        elif step == 'SUMMARIZE':
            step_data.append({
                "step_type": step,
                "input_data": {
                    "input_text": input_text
                }
            })
        elif step == 'TRANSLATE':
            lang = st.text_input('Enter target language for translation: ')
            step_data.append({
                "step_type": step,
                "input_data": {
                    "input_text": input_text,
                    "target_lang": lang
                }
            })
        elif step == 'NOTIFY':
            method = st.selectbox('Choose notification method: ', ["SMS", "WHATSAPP"])
            reciever = st.text_input('Enter Phone number with Country code: ')

            step_data.append({
                "step_type": step,
                "input_data": {
                    "method": method,
                    "reciever": reciever
                }
            })

    submit_btn = st.button('Create Pipeline')

    if submit_btn:
        resp = requests.post(f"{API_BASE}/create-pipeline/", json={
            'steps': step_data
        })

        if resp.status_code == 200:
            pipeline_id = resp.json()["pipeline_id"]
            st.success(f"Pipeline created! ID: {pipeline_id}")
        else:
            st.error(f"Error: Failed to create pipeline.")


    st.header('Run a Pipeline')

    pipeline_to_run = st.number_input("Enter Pipeline ID: ", min_value=1)

    if st.button('Run Pipeline'):
        resp = requests.post(f"{API_BASE}/run-pipeline-api/{pipeline_to_run}/")

        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", "No result returned")
            st.success('Pipeline executed successfully')
            if result:
                st.write(result)
            else:
                st.write("Notification sent successfully!")
        else:
            st.error('Error: Pipeline run failed')

    if st.button("Go again!"):
        st.rerun()
