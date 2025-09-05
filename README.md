Got it 👍 You want a cleaner, more refined Streamlit app for your Media Content Summarization Agent.
Let’s make it structured, user-friendly, and flexible.


---

🎯 Features in Refined Version

Nice UI layout with sections.

User can choose input type: Audio/Video OR News URL.

Select summary style: TL;DR, Bullet Points, Detailed.

Summaries displayed in a formatted output.

Efficient handling (store temp files, chunk text if large).



---

🐍 Refined Streamlit Code

import streamlit as st
import whisper
import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

# ------------------ Utility Functions ------------------
def summarize_text(text, style="TL;DR"):
    """Summarize transcript or article text using LLM."""
    docs = [Document(page_content=text)]
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # Add style formatting
    if style == "Bullet Points":
        text = f"Summarize the text into clear bullet points:\n{text}"
    elif style == "Detailed":
        text = f"Provide a detailed structured summary with key themes and insights:\n{text}"
    else:  # Default TL;DR
        text = f"Give a short 3-4 line TL;DR summary:\n{text}"

    docs = [Document(page_content=text)]
    return chain.run(docs)

def summarize_audio(file, style):
    """Transcribe audio using Whisper and summarize."""
    whisper_model = whisper.load_model("base")
    result = whisper_model.transcribe(file)
    return summarize_text(result["text"], style)

def summarize_url(url, style):
    """Fetch news/article text and summarize."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = " ".join([p.get_text() for p in soup.find_all("p")])
    return summarize_text(paragraphs, style)

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Media Summarization Agent", layout="wide")
st.title("🎙️📰 Media Content Summarization Agent")
st.markdown("Upload audio/video **or** paste a news URL, and get a refined summary instantly.")

# Input type
mode = st.radio("Choose input type:", ["Audio/Video File", "News URL"], horizontal=True)

# Summary style selection
style = st.selectbox("Select summary style:", ["TL;DR", "Bullet Points", "Detailed"])

if mode == "Audio/Video File":
    file = st.file_uploader("Upload an audio/video file", type=["mp3", "wav", "mp4"])
    if file and st.button("Summarize Audio/Video"):
        with st.spinner("Transcribing and summarizing... ⏳"):
            with open("temp_audio.mp3", "wb") as f:
                f.write(file.getbuffer())
            summary = summarize_audio("temp_audio.mp3", style)
        st.subheader("📌 Summary Result")
        st.write(summary)

elif mode == "News URL":
    url = st.text_input("Enter news article URL:")
    if url and st.button("Summarize URL"):
        with st.spinner("Fetching and summarizing... ⏳"):
            summary = summarize_url(url, style)
        st.subheader("📌 Summary Result")
        st.write(summary)


---

✨ Improvements in This Version

Radio buttons & dropdowns → Clear selection of input + style.

Loading spinners → User sees progress.

Summary styles → TL;DR, Bullet Points, Detailed.

Wide layout → Better readability.

Formatted outputs → Clean, easy-to-read summaries.



---

👉 Do you want me to also add a third mode: “Paste Raw Text” (so users can just paste any transcript/article instead of uploading or URL)?

# MCP
