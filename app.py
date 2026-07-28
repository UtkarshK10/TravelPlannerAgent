import asyncio
import threading
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from travelPlannerAgent_mcp import plan_trip


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / "scripts" / ".env"
load_dotenv(ENV_PATH)


st.set_page_config(
    page_title="Travel Planner Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
    :root {
        --bg: #fbfaf7;
        --ink: #172033;
        --muted: #667085;
        --line: #e4e0d7;
        --accent: #147c72;
        --accent-2: #d97706;
        --soft: #f0f7f5;
        --panel: #ffffff;
        --shadow: 0 24px 70px rgba(23, 32, 51, 0.08);
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(251, 250, 247, 0.90), rgba(251, 250, 247, 0.98) 48%, #fbfaf7),
            url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1800&q=82");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(251, 250, 247, 0.76);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none;
    }

    .main .block-container {
        max-width: 1040px;
        padding-top: 2.35rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.2rem 0 1.35rem;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 0.8rem;
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .app-title {
        max-width: 850px;
        margin: 0 0 0.65rem;
        font-size: clamp(2.4rem, 5vw, 5rem);
        line-height: 0.96;
        font-weight: 800;
        letter-spacing: 0;
        color: var(--ink);
    }

    .app-subtitle {
        max-width: 700px;
        margin: 0;
        color: var(--muted);
        font-size: 1.06rem;
        line-height: 1.6;
    }

    .quick-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.4rem 0 1.05rem;
    }

    .chat-shell {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: var(--shadow);
        padding: 1rem 1rem 0.75rem;
    }

    .chat-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.2rem 0.15rem 0.85rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 0.85rem;
    }

    .chat-title {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--ink);
    }

    .small-muted {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.4;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 8px;
        border: 1px solid rgba(228, 224, 215, 0.9);
        background: rgba(255, 255, 255, 0.86);
        box-shadow: 0 10px 30px rgba(23, 32, 51, 0.04);
    }

    .stButton > button {
        border-radius: 8px;
        border-color: var(--line);
        min-height: 54px;
        white-space: normal;
        line-height: 1.25;
        font-weight: 700;
        color: var(--ink);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 10px 26px rgba(23, 32, 51, 0.06);
    }

    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
        background: var(--soft);
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 8px;
        border-color: var(--line);
        background: rgba(255, 255, 255, 0.98);
    }

    [data-testid="stChatInput"] {
        background: rgba(251, 250, 247, 0.88);
        backdrop-filter: blur(10px);
    }

    @media (max-width: 760px) {
        .quick-grid {
            grid-template-columns: 1fr;
        }
        .main .block-container {
            padding-top: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


EXAMPLE_PROMPTS = [
    "Romantic 5-day Mumbai trip for 2 adults",
    "Relaxed 3-day Goa beach escape",
    "Work-friendly Bengaluru trip next week",
]


def run_agent(prompt, thread_id):
    result = {"response": None, "error": None}

    def runner():
        try:
            result["response"] = asyncio.run(plan_trip(prompt, thread_id=thread_id))
        except Exception as exc:
            result["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()

    if result["error"]:
        raise result["error"]
    return result["response"]


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Tell me where you want to go, the dates, group size, vibe, and whether I should add the plan to Google Calendar.",
        }
    ]

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-session"


st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Tailored trips, beautifully planned</div>
        <h1 class="app-title">Travel Planner Agent</h1>
        <p class="app-subtitle">Describe the trip you have in mind and get a thoughtful itinerary with stays, local context, and schedule-ready details.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="quick-grid">', unsafe_allow_html=True)
cols = st.columns(3)
for index, example in enumerate(EXAMPLE_PROMPTS):
    with cols[index]:
        if st.button(example, key=f"example_{index}", use_container_width=True):
            st.session_state.pending_prompt = example
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
heading_cols = st.columns([0.78, 0.22])
with heading_cols[0]:
    st.markdown('<p class="chat-title">Trip Conversation</p>', unsafe_allow_html=True)
with heading_cols[1]:
    if st.button("New Trip", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Fresh trip board ready. Where are we heading?",
            }
        ]
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown("</div>", unsafe_allow_html=True)

prompt = st.chat_input("Ask for a trip plan, stay search, weather check, or calendar itinerary")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Planning the trip and calling tools..."):
            try:
                response = run_agent(prompt, st.session_state.thread_id)
            except Exception as exc:
                response = (
                    "I could not complete the planning run yet.\n\n"
                    f"Error: `{exc}`\n\n"
                    "Check that your `.env` keys are set, your Google OAuth JSON exists, and Node can run the MCP servers."
                )
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
