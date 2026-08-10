import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import (
    SYSTEM_PROMPT,
    LOG_ANALYZER_PROMPT,
    SOP_GENERATOR_PROMPT,
    INCIDENT_SUMMARY_PROMPT,
    SERVER_TROUBLESHOOTING_PROMPT,
    NETWORKING_ASSISTANT_PROMPT,
    CABLING_ASSISTANT_PROMPT,
    RACK_STACK_PROMPT,
)


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

if "page" not in st.session_state:
    st.session_state.page = "AI Chat"

if "log_input" not in st.session_state:
    st.session_state.log_input = ""


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

    if st.button(
        "💬 AI Chat",
        use_container_width=True,
    ):
        st.session_state.page = "AI Chat"

    if st.button(
        "🔧 Server Troubleshooting",
        use_container_width=True,
    ):
        st.session_state.page = "Server Troubleshooting"

    if st.button(
        "🖥️ Rack & Stack",
        use_container_width=True,
    ):
        st.session_state.page = "Rack & Stack"

    if st.button(
        "🌐 Networking",
        use_container_width=True,
    ):
        st.session_state.page = "Networking"

    if st.button(
        "🔌 Cabling",
        use_container_width=True,
    ):
        st.session_state.page = "Cabling"

    if st.button(
        "📄 SOP Generator",
        use_container_width=True,
    ):
        st.session_state.page = "SOP Generator"

    if st.button(
        "📋 Incident Summary",
        use_container_width=True,
    ):
        st.session_state.page = "Incident Summary"

    if st.button(
        "📊 Log Analyzer",
        use_container_width=True,
    ):
        st.session_state.page = "Log Analyzer"

    if st.button(
        "🎤 Interview Practice",
        use_container_width=True,
    ):
        st.session_state.page = "Interview Practice"

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.caption("Version 0.3")


# ----------------------------
# AI Chat Page
# ----------------------------

if st.session_state.page == "AI Chat":

    st.title("💬 AI Data Center Assistant")

    st.write(
        "Ask questions about servers, networking, racks, hardware, "
        "or data center operations."
    )

    with st.expander("📚 Knowledge Base"):
        st.text(knowledge)

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    question = st.chat_input(
        "Ask a data center question...",
        key="main_chat_input",
    )

    if question:

        # Save user's message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        # Display user's message
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
        # Build conversation
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
        # Generate AI response
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


# ----------------------------
# Log Analyzer Page
# ----------------------------

elif st.session_state.page == "Log Analyzer":

    st.title("📊 AI Log Analyzer")

    st.write(
        "Upload or paste a system log for AI-powered analysis."
    )

    uploaded_log = st.file_uploader(
        "Upload a log file",
        type=["txt", "log"],
        key="log_file_upload",
    )

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
        height=300,
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

                    st.markdown(
                        log_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to analyze the log: {error}"
                    )


# ----------------------------
# Server Troubleshooting Page
# ----------------------------

elif st.session_state.page == "Server Troubleshooting":

    st.title("🔧 AI Server Troubleshooting")

    st.write(
        "Describe a server problem and the assistant will help you "
        "work through a structured troubleshooting process."
    )

    server_problem = st.text_area(
        "Describe the server issue",
        placeholder=(
            "Example: Server powers on, but there is no network connectivity. "
            "The link light on NIC 1 is off."
        ),
        height=180,
        key="server_problem",
    )

    if st.button("Troubleshoot Server"):

        if not server_problem.strip():
            st.warning(
                "Please describe the server problem before troubleshooting."
            )

        else:

            # Search your internal knowledge base
            search_results = search_knowledge_base(server_problem)

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

            with st.spinner("Analyzing server issue..."):

                try:
                    troubleshooting_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": (
                                    SERVER_TROUBLESHOOTING_PROMPT
                                    + "\n\n"
                                    + "Retrieved Internal Documentation:\n"
                                    + relevant_knowledge
                                ),
                            },
                            {
                                "role": "user",
                                "content": server_problem,
                            },
                        ],
                    )

                    st.markdown(
                        troubleshooting_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to troubleshoot the server: {error}"
                    )


# ----------------------------
# Rack & Stack Page
# ----------------------------

elif st.session_state.page == "Rack & Stack":

    st.title("🖥️ AI Rack & Stack Planner")

    st.write(
        "Describe the equipment you need to install and the assistant "
        "will help build a rack deployment plan."
    )

    rack_request = st.text_area(
        "Describe the rack deployment",
        placeholder=(
            "Example: Install four 2U servers, two 1U switches, "
            "and two rack PDUs in a 42U rack."
        ),
        height=180,
        key="rack_request",
    )

    if st.button("Create Rack Plan"):

        if not rack_request.strip():
            st.warning(
                "Please describe the rack deployment before creating a plan."
            )

        else:

            search_results = search_knowledge_base(rack_request)

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

            with st.spinner("Building rack deployment plan..."):

                try:
                    rack_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": (
                                    RACK_STACK_PROMPT
                                    + "\n\n"
                                    + "Retrieved Internal Documentation:\n"
                                    + relevant_knowledge
                                ),
                            },
                            {
                                "role": "user",
                                "content": rack_request,
                            },
                        ],
                    )

                    st.markdown(
                        rack_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to create the rack plan: {error}"
                    )


