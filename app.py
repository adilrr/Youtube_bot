import streamlit as st
import os
from summarizer import link_processor
from dotenv import load_dotenv
import anthropic

load_dotenv()

def llm_function(query, option, length):
    if length == "Short":
        min_tokens = 700
        max_tokens = 1000
    elif length == "Long":
        min_tokens = 2500
        max_tokens = 4096
    
    options = [
    f'''
Tone: Casual, humorous
Lexical Choices: Contemporary, crass
Dialogue: Quotes, hypothetical
Structure: Chronological, suspenseful
Narrative Perspective: Omniscient
Pacing: Rapid
Repetition: Emphasis
Number of Words: from {min_tokens} to {max_tokens}
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
Number of Words: from {min_tokens} to {max_tokens}
    '''
    ]
    
    if option == "Casual/Humorous":
        selected_option = options[0]
    elif option == "Conversational/Educational":
        selected_option = options[1]

    sample_prompt = f"You are a professional script writer who writes a complete {length} monologue strictly according to the Context and Instructions. Video is being shot in a studio so there should be no scene making and you should also not add people's expressions in the monologue. \nInstructions:\n{selected_option}\n\n"

    prompt=sample_prompt+"Context:\n"+query

    print(prompt)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    with st.chat_message("assistant"):
        st.markdown(message.content[0].text)

st.set_page_config(
        page_title="Script Writer",
)
st.title("Script Writer")

# os.environ['GOOGLE_API_KEY'] = "AIzaSyCTVNBGUsVqG2b37HbBrruCRooYJw4dsMA"
# genai.configure(api_key = os.environ['GOOGLE_API_KEY'])

# model = genai.GenerativeModel('gemini-1.5-pro-001')

key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=key,
)

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
    st.write("\n")
    st.write("\n")
    transcribe_button = st.button("Transcribe & Generate", key="transcribe")
    option = st.selectbox("Select Script Option", ["Not Selected", "Casual/Humorous", "Conversational/Educational"], key="script_option")
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
        with st.chat_message("user"):
            st.markdown(query)
        llm_function(query, option, length)
    else:
        st.warning("Please fill in all fields before generating the script.")

if generate_button:
    with st.chat_message("user"):
        st.markdown(query)

    if generate_button:
        if query and script_option != "Not Selected" and script_length != "Not Selected":
            llm_function(query, option, length)
            transcribed_text = ""
        else:
            st.warning("Please fill in all fields before generating the script.")
