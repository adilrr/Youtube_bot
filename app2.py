import streamlit as st
import os
import google.generativeai as genai
from summarizer import link_processor

def llm_function(query, option, length):
    if length == "Short":
        min_tokens = 700
        max_tokens = 1000
    elif length == "Long":
        min_tokens = 2500
        max_tokens = 8192
    
    options = [
    f'''
Tone: Casual, humorous
Lexical Choices: Contemporary, crass
Dialogue: Quotes, hypothetical
Structure: Chronological, suspenseful
Narrative Perspective: Omniscient
Pacing: Rapid
Repetition: Emphasis
Number of Words: {min_tokens}-{max_tokens}
    ''', 
    f'''
Tone: Conversational, dramatic
Structure: Setup, conflict, resolution
Transition and Pacing: Smooth, quick
Language: Informal, rhetorical
Emotional Appeal: Emotional
Direct Audience Engagement: Interactive
Commentary and Opinion: Opinionated, sarcastic
Sound Effects: Inferred
Number of Words: {min_tokens}-{max_tokens}
    '''
    ]
    
    if option == "Option 1":
        selected_option = options[0]
    elif option == "Option 2":
        selected_option = options[1]

    prompt = f"You are a professional script writer who writes a complete {length} video script strictly according to the Context and Instructions. \nInstructions:\n{selected_option}\n\n"
    print(prompt + "Context:\n" + query)

    response = model.generate_content(prompt + "Context:\n" + query, safety_settings=[
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    ],
    generation_config=genai.types.GenerationConfig(max_output_tokens = max_tokens),
    )

    with st.chat_message("assistant"):
        st.markdown(response.text)


st.set_page_config(
        page_title="Script Writer",
)
st.title("Script Writer")

os.environ['GOOGLE_API_KEY'] = "AIzaSyCTVNBGUsVqG2b37HbBrruCRooYJw4dsMA"
genai.configure(api_key = os.environ['GOOGLE_API_KEY'])

model = genai.GenerativeModel('gemini-1.5-pro-001')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"assistant",
            "content":"I will help you with the script writing just enter the context and script options and press generate button."
        }
    ]

col1, col2 = st.columns([2, 1])

with col1:
    link_input = st.text_input("Enter youtube video link: ", key="link_input", placeholder="Enter youtube video link")
    st.text_area("Enter your script context:", key="query_input", placeholder="Enter your script context", height=200)

with col2:
    transcribe_button = st.button("Transcribe", key="transcribe")
    option = st.selectbox("Select Script Option", ["Not Selected", "Option 1", "Option 2"], key="script_option")
    length = st.selectbox("Select Script Length", ["Not Selected", "Short", "Long"], key="script_length")
    generate_button = st.button("Generate", key="generate_prompt")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query = st.session_state.query_input
script_option = st.session_state.script_option
script_length = st.session_state.script_length

if transcribe_button:
    if link_input and script_option != "Not Selected" and script_length != "Not Selected":
        query = link_processor(link_input)
        llm_function(query, option, length)

if query:
    with st.chat_message("user"):
        st.markdown(query)

    if generate_button:
        if query and script_option != "Not Selected" and script_length != "Not Selected":
            llm_function(query, option, length)
            transcribed_text = ""
        else:
            st.warning("Please fill in all fields before generating the script.")
