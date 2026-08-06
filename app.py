import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Please check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="AI Data Center Assistant",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ AI Data Center Assistant")

st.write(
    "Ask questions about servers, networking, racks, hardware, "
    "or data center operations."
)

question = st.text_area(
    "Ask a question",
    height=150,
)

if st.button("Ask AI"):

    if question.strip() == "":
        st.warning("Please enter a question.")
    else:

        with st.spinner("Thinking..."):

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
            )

        st.markdown(response.output_text)