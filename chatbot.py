import streamlit as st
from google.generativeai import genai
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
import os
import base64

# Set environment variable for Google API key
os.environ["GOOGLE_API_KEY"] = "your_actual_api_key_here"

# Google Generative AI configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

input[type="text"] {
    background-color: #e6f7ff;
    color: #004085;
    border-radius: 5px;
    border: 1px solid #b8daff;
    padding: 10px;
    margin: 5px 0;
}
button {
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    border: none;
    padding: 10px 20px;
    margin: 5px 0;
    cursor: pointer;
}
button:hover {
    background-color: #0056b3;
}
input::placeholder {
    color: #888;
}
label[data-testid="stText"] {
    color: #ff5733;
    font-weight: bold;
}
.column {
    float: left;
    width: 50%;
}
.row:after {
    content: "";
    display: table;
    clear: both;
}
.stTextInput > label {
    color: indigo; /* Change this to your desired color */
    font-size: 100px;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Translator setup
translator = Translator()

# Function to fetch and parse web data
def fetch_web_data(url):
    try:
        text_content = ""
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content += soup.get_text(separator="\n")
        return text_content
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return ""

# Function to get AI response
def get_gemini_response(query, text_content):
    context = f"Text content: {text_content}\n\nQuestion: {query}"
    # Dummy response generation (replace with actual logic)
    response = {"result": "Dummy AI response"}
    return response["result"]

# Function to translate text to Hindi
def translate_to_hindi(text):
    try:
        translation = translator.translate(text, src='en', dest='hi')
        return translation.text
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        return "Translation Error"

# Function to generate a link for downloading a binary file
def get_binary_file_downloader_html(content, button_text, file_name):
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
        if "responses" not in st.session_state:
            st.session_state["responses"] = []

        # Display previous responses
        if st.session_state["responses"]:
            st.subheader("Previous Responses:")
            for i, response in enumerate(st.session_state["responses"]):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Response {i + 1} (English):")
                    st.write(response["english"])
                    st.markdown(get_binary_file_downloader_html(response["english"], f"Download English Response {i + 1}", f"english_response_{i + 1}.txt"), unsafe_allow_html=True)
                with col2:
                    st.subheader(f"Response {i + 1} (Hindi):")
                    st.write(response["hindi"])
                    st.markdown(get_binary_file_downloader_html(response["hindi"], f"Download Hindi Response {i + 1}", f"hindi_response_{i + 1}.txt"), unsafe_allow_html=True)

        # Input field and button for asking a new question
        input_text = st.text_input("Ask a Question About the URL Content:", key="input_question")
        submit_button = st.button("Get Instant Answer", key="submit_question")

        if submit_button and input_text:
            output = get_gemini_response(input_text, text_content)
            english_response = output
            hindi_response = translate_to_hindi(english_response)

            # Save the new response
            st.session_state["responses"].append({
                "english": english_response,
                "hindi": hindi_response
            })

            # Display the new response immediately
            st.subheader("New Response:")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("English:")
                st.write(english_response)
                st.markdown(get_binary_file_downloader_html(english_response, "Download English Response", "english_response.txt"), unsafe_allow_html=True)
            with col2:
                st.subheader("Hindi:")
                st.write(hindi_response)
                st.markdown(get_binary_file_downloader_html(hindi_response, "Download Hindi Response", "hindi_response.txt"), unsafe_allow_html=True)
    else:
        st.write("No data fetched from the provided URL. Please check the URL and try again.")
else:
    st.write("Please enter a URL to fetch data from.")