# ----------------------------
# Networking Page
# ----------------------------
elif st.session_state.page == "Networking":

    st.title("🌐 AI Networking Assistant")

    st.write(
        "Describe a connectivity or network problem and the assistant "
        "will walk through a structured troubleshooting process."
    )

    network_problem = st.text_area(
        "Describe the network issue",
        placeholder=(
            "Example: Server01 can ping its own IP address but cannot "
            "ping the default gateway."
        ),
        height=180,
        key="network_problem",
    )

    if st.button("Troubleshoot Network"):

        if not network_problem.strip():
            st.warning(
                "Please describe the network problem before troubleshooting."
            )

        else:

            search_results = search_knowledge_base(network_problem)

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

            with st.spinner("Analyzing network issue..."):

                try:
                    network_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": (
                                    NETWORKING_ASSISTANT_PROMPT
                                    + "\n\n"
                                    + "Retrieved Internal Documentation:\n"
                                    + relevant_knowledge
                                ),
                            },
                            {
                                "role": "user",
                                "content": network_problem,
                            },
                        ],
                    )

                    st.markdown(
                        network_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to troubleshoot the network: {error}"
                    )


# ----------------------------
# Cabling Page
# ----------------------------

elif st.session_state.page == "Cabling":

    st.title("🔌 AI Cabling Assistant")

    st.write(
        "Describe a cabling issue or ask a question about copper, fiber, "
        "labeling, routing, or cable management."
    )

    cabling_problem = st.text_area(
        "Describe the cabling issue",
        placeholder=(
            "Example: A server has no link after a cable move. "
            "The Ethernet cable appears connected, but the NIC link light is off."
        ),
        height=180,
        key="cabling_problem",
    )

    if st.button("Analyze Cabling Issue"):

        if not cabling_problem.strip():
            st.warning(
                "Please describe the cabling issue before analyzing."
            )

        else:

            search_results = search_knowledge_base(cabling_problem)

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

            with st.spinner("Analyzing cabling issue..."):

                try:
                    cabling_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": (
                                    CABLING_ASSISTANT_PROMPT
                                    + "\n\n"
                                    + "Retrieved Internal Documentation:\n"
                                    + relevant_knowledge
                                ),
                            },
                            {
                                "role": "user",
                                "content": cabling_problem,
                            },
                        ],
                    )

                    st.markdown(
                        cabling_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to analyze the cabling issue: {error}"
                    )


# ----------------------------
# SOP Generator Page
# ----------------------------

elif st.session_state.page == "SOP Generator":

    st.title("📄 AI SOP Generator")

    st.write(
        "Describe a data center or IT procedure and the assistant "
        "will create a structured SOP draft."
    )

    sop_task = st.text_area(
        "What procedure do you need?",
        placeholder=(
            "Example: Replace a failed redundant power supply "
            "in a rack-mounted server."
        ),
        height=150,
        key="sop_task",
    )

    if st.button(
        "Generate SOP",
        use_container_width=False,
    ):

        if not sop_task.strip():
            st.warning(
                "Please enter a procedure before generating an SOP."
            )

        else:

            with st.spinner("Generating SOP..."):

                try:
                    sop_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": SOP_GENERATOR_PROMPT,
                            },
                            {
                                "role": "user",
                                "content": sop_task,
                            },
                        ],
                    )

                    st.markdown(sop_response.output_text)

                except Exception as error:
                    st.error(
                        f"Unable to generate the SOP: {error}"
                    )


# ----------------------------
# Incident Summary Page
# ----------------------------

elif st.session_state.page == "Incident Summary":

    st.title("📋 AI Incident Summary")

    st.write(
        "Paste incident notes, troubleshooting details, or log findings "
        "and the assistant will create a structured incident report."
    )

    incident_notes = st.text_area(
        "Incident notes",
        placeholder=(
            "Example: Server01 lost network connectivity at 14:32. "
            "Technician verified power and cabling. Switch port showed "
            "no link. Cable was replaced and connectivity was restored "
            "at 14:47."
        ),
        height=250,
        key="incident_notes",
    )

    if st.button("Generate Incident Summary"):

        if not incident_notes.strip():
            st.warning(
                "Please enter incident notes before generating a summary."
            )

        else:
            with st.spinner("Creating incident summary..."):

                try:
                    incident_response = client.responses.create(
                        model="gpt-4.1",
                        input=[
                            {
                                "role": "system",
                                "content": INCIDENT_SUMMARY_PROMPT,
                            },
                            {
                                "role": "user",
                                "content": incident_notes,
                            },
                        ],
                    )

                    st.markdown(
                        incident_response.output_text
                    )

                except Exception as error:
                    st.error(
                        f"Unable to generate the incident summary: {error}"
                    )


# ----------------------------
# Interview Practice Page
# ----------------------------

elif st.session_state.page == "Interview Practice":

    st.title("🎤 Interview Practice")

    st.info(
        "This tool is coming soon."
    )