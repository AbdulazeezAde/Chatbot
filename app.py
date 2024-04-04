import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, get_text_input
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

initialize_session_state()

st.title("GreeneDesk Conversational Chatbot")

# Create container for chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Create container for text input
text_input_container = st.sidebar.container()

with text_input_container:
    user_text = get_text_input()
    if user_text:
        messages = [{"role": "user", "content": user_text}]
        response = get_answer(messages)
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": response})

# Create footer container for the microphone
footer_container = st.container()

with footer_container:
    audio_bytes = audio_recorder()

    if audio_bytes:
        # Write the audio bytes to a file
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript = speech_to_text(webm_file_path)

            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)

                os.remove(webm_file_path)

                if st.session_state.messages[-1]["role"] != "assistant":
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking🤔..."):
                            final_response = get_answer(st.session_state.messages)
                            with st.spinner("Generating audio response..."):
                                audio_file = text_to_speech(final_response)
                                autoplay_audio(audio_file)
                                st.write(final_response)
                                st.session_state.messages.append({"role": "assistant", "content": final_response})
                                os.remove(audio_file)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")

# Add some spacing between the chat container and the text input container
st.markdown("""<style>.css-1y2s5g9 {padding-bottom: 5rem;}</style>""", unsafe_allow_html=True)
