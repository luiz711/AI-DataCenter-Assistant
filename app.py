import os
from pathlib import Path

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
    INTERVIEW_PRACTICE_PROMPT,
)

from utils import load_knowledge_base, search_knowledge_base
from embeddings import semantic_search_knowledge_base


# ============================================================
# LOAD CONFIGURATION
# ============================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OpenAI API key not found. Please check your .env file."
    )
    st.stop()

client = OpenAI(api_key=api_key)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Center Assistant",
    page_icon="🖥️",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        min-width: 260px;
        max-width: 260px;
    }

    .app-subtitle {
        font-size: 1.05rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "page" not in st.session_state:
    st.session_state.page = "AI Chat"

if "log_input" not in st.session_state:
    st.session_state.log_input = ""

if "troubleshoot_step" not in st.session_state:
    st.session_state.troubleshoot_step = 1

if "troubleshoot_answers" not in st.session_state:
    st.session_state.troubleshoot_answers = {}


# ============================================================
# KNOWLEDGE BASE
# ============================================================

knowledge = load_knowledge_base()

knowledge_file_count = len(
    list(
        Path("knowledge_base").glob("*.md")
    )
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🖥️ AI Data Center")

    st.markdown("---")

    st.subheader("Quick Tools")

    st.caption(
        f"Current Tool: {st.session_state.page}"
    )

    if st.button(
        "💬 AI Chat",
        use_container_width=True,
        key="nav_chat",
    ):
        st.session_state.page = "AI Chat"
        st.rerun()

    if st.button(
        "🔧 Server Troubleshooting",
        use_container_width=True,
        key="nav_server",
    ):
        st.session_state.page = "Server Troubleshooting"
        st.rerun()

    if st.button(
        "🖥️ Rack & Stack",
        use_container_width=True,
        key="nav_rack",
    ):
        st.session_state.page = "Rack & Stack"
        st.rerun()

    if st.button(
        "🌐 Networking",
        use_container_width=True,
        key="nav_networking",
    ):
        st.session_state.page = "Networking"
        st.rerun()

    if st.button(
        "🔌 Cabling",
        use_container_width=True,
        key="nav_cabling",
    ):
        st.session_state.page = "Cabling"
        st.rerun()

    if st.button(
        "📄 SOP Generator",
        use_container_width=True,
        key="nav_sop",
    ):
        st.session_state.page = "SOP Generator"
        st.rerun()

    if st.button(
        "📋 Incident Summary",
        use_container_width=True,
        key="nav_incident",
    ):
        st.session_state.page = "Incident Summary"
        st.rerun()

    if st.button(
        "📊 Log Analyzer",
        use_container_width=True,
        key="nav_logs",
    ):
        st.session_state.page = "Log Analyzer"
        st.rerun()

    if st.button(
        "🎤 Interview Practice",
        use_container_width=True,
        key="nav_interview",
    ):
        st.session_state.page = "Interview Practice"
        st.rerun()

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
        key="clear_chat",
    ):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.caption("AI Data Center Assistant")
    st.caption("Version 1.0 RC")


# ============================================================
# AI CHAT PAGE
# ============================================================

if st.session_state.page == "AI Chat":

    st.title("💬 AI Data Center Assistant")

    st.markdown(
        """
        <div class="app-subtitle">
            AI-powered troubleshooting, semantic knowledge retrieval,
            documentation support, and data center operations assistance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Status metrics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Knowledge Files",
            knowledge_file_count,
        )

    with col2:
        st.metric(
            "AI Model",
            "GPT-4.1",
        )

    with col3:
        st.metric(
            "Retrieval",
            "Semantic",
        )

    # --------------------------------------------------------
    # Capabilities
    # --------------------------------------------------------

    st.markdown("### Available Capabilities")

    tool_col1, tool_col2 = st.columns(2)

    with tool_col1:

        st.markdown(
            """
            **🔧 Troubleshooting**

            - Server diagnostics
            - Networking assistance
            - Cabling guidance
            - Rack & stack planning
            """
        )

    with tool_col2:

        st.markdown(
            """
            **📄 AI Operations Tools**

            - Log analysis
            - SOP generation
            - Incident summaries
            - Interview practice
            """
        )

    # --------------------------------------------------------
    # Knowledge base preview
    # --------------------------------------------------------

    with st.expander("📚 Knowledge Base"):
        st.text(knowledge)

    # --------------------------------------------------------
    # Previous chat history
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            if message["role"] == "assistant":

                sources = message.get(
                    "sources",
                    [],
                )

                if sources:

                    with st.expander(
                        "📚 Retrieved Sources"
                    ):

                        for source in sources:
                            st.write(
                                f"• {source}"
                            )

    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # Semantic knowledge retrieval
        # ----------------------------------------------------

        search_results = (
            semantic_search_knowledge_base(
                client,
                question,
            )
        )

        relevant_knowledge = ""

        for (
            score,
            filename,
            content,
        ) in search_results:

            relevant_knowledge += (
                f"\n\nSource: {filename}\n"
                f"{content}"
            )

        if not relevant_knowledge:

            relevant_knowledge = (
                "No relevant internal documentation "
                "was found."
            )

        retrieved_sources = [
            filename
            for (
                score,
                filename,
                content,
            ) in search_results
        ]

        # ----------------------------------------------------
        # Build conversation
        # ----------------------------------------------------

        conversation = [
            {
                "role": "system",
                "content": (
                    SYSTEM_PROMPT
                    + "\n\n"
                    + "Use the following retrieved internal "
                    + "documentation when relevant. "
                    + "Prefer the retrieved documentation "
                    + "when answering. "
                    + "If the documentation does not fully "
                    + "answer the question, say so and then "
                    + "provide general guidance."
                    + "\n\nRetrieved Knowledge:\n"
                    + relevant_knowledge
                ),
            }
        ]

        # Only send role/content to OpenAI
        for message in st.session_state.messages:

            conversation.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        # ----------------------------------------------------
        # Generate response
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner("Analyzing..."):

                try:

                    response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=conversation,
                        )
                    )

                    answer = (
                        response.output_text
                    )

                    st.markdown(answer)

                    if retrieved_sources:

                        with st.expander(
                            "📚 Retrieved Sources"
                        ):

                            for source in retrieved_sources:

                                st.write(
                                    f"• {source}"
                                )

                    else:

                        st.caption(
                            "No internal knowledge-base "
                            "sources were retrieved."
                        )

                    # Save answer + sources locally
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": retrieved_sources,
                        }
                    )

                except Exception as error:

                    st.error(
                        "Unable to generate a response: "
                        f"{error}"
                    )


# ============================================================
# LOG ANALYZER PAGE
# ============================================================

elif st.session_state.page == "Log Analyzer":

    st.title("📊 AI Log Analyzer")

    st.write(
        "Upload or paste a system log "
        "for AI-powered analysis."
    )

    uploaded_log = st.file_uploader(
        "Upload a log file",
        type=["txt", "log"],
        key="log_file_upload",
    )

    if uploaded_log is not None:

        try:

            uploaded_text = (
                uploaded_log
                .getvalue()
                .decode("utf-8")
            )

            st.session_state.log_input = (
                uploaded_text
            )

            st.success(
                f"Loaded: {uploaded_log.name}"
            )

        except UnicodeDecodeError:

            st.error(
                "This file could not be read "
                "as UTF-8 text."
            )

    log_text = st.text_area(
        "Log contents",
        height=300,
        key="log_input",
    )

    if st.button(
        "Analyze Log",
        key="analyze_log",
    ):

        if not log_text.strip():

            st.warning(
                "Please paste or upload a log "
                "before analyzing."
            )

        else:

            with st.spinner(
                "Analyzing log..."
            ):

                try:

                    log_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content":
                                    LOG_ANALYZER_PROMPT,
                                },
                                {
                                    "role": "user",
                                    "content": log_text,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        log_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to analyze the log: "
                        f"{error}"
                    )


# ============================================================
# SERVER TROUBLESHOOTING PAGE
# ============================================================

elif st.session_state.page == "Server Troubleshooting":

    st.title(
        "🔧 AI Server Troubleshooting"
    )

    st.write(
        "Work through a guided diagnostic process "
        "before generating an AI troubleshooting "
        "recommendation."
    )

    # --------------------------------------------------------
    # Step 1
    # --------------------------------------------------------

    if (
        st.session_state.troubleshoot_step
        == 1
    ):

        st.subheader(
            "Step 1: Describe the problem"
        )

        problem = st.text_area(
            "What is happening?",
            placeholder=(
                "Example: Server01 will not power on. "
                "There are no LEDs and the fans "
                "do not spin."
            ),
            height=150,
            key="troubleshoot_problem",
        )

        if st.button(
            "Continue",
            key="troubleshoot_continue_1",
        ):

            if not problem.strip():

                st.warning(
                    "Please describe the server problem."
                )

            else:

                st.session_state.troubleshoot_answers[
                    "problem"
                ] = problem

                st.session_state.troubleshoot_step = 2

                st.rerun()

    # --------------------------------------------------------
    # Step 2
    # --------------------------------------------------------

    elif (
        st.session_state.troubleshoot_step
        == 2
    ):

        st.subheader(
            "Step 2: Power status"
        )

        power_status = st.radio(
            "Does the server show any signs of power?",
            [
                "Yes",
                "No",
                "Not sure",
            ],
            key="power_status",
        )

        if st.button(
            "Continue",
            key="troubleshoot_continue_2",
        ):

            st.session_state.troubleshoot_answers[
                "power_status"
            ] = power_status

            st.session_state.troubleshoot_step = 3

            st.rerun()

    # --------------------------------------------------------
    # Step 3
    # --------------------------------------------------------

    elif (
        st.session_state.troubleshoot_step
        == 3
    ):

        st.subheader(
            "Step 3: Indicator lights"
        )

        led_status = st.radio(
            "What do the server LEDs show?",
            [
                "Normal / green",
                "Amber / warning",
                "No LEDs",
                "Unknown",
            ],
            key="led_status",
        )

        if st.button(
            "Continue",
            key="troubleshoot_continue_3",
        ):

            st.session_state.troubleshoot_answers[
                "led_status"
            ] = led_status

            st.session_state.troubleshoot_step = 4

            st.rerun()

    # --------------------------------------------------------
    # Step 4
    # --------------------------------------------------------

    elif (
        st.session_state.troubleshoot_step
        == 4
    ):

        st.subheader(
            "Step 4: Rack power"
        )

        rack_power = st.radio(
            "Do other devices in the rack have power?",
            [
                "Yes",
                "No",
                "Not sure",
            ],
            key="rack_power",
        )

        if st.button(
            "Generate Diagnosis",
            key="troubleshoot_generate",
        ):

            st.session_state.troubleshoot_answers[
                "rack_power"
            ] = rack_power

            answers = (
                st.session_state
                .troubleshoot_answers
            )

            troubleshooting_summary = f"""
Server Problem:
{answers.get("problem", "Not provided")}

Signs of Power:
{answers.get("power_status", "Not provided")}

LED Status:
{answers.get("led_status", "Not provided")}

Other Rack Equipment Has Power:
{answers.get("rack_power", "Not provided")}
"""

            search_results = (
                semantic_search_knowledge_base(
                    client,
                    troubleshooting_summary,
                )
            )

            relevant_knowledge = ""

            for (
                score,
                filename,
                content,
            ) in search_results:

                relevant_knowledge += (
                    f"\n\nSource: {filename}\n"
                    f"{content}"
                )

            if not relevant_knowledge:

                relevant_knowledge = (
                    "No relevant internal documentation "
                    "was found."
                )

            retrieved_sources = [
                filename
                for (
                    score,
                    filename,
                    content,
                ) in search_results
            ]

            with st.spinner(
                "Analyzing troubleshooting results..."
            ):

                try:

                    troubleshooting_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content": (
                                        SERVER_TROUBLESHOOTING_PROMPT
                                        + "\n\n"
                                        + "Retrieved Internal "
                                        + "Documentation:\n"
                                        + relevant_knowledge
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content":
                                    troubleshooting_summary,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        troubleshooting_response
                        .output_text
                    )

                    if retrieved_sources:

                        with st.expander(
                            "📚 Retrieved Sources"
                        ):

                            for source in retrieved_sources:

                                st.write(
                                    f"• {source}"
                                )

                except Exception as error:

                    st.error(
                        "Unable to troubleshoot the server: "
                        f"{error}"
                    )

    st.markdown("---")

    if st.button(
        "🔄 Start Over",
        key="troubleshoot_reset",
    ):

        st.session_state.troubleshoot_step = 1

        st.session_state.troubleshoot_answers = {}

        st.rerun()


# ============================================================
# RACK & STACK PAGE
# ============================================================

elif st.session_state.page == "Rack & Stack":

    st.title(
        "🖥️ AI Rack & Stack Planner"
    )

    st.write(
        "Describe the equipment you need to install "
        "and the assistant will help build a rack "
        "deployment plan."
    )

    rack_request = st.text_area(
        "Describe the rack deployment",
        placeholder=(
            "Example: Install four 2U servers, "
            "two 1U switches, and two rack PDUs "
            "in a 42U rack."
        ),
        height=180,
        key="rack_request",
    )

    if st.button(
        "Create Rack Plan",
        key="create_rack_plan",
    ):

        if not rack_request.strip():

            st.warning(
                "Please describe the rack deployment "
                "before creating a plan."
            )

        else:

            search_results = (
                semantic_search_knowledge_base(
                    client,
                    rack_request,
                )
            )

            relevant_knowledge = ""

            for (
                score,
                filename,
                content,
            ) in search_results:

                relevant_knowledge += (
                    f"\n\nSource: {filename}\n"
                    f"{content}"
                )

            if not relevant_knowledge:

                relevant_knowledge = (
                    "No relevant internal documentation "
                    "was found."
                )

            with st.spinner(
                "Building rack deployment plan..."
            ):

                try:

                    rack_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content": (
                                        RACK_STACK_PROMPT
                                        + "\n\n"
                                        + "Retrieved Internal "
                                        + "Documentation:\n"
                                        + relevant_knowledge
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": rack_request,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        rack_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to create the rack plan: "
                        f"{error}"
                    )


# ============================================================
# NETWORKING PAGE
# ============================================================

elif st.session_state.page == "Networking":

    st.title(
        "🌐 AI Networking Assistant"
    )

    st.write(
        "Describe a connectivity or network problem "
        "and the assistant will walk through a "
        "structured troubleshooting process."
    )

    network_problem = st.text_area(
        "Describe the network issue",
        placeholder=(
            "Example: Server01 can ping its own "
            "IP address but cannot ping the "
            "default gateway."
        ),
        height=180,
        key="network_problem",
    )

    if st.button(
        "Troubleshoot Network",
        key="network_troubleshoot",
    ):

        if not network_problem.strip():

            st.warning(
                "Please describe the network problem "
                "before troubleshooting."
            )

        else:

            search_results = (
                semantic_search_knowledge_base(
                    client,
                    network_problem,
                )
            )

            relevant_knowledge = ""

            for (
                score,
                filename,
                content,
            ) in search_results:

                relevant_knowledge += (
                    f"\n\nSource: {filename}\n"
                    f"{content}"
                )

            if not relevant_knowledge:

                relevant_knowledge = (
                    "No relevant internal documentation "
                    "was found."
                )

            with st.spinner(
                "Analyzing network issue..."
            ):

                try:

                    network_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content": (
                                        NETWORKING_ASSISTANT_PROMPT
                                        + "\n\n"
                                        + "Retrieved Internal "
                                        + "Documentation:\n"
                                        + relevant_knowledge
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content":
                                    network_problem,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        network_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to troubleshoot the network: "
                        f"{error}"
                    )


# ============================================================
# CABLING PAGE
# ============================================================

elif st.session_state.page == "Cabling":

    st.title(
        "🔌 AI Cabling Assistant"
    )

    st.write(
        "Describe a cabling issue or ask a question "
        "about copper, fiber, labeling, routing, "
        "or cable management."
    )

    cabling_problem = st.text_area(
        "Describe the cabling issue",
        placeholder=(
            "Example: A server has no link after "
            "a cable move. The Ethernet cable appears "
            "connected, but the NIC link light is off."
        ),
        height=180,
        key="cabling_problem",
    )

    if st.button(
        "Analyze Cabling Issue",
        key="cabling_analyze",
    ):

        if not cabling_problem.strip():

            st.warning(
                "Please describe the cabling issue "
                "before analyzing."
            )

        else:

            search_results = (
                semantic_search_knowledge_base(
                    client,
                    cabling_problem,
                )
            )

            relevant_knowledge = ""

            for (
                score,
                filename,
                content,
            ) in search_results:

                relevant_knowledge += (
                    f"\n\nSource: {filename}\n"
                    f"{content}"
                )

            if not relevant_knowledge:

                relevant_knowledge = (
                    "No relevant internal documentation "
                    "was found."
                )

            with st.spinner(
                "Analyzing cabling issue..."
            ):

                try:

                    cabling_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content": (
                                        CABLING_ASSISTANT_PROMPT
                                        + "\n\n"
                                        + "Retrieved Internal "
                                        + "Documentation:\n"
                                        + relevant_knowledge
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content":
                                    cabling_problem,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        cabling_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to analyze the cabling issue: "
                        f"{error}"
                    )


# ============================================================
# SOP GENERATOR PAGE
# ============================================================

elif st.session_state.page == "SOP Generator":

    st.title("📄 AI SOP Generator")

    st.write(
        "Describe a data center or IT procedure "
        "and the assistant will create a "
        "structured SOP draft."
    )

    sop_task = st.text_area(
        "What procedure do you need?",
        placeholder=(
            "Example: Replace a failed redundant "
            "power supply in a rack-mounted server."
        ),
        height=150,
        key="sop_task",
    )

    if st.button(
        "Generate SOP",
        key="generate_sop",
    ):

        if not sop_task.strip():

            st.warning(
                "Please enter a procedure "
                "before generating an SOP."
            )

        else:

            with st.spinner(
                "Generating SOP..."
            ):

                try:

                    sop_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content":
                                    SOP_GENERATOR_PROMPT,
                                },
                                {
                                    "role": "user",
                                    "content": sop_task,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        sop_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to generate the SOP: "
                        f"{error}"
                    )


# ============================================================
# INCIDENT SUMMARY PAGE
# ============================================================

elif st.session_state.page == "Incident Summary":

    st.title(
        "📋 AI Incident Summary"
    )

    st.write(
        "Paste incident notes, troubleshooting details, "
        "or log findings and the assistant will create "
        "a structured incident report."
    )

    incident_notes = st.text_area(
        "Incident notes",
        placeholder=(
            "Example: Server01 lost network connectivity "
            "at 14:32. Technician verified power and "
            "cabling. Switch port showed no link. "
            "Cable was replaced and connectivity "
            "was restored at 14:47."
        ),
        height=250,
        key="incident_notes",
    )

    if st.button(
        "Generate Incident Summary",
        key="generate_incident",
    ):

        if not incident_notes.strip():

            st.warning(
                "Please enter incident notes before "
                "generating a summary."
            )

        else:

            with st.spinner(
                "Creating incident summary..."
            ):

                try:

                    incident_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content":
                                    INCIDENT_SUMMARY_PROMPT,
                                },
                                {
                                    "role": "user",
                                    "content":
                                    incident_notes,
                                },
                            ],
                        )
                    )

                    st.markdown(
                        incident_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to generate the incident "
                        f"summary: {error}"
                    )


# ============================================================
# INTERVIEW PRACTICE PAGE
# ============================================================

elif st.session_state.page == "Interview Practice":

    st.title(
        "🎤 AI Interview Practice"
    )

    st.write(
        "Practice realistic data center and IT "
        "interview questions and receive feedback "
        "on your answers."
    )

    interview_question = st.selectbox(
        "Choose a practice question",
        [
            (
                "What would you check first if "
                "a server will not power on?"
            ),
            (
                "How would you troubleshoot a server "
                "with no network connectivity?"
            ),
            (
                "Explain the difference between "
                "a switch and a router."
            ),
            (
                "What is hot aisle and cold aisle "
                "containment?"
            ),
            (
                "How would you handle a damaged "
                "fiber cable?"
            ),
            (
                "What steps would you take before "
                "replacing server hardware?"
            ),
            (
                "Tell me about a time you had to "
                "troubleshoot a technical problem."
            ),
            (
                "How do you prioritize safety while "
                "working in a data center?"
            ),
        ],
        key="interview_question",
    )

    st.markdown(
        "### Interview Question"
    )

    st.info(
        interview_question
    )

    interview_answer = st.text_area(
        "Your answer",
        placeholder=(
            "Answer the question as if you were "
            "speaking directly to the interviewer."
        ),
        height=220,
        key="interview_answer",
    )

    if st.button(
        "Evaluate My Answer",
        key="evaluate_interview",
    ):

        if not interview_answer.strip():

            st.warning(
                "Please enter your answer before "
                "requesting feedback."
            )

        else:

            with st.spinner(
                "Reviewing your answer..."
            ):

                try:

                    interview_response = (
                        client.responses.create(
                            model="gpt-4.1",
                            input=[
                                {
                                    "role": "system",
                                    "content":
                                    INTERVIEW_PRACTICE_PROMPT,
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        "Interview Question:\n"
                                        f"{interview_question}"
                                        "\n\nCandidate Answer:\n"
                                        f"{interview_answer}"
                                    ),
                                },
                            ],
                        )
                    )

                    st.markdown(
                        interview_response.output_text
                    )

                except Exception as error:

                    st.error(
                        "Unable to evaluate the answer: "
                        f"{error}"
                    )