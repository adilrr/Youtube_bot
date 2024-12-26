import os
import subprocess
from yt_dlp import YoutubeDL
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import YoutubeLoader
from langchain.docstore.document import Document
from concurrent.futures import ProcessPoolExecutor, as_completed
from yt_transcript import get_transcript


def extract_text_youtube_loader(link):
    try:
        loader = YoutubeLoader.from_youtube_url(
            link,
            add_video_info=False,
            language=["en"],
            translation="en",
        )
        documents = loader.load()
        return documents[0].page_content if documents else None
    except Exception as e:
        print(f"Error extracting text using YoutubeLoader: {str(e)}")
        return None

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'verbose': True,
        'cookiesfrombrowser': ('chrome', ),  # or ('chrome', 'Profile 1') for a specific profile
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"An error occurred during download: {str(e)}")
        raise

def process_chunk(chunk_filename):
    r = sr.Recognizer()
    with sr.AudioFile(chunk_filename) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            return f"{text.capitalize()}. "
        except sr.UnknownValueError as e:
            print(f"Error in {chunk_filename}: {str(e)}")
            return ""

def transcribe_audio(path):
    sound = AudioSegment.from_wav(path)
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    
    chunk_files = []
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        chunk_files.append(chunk_filename)
    
    whole_text = ""
    with ProcessPoolExecutor() as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk_file): chunk_file for chunk_file in chunk_files}
        for future in as_completed(future_to_chunk):
            chunk_file = future_to_chunk[future]
            try:
                text = future.result()
                whole_text += text
                print(f"{chunk_file}: {text}")
            except Exception as e:
                print(f"Error processing {chunk_file}: {str(e)}")
    
    return whole_text

def extract_text_audio_method(url):
    output_path = "audio"
    print("Downloading audio...")
    download_audio(url, output_path)
    print("Transcribing audio...")
    text = transcribe_audio(output_path + ".wav")
    return text

def link_processor(link):
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # First, try to extract text using YoutubeLoader
    text = get_transcript(link)

    # If YoutubeLoader fails, use the audio method
    if not text:
        print("YoutubeLoader failed. Attempting audio transcription method...")
        text = extract_text_audio_method(link)

    if not text:
        return "Failed to extract text from the video."
    print(f"Extracted text: {text}")

    # Create a Document object with the extracted text
    documents = [Document(page_content=text)]

    template = """Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:"""

    prompt = PromptTemplate.from_template(template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

    response = stuff_chain.invoke(documents)
    return response["output_text"]

if __name__ == "__main__":
    link = input("Enter the YouTube video URL: ")
    summary = link_processor(link)
    print("\nSummary:")
    print(summary)
