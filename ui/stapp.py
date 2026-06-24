"""
Healthcare AI Assistant UI

Run:

streamlit run ui/stapp.py
"""

from __future__ import annotations

import requests
import streamlit as st

# =====================================================
# CONFIGURATION
# =====================================================

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
)

# =====================================================
# SESSION STATE
# =====================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "password" not in st.session_state:
    st.session_state.password = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


# =====================================================
# HELPERS
# =====================================================

def get_auth():
    return (
        st.session_state.username,
        st.session_state.password,
    )


def check_credentials() -> bool:
    """
    Verify credentials using the
    lightweight authentication endpoint.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/auth/check",
            auth=get_auth(),
            timeout=5,
        )

        return response.status_code == 200

    except Exception:

        return False

def get_health():

    try:

        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception:
        return None


# =====================================================
# LOGIN PAGE
# =====================================================

if not st.session_state.authenticated:

    st.title("🏥 Healthcare AI Assistant")

    st.markdown(
        """
        Authenticate using your FastAPI
        HTTP Basic Authentication credentials.
        """
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        st.session_state.username = username
        st.session_state.password = password

        with st.spinner(
            "Verifying credentials..."
        ):

            if check_credentials():

                st.session_state.authenticated = True

                st.success(
                    "Authentication successful."
                )

                st.rerun()

            else:

                st.error(
                    "Invalid credentials."
                )

    st.stop()


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("System Controls")

    if st.button("Logout"):

        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.subheader("Backend Status")

    health = get_health()

    if health:

        st.success("Backend Online")

        services = (
            health.get(
                "services",
                {}
            )
        )

        for name, status in services.items():

            st.write(
                f"**{name}**"
            )

            st.code(
                str(status)
            )

    else:

        st.error(
            "Backend Offline"
        )

    st.divider()

    st.subheader(
        "Knowledge Base"
    )

    if st.button(
        "📥 Ingest Documents",
        use_container_width=True,
    ):

        with st.spinner(
            "Creating embeddings..."
        ):

            try:

                response = requests.post(
                    f"{API_BASE_URL}/ingest",
                    auth=get_auth(),
                    timeout=300,
                )

                if response.status_code == 200:

                    st.success(
                        "Documents ingested successfully."
                    )

                    st.json(
                        response.json()
                    )

                else:

                    st.error(
                        response.text
                    )

            except Exception as exc:

                st.error(str(exc))

    st.divider()

    st.subheader("Danger Zone")

    confirm_reset = st.checkbox(
        "I understand this will erase the vector database."
    )

    if st.button(
        "🗑 Reset Knowledge Base",
        use_container_width=True,
    ):

        if not confirm_reset:

            st.warning(
                "Please confirm first."
            )

        else:

            with st.spinner(
                "Resetting..."
            ):

                try:

                    response = requests.delete(
                        f"{API_BASE_URL}/reset",
                        auth=get_auth(),
                        timeout=60,
                    )

                    if response.status_code == 200:

                        st.success(
                            "Knowledge base reset."
                        )

                        st.json(
                            response.json()
                        )

                    else:

                        st.error(
                            response.text
                        )

                except Exception as exc:

                    st.error(str(exc))


# =====================================================
# MAIN PAGE
# =====================================================

st.title(
    "🏥 Healthcare AI Assistant"
)

st.caption(
    "FastAPI + ChromaDB + Phi-3 + Ollama"
)

# =====================================================
# CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =====================================================
# CHAT INPUT
# =====================================================

prompt = st.chat_input(
    "Ask a healthcare question..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message(
        "user"
    ):
        st.markdown(prompt)

    with st.chat_message(
        "assistant"
    ):

        status = st.empty()

        status.info(
            "Sending request..."
        )

        try:

            response = requests.post(
                f"{API_BASE_URL}/ask",
                auth=get_auth(),
                json={
                    "question": prompt
                },
                timeout=180,
            )

            if response.status_code != 200:

                status.error(
                    response.text
                )

            else:

                result = response.json()

                route = result.get(
                    "route",
                    "unknown"
                )

                status.success(
                    f"Processed via: {route}"
                )

                if route == "rag":

                    answer = result.get(
                        "answer",
                        "No answer generated."
                    )

                    st.markdown(answer)

                    similarity = (
                        result.get(
                            "similarity_score"
                        )
                    )

                    if similarity is not None:

                        st.caption(
                            f"Similarity Score: {similarity:.4f}"
                        )

                    sources = (
                        result.get(
                            "sources"
                        )
                    )

                    if sources:

                        with st.expander(
                            "Sources"
                        ):

                            st.json(
                                sources
                            )

                    assistant_message = (
                        answer
                    )

                else:

                    st.json(result)

                    assistant_message = (
                        str(result)
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message,
                    }
                )

        except Exception as exc:

            status.error(
                f"Error: {exc}"
            )
