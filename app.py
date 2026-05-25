import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from sarvamai import SarvamAI

SARVAM_API_KEY = ""

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)

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


def ask_sarvam(context, question):

    prompt = f"""
    You are an AI tool.

    Answer using the transcript of a YouTube video provided below.

    Transcript:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="sarvam-m",
        temperature=0.2
    )

    return response["choices"][0]["message"]["content"]


youtube_url = st.text_input("Paste YouTube Lecture URL")

if youtube_url:

    try:
        video_id = extract_video_id(youtube_url)

        st.info("Fetching transcript...")

        transcript_text = get_transcript(video_id)

        transcript_text = transcript_text[:12000]

        st.success("Transcript loaded successfully!")

        if st.button("Generate Summary"):

            summary_prompt = """
            Summarize this video in concise bullet points.
            Highlight the important points.
            """

            summary = ask_sarvam(
                transcript_text,
                summary_prompt
            )

            st.subheader("Summary")
            st.write(summary)

        if st.button("Generate Notes (for Lectures)"):

            notes_prompt = """
            Create concise exam revision notes from this lecture.
            Include important concepts and definitions.
            """

            notes = ask_sarvam(
                transcript_text,
                notes_prompt
            )

            st.subheader("Exam Notes")
            st.write(notes)

        st.subheader("Ask Questions")

        user_question = st.text_input(
            "Ask anything from the lecture"
        )

        if st.button("Ask"):

            if user_question.strip() != "":

                answer = ask_sarvam(
                    transcript_text,
                    user_question
                )

                st.subheader("Answer")
                st.write(answer)

    except Exception as e:
        st.error(f"Error: {e}")
