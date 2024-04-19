from openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
import base64
import streamlit as st

load_dotenv()
api_key = os.getenv("openai_api_key")

client = OpenAI(api_key=api_key)

def get_text_input():
    user_input = st.text_input("Enter your question or message:")
    return user_input

def create_vector_store(pdf_files):
    loaders = [PyPDFLoader(file) for file in pdf_files]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    return vector_store

def get_conversation_chain(vector_store):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0, openai_api_key=api_key)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vector_store.as_retriever(), memory=memory)
    return conversation_chain


def get_answer(messages):
    system_message = {"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by users about Swim Schools."}
    messages.append(system_message)
    user_question = messages[-2]["content"]
    response = conversation_chain({"question": user_question, "chat_history": messages})
    memory = conversation_chain.memory
    if isinstance(memory, ConversationBufferMemory):
        memory.clear()
    return response["answer"]


def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    max_length = 4096
    if len(input_text) > max_length:
        input_text = textwrap.shorten(input_text, max_length, placeholder="...")
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=str(input_text)
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

pdf_files = [
    "CGC-Aquatics-Programs-Parent-Handbook.pdf",
    "client-handbook-recreation.pdf",
    "curriculum_swimming_and_water_safety-a_guide_for_parents.pdf",
    "dipadees_learntoswim_infobk.pdf",
    "LTS flyer Term 3 2015.pdf",
    "National-Swimming-and-Water-Safety-Framework_FINAL-2020.pdf",
    "Parent Handbook.pdf",
    "ssa_info_book.pdf",
    "Swim+School+-+Parents+Handbook-lowres-web.pdf",
    "Swimming Lessons Level Progression Chart _ The Y.pdf",
    "Swim-Lessons-Parent-Handbook_r4.pdf",
    "WIRAC LTS Timetable.pdf",
    "Y NSW Swim School Program - Terms and Conditions _ The Y.pdf",
    "YMCA Swim Lesson Level Guide.pdf",
    "YMCA-Swim-School-Brochure.pdf",
   ]
vector_store = create_vector_store(pdf_files)
conversation_chain = get_conversation_chain(vector_store)
