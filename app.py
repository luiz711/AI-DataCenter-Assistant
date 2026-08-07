import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, LOG_ANALYZER_PROMPT
from utils import load_knowledge_base, search_knowledge_base

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
# Load knowledge base
# ----------------------------

knowledge = load_knowledge_base()


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
        "📊 Log Analyzer",
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
# Knowledge base preview
# ----------------------------

with st.expander("📚 Knowledge Base"):
    st.text(knowledge)


# ----------------------------
# Display chat history
# ----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ----------------------------
# Log Analyzer
# ----------------------------

with st.expander("📊 AI Log Analyzer"):

    st.write(
        "Paste a log or upload a .txt/.log file for AI analysis."
    )

    uploaded_log = st.file_uploader(
        "Upload a log file",
        type=["txt", "log"],
    )

    if "log_input" not in st.session_state:
        st.session_state.log_input = ""

    if uploaded_log is not None:
        try:
            uploaded_text = uploaded_log.getvalue().decode("utf-8")

            st.session_state.log_input = uploaded_text

            st.success(
                f"Loaded: {uploaded_log.name}"
            )

        except UnicodeDecodeError:
            st.error(
                "This file could not be read as UTF-8 text."
            )

    log_text = st.text_area(
        "Log contents",
        height=200,
        key="log_input",
    )

    if st.button("Analyze Log"):

        if not log_text.strip():
            st.warning(
                "Please paste or upload a log before analyzing."
            )

        else:
            with st.spinner("Analyzing log..."):

                try:
                    log_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": LOG_ANALYZER_PROMPT,
                            },
                            {
                                "role": "user",
                                "content": log_text,
                            },
                        ],
                    )

                    st.markdown(log_response.output_text)

                except Exception as error:
                    st.error(
                        f"Unable to analyze the log: {error}"
                    )


# ----------------------------
# Chat input
# ----------------------------

question = st.chat_input("Ask a data center question...")

if question:

    # Save the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Display the user's message
    with st.chat_message("user"):
        st.markdown(question)

    # ----------------------------
    # Search knowledge base
    # ----------------------------

    search_results = search_knowledge_base(question)

    relevant_knowledge = ""

    for score, filename, content in search_results:
        relevant_knowledge += (
            f"\n\nSource: {filename}\n"
            f"{content}"
        )

    if not relevant_knowledge:
        relevant_knowledge = (
            "No relevant internal documentation was found."
        )

    # ----------------------------
    # Build the conversation
    # ----------------------------

    conversation = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + "\n\n"
                + "Use the following retrieved internal documentation "
                + "when relevant. "
                + "Prefer the retrieved documentation when answering. "
                + "If the retrieved documentation does not fully answer "
                + "the question, say so and then provide general guidance."
                + "\n\nRetrieved Knowledge:\n"
                + relevant_knowledge
            ),
        }
    ]

    conversation.extend(st.session_state.messages)

    # ----------------------------
    # Generate the AI response
    # ----------------------------

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
                st.error(
                    f"Unable to generate a response: {error}"
                )