import streamlit as st
import google.generativeai as genai
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
import os
import base64

# Set environment variable for protocol buffers
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Google Generative AI configuration

#GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Translator setup
translator = Translator()

# Streamlit UI
st.markdown("# ChatBot with URL Fetching 🔗")

# CSS Styling
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f0f2f6;
}
h1 {
    color: green;
    font-size: 35px;
}
h2 {
    color: green;
    font-size: 25px;
}
h3 {
    color: blue;
    font-size: 20px;
}
... (CSS styles)
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

def fetch_web_data(url):
    """
    Fetches and parses web data from the provided URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text(separator="\n")
        return text_content
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return None

def get_gemini_response(query, text_content):
    """
    Generates AI response based on the user query and text content.
    """
    context = f"Text content: {text_content}\n\nQuestion: {query}"
    response = genai.generate_text(prompt=context)
    return response.result

def is_response_relevant(response, text_content):
    """
    Checks if the response is relevant to the fetched content.
    """
    response_words = set(response.lower().split())
    content_words = set(text_content.lower().split())
    common_words = response_words.intersection(content_words)
    return len(common_words) > 5

def translate_to_hindi(text):
    """
    Translates text to Hindi.
    """
    translation = translator.translate(text, src='en', dest='hi')
    return translation.text

def get_binary_file_downloader_html(content, button_text, file_name):
    """
    Generates HTML for downloading a binary file.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    b64 = base64.b64encode(content).decode()
    html = f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{button_text}</a>'
    return html

# Streamlit UI components for URL fetching
st.header("ChatBot with URL Fetching")

url = st.text_input("Enter a URL to fetch data from:")
if url:
    text_content = fetch_web_data(url)

    if text_content:
        if "questions" not in st.session_state:
            st.session_state.questions = []
        if "answers" not in st.session_state:
            st.session_state.answers = []

        # Display previous questions and answers
        if st.session_state.questions:
            st.subheader("Responses:")
            for i, question in enumerate(st.session_state.questions):
                st.write(f"**Q: {question}**")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("English:")
                    st.write(st.session_state.answers[i]["english"])
                    st.markdown(get_binary_file_downloader_html(st.session_state.answers[i]["english"], "Download English Response", f"english_response_{i}.txt"), unsafe_allow_html=True)
                with col2:
                    st.subheader("Hindi:")
                    st.write(st.session_state.answers[i]["hindi"])
                    st.markdown(get_binary_file_downloader_html(st.session_state.answers[i]["hindi"], "Download Hindi Response", f"hindi_response_{i}.txt"), unsafe_allow_html=True)

        # Input text field
        with st.form(key='query_form'):
            input_text = st.text_input("Ask a Question About the URL Content:", key="input_question")
            st.form_submit_button(label="➔", help="Click to get the answer", on_click=lambda: None)

        if input_text:
            output = get_gemini_response(input_text, text_content)
            
            if is_response_relevant(output, text_content):
                english_response = output
                hindi_response = translate_to_hindi(english_response)
                
                # Store the question and answers in session state
                st.session_state.questions.append(input_text)
                st.session_state.answers.append({
                    "english": english_response,
                    "hindi": hindi_response
                })

            else:
                st.error("The content related to your question is not present in the provided URL.")
    else:
        st.write("No data fetched from the provided URL. Please check the URL and try again.")
else:
    st.write("Please enter a URL to fetch data from.")
