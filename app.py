''' import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from datetime import datetime 

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FOLDER = "chats"
os.makedirs(CHAT_FOLDER, exist_ok=True)

def save_chat(chat_name, messages):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)




def load_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
    
st.sidebar.title("Chat History")
chat_files = sorted(os.listdir(CHAT_FOLDER), reverse=True)

if st.sidebar.button("New Chat"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_name = f"chat_{timestamp}.json"
    st.session_state.chat_name = chat_name
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]
    save_chat(chat_name, st.session_state.messages)

selected_chat = st.sidebar.selectbox(
    "Previous Chats",
    [""] + chat_files
)

if selected_chat:
    if(
        "chat_name" not in st.session_state or
        st.session_state.chat_name != selected_chat
    ):
        st.session_state.chat_name = selected_chat
        st.session_state.messages = load_chat(selected_chat)

if "messages" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_name = f"chat_{timestamp}.json"
    st.session_state.chat_name = chat_name
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]
    save_chat(chat_name, st.session_state.messages)

st.title("OpenAI Chatbot")

for msg in st.session_state.messages:
    if msg['role'] == 'system':
        continue

    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

prompt = st.chat_input("Ask Something...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {
        "role": "user",
        "content": prompt
        }
    )

    with st.spinner("Generating response..."):
        response = client.responses.create(
            model = "gpt-4o-mini",
            input = st.session_state.messages
        )
        answer = response.output_text
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        save_chat(st.session_state.chat_name, st.session_state.messages) '''


import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FOLDER = "chats"
os.makedirs(CHAT_FOLDER, exist_ok=True)


# ---------------- SAVE ---------------- #

def save_chat(chat_name, messages, pinned=False):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    data = {
        "pinned": pinned,
        "messages": messages
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------------- LOAD ---------------- #

def load_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support old chat files
    if isinstance(data, list):
        return {
            "pinned": False,
            "messages": data
        }

    return data


# ---------------- NEW CHAT ---------------- #

st.sidebar.title("Chat History")

if st.sidebar.button("➕ New Chat", use_container_width=True):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_name = f"chat_{timestamp}.json"

    st.session_state.chat_name = chat_name
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]
    st.session_state.pinned = False

    save_chat(chat_name,
              st.session_state.messages,
              st.session_state.pinned)


# ---------------- LOAD CHAT LIST ---------------- #

chat_files = os.listdir(CHAT_FOLDER)

pinned_chats = []
normal_chats = []

for file in chat_files:

    chat = load_chat(file)

    if chat["pinned"]:
        pinned_chats.append(file)
    else:
        normal_chats.append(file)

pinned_chats.sort(reverse=True)
normal_chats.sort(reverse=True)


# ---------------- PINNED ---------------- #

if pinned_chats:
    st.sidebar.markdown("### 📌 Pinned")

    for chat in pinned_chats:

        col1, col2 = st.sidebar.columns([4,1])

        if col1.button(chat.replace(".json",""),
                       key=f"chat_{chat}",
                       use_container_width=True):

            data = load_chat(chat)

            st.session_state.chat_name = chat
            st.session_state.messages = data["messages"]
            st.session_state.pinned = data["pinned"]

        if col2.button("📍",
                       key=f"unpin_{chat}"):

            data = load_chat(chat)

            save_chat(
                chat,
                data["messages"],
                False
            )

            st.rerun()


# ---------------- RECENT ---------------- #

st.sidebar.markdown("### Recent Chats")

for chat in normal_chats:

    col1, col2 = st.sidebar.columns([4,1])

    if col1.button(chat.replace(".json",""),
                   key=f"recent_{chat}",
                   use_container_width=True):

        data = load_chat(chat)

        st.session_state.chat_name = chat
        st.session_state.messages = data["messages"]
        st.session_state.pinned = data["pinned"]

    if col2.button("📌",
                   key=f"pin_{chat}"):

        data = load_chat(chat)

        save_chat(
            chat,
            data["messages"],
            True
        )

        st.rerun()


# ---------------- FIRST LOAD ---------------- #

if "messages" not in st.session_state:

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_name = f"chat_{timestamp}.json"

    st.session_state.chat_name = chat_name
    st.session_state.pinned = False

    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]

    save_chat(
        chat_name,
        st.session_state.messages,
        False
    )


# ---------------- TITLE ---------------- #

st.title("OpenAI Chatbot")


# ---------------- SHOW CHAT ---------------- #

for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- INPUT ---------------- #

prompt = st.chat_input("Ask Something...")


if prompt:

    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.spinner("Generating response..."):

        response = client.responses.create(
            model="gpt-4o-mini",
            input=st.session_state.messages
        )

        answer = response.output_text

        st.chat_message("assistant").markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        save_chat(
            st.session_state.chat_name,
            st.session_state.messages,
            st.session_state.pinned
        )