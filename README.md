Got it 👍 You want three modes in your Streamlit app now:

1. 🎙️ Audio/Video Upload → Azure Whisper → Summarization


2. 📰 News URL → Extract → Summarization


3. ✍️ Blog/Text Paste → Summarization



I’ll refine the Streamlit code with this third option 👇


---

🐍 Streamlit: Media, URL & Blog Summarization Agent

import streamlit as st
import openai
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_openai import AzureChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import os

# ------------------ Azure Config ------------------
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = "https://<your-resource-name>.openai.azure.com/"
openai.api_version = "2024-06-01"

# ------------------ Utility Functions ------------------
def transcribe_audio(file_path):
    """Convert audio to text using Azure Whisper."""
    with open(file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",   # Azure Whisper deployment
            file=audio_file
        )
    return transcript.text

def summarize_text(text, style="TL;DR"):
    """Summarize text using LangChain + Azure GPT."""
    llm = AzureChatOpenAI(
        openai_api_version="2024-06-01",
        azure_deployment="gpt-4o-mini",  # Replace with your Azure GPT deployment
        temperature=0
    )

    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # Add style prompt
    if style == "Bullet Points":
        text = f"Summarize into clear bullet points:\n{text}"
    elif style == "Detailed":
        text = f"Provide a detailed structured summary:\n{text}"
    else:  # TL;DR
        text = f"Give a short 3-4 line TL;DR summary:\n{text}"

    docs = [Document(page_content=text)]
    return chain.run(docs)

def summarize_audio(file, style):
    """Handle audio upload, transcription, and summarization."""
    with open("temp_audio.mp3", "wb") as f:
        f.write(file.getbuffer())
    transcript = transcribe_audio("temp_audio.mp3")
    return summarize_text(transcript, style)

def summarize_url(url, style):
    """Fetch a news/blog URL and summarize."""
    loader = UnstructuredURLLoader(urls=[url])
    docs = loader.load()
    llm = AzureChatOpenAI(
        openai_api_version="2024-06-01",
        azure_deployment="gpt-4o-mini",
        temperature=0
    )
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.run(docs)

def summarize_blog(blog_text, style):
    """Summarize directly pasted blog/article text."""
    return summarize_text(blog_text, style)

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Media, URL & Blog Summarization Agent", layout="wide")
st.title("🎙️📰✍️ Media, News & Blog Summarization Agent")
st.markdown("Upload audio/video (Azure Whisper) **or** paste a news/blog URL, **or** paste raw blog text.")

mode = st.radio(
    "Choose input type:",
    ["Audio/Video File", "News/Blog URL", "Paste Blog/Text"],
    horizontal=True
)

style = st.selectbox("Select summary style:", ["TL;DR", "Bullet Points", "Detailed"])

if mode == "Audio/Video File":
    file = st.file_uploader("Upload audio/video", type=["mp3", "wav", "mp4"])
    if file and st.button("Summarize Audio/Video"):
        with st.spinner("Processing with Azure Whisper + GPT... ⏳"):
            summary = summarize_audio(file, style)
        st.subheader("📌 Summary Result")
        st.write(summary)

elif mode == "News/Blog URL":
    url = st.text_input("Enter news or blog article URL:")
    if url and st.button("Summarize URL"):
        with st.spinner("Fetching and summarizing... ⏳"):
            summary = summarize_url(url, style)
        st.subheader("📌 Summary Result")
        st.write(summary)

elif mode == "Paste Blog/Text":
    blog_text = st.text_area("Paste blog/article text here:")
    if blog_text and st.button("Summarize Blog/Text"):
        with st.spinner("Summarizing... ⏳"):
            summary = summarize_blog(blog_text, style)
        st.subheader("📌 Summary Result")
        st.write(summary)


---

✨ Now Supports:

🎙️ Audio/Video upload → Whisper → Summarize

📰 News/Blog URL → Load → Summarize

✍️ Paste Blog/Text → Summarize directly



---

👉 Do you want me to also add an option for YouTube links (auto extract transcript + summarize)? That would make this a complete media summarizer agent.

