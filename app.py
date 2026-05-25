import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from urllib.parse import urlparse, parse_qs

GEMINI_API_KEY = ""

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(
    page_title="YouTube Query",
    layout="wide"
)

st.title("YouTube Query Tool")

def extract_video_id(url):
    parsed_url = urlparse(url)

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]

    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed_url.query)["v"][0]

    return None


def get_transcript(video_id):
    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    full_text = " ".join([snippet.text for snippet in transcript])

    return full_text


def ask_gemini(context, question):

    prompt = f"""
    You are a helpful AI tutor.

    Answer ONLY using the transcript provided below.

    If the answer is not mentioned in the transcript,
    say:
    "This was not covered in the lecture."

    Transcript:
    {context}

    Question:
    {question}
    """

    response = model.generate_content(prompt)

    return response.text


youtube_url = st.text_input("Paste YouTube Lecture URL")

if youtube_url:

    try:
        video_id = extract_video_id(youtube_url)

        st.info("Fetching transcript...")

        transcript_text = get_transcript(video_id)

        transcript_text = transcript_text[:12000]

        st.success("Transcript loaded successfully!")

        if st.button("Generate Lecture Summary"):

            summary_prompt = """
            Summarize this lecture in concise bullet points.
            Highlight the most important concepts.
            """

            summary = ask_gemini(transcript_text, summary_prompt)

            st.subheader("📘 Lecture Summary")
            st.write(summary)

        if st.button("Generate Exam Notes"):

            notes_prompt = """
            Create concise exam revision notes from this lecture.
            Include important concepts and definitions.
            """

            notes = ask_gemini(transcript_text, notes_prompt)

            st.subheader("📝 Exam Notes")
            st.write(notes)

        st.subheader("💬 Ask Questions")

        user_question = st.text_input(
            "Ask anything from the lecture"
        )

        if st.button("Ask"):

            if user_question.strip() != "":

                answer = ask_gemini(
                    transcript_text,
                    user_question
                )

                st.subheader("Answer")
                st.write(answer)

    except Exception as e:
        st.error(f"Error: {e}")
