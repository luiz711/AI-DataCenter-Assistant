import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT


# ----------------------------
# Load configuration
# ----------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Please check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)


# ----------------------------
# Page configuration
# ----------------------------

st.set_page_config(
    page_title="AI Data Center Assistant",
    page_icon="🖥️",
    layout="wide",
)


# ----------------------------
# Session state
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:
    st.title("🖥️ AI Data Center")

    st.markdown("---")

    st.subheader("Quick Tools")

    st.button(
        "🔧 Server Troubleshooting",
        use_container_width=True,
    )

    st.button(
        "🖥️ Rack & Stack",
        use_container_width=True,
    )

    st.button(
        "🌐 Networking",
        use_container_width=True,
    )

    st.button(
        "🔌 Cabling",
        use_container_width=True,
    )

    st.button(
        "📄 SOP Generator",
        use_container_width=True,
    )

    st.button(
        "📋 Incident Summary",
        use_container_width=True,
    )

    st.button(
        "🎤 Interview Practice",
        use_container_width=True,
    )

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.caption("Version 0.2")


# ----------------------------
# Main page
# ----------------------------

st.title("🖥️ AI Data Center Assistant")

st.write(
    "Ask questions about servers, networking, racks, hardware, "
    "or data center operations."
)


# ----------------------------
# Display chat history
# ----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ----------------------------
# Chat input
# ----------------------------

question = st.chat_input("Ask a data center question...")

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    conversation.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = client.responses.create(
                    model="gpt-4.1",
                    input=conversation,
                )

                answer = response.output_text
                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as error:
                st.error(f"Unable to generate a response: {error}")