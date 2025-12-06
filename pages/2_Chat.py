import streamlit as st
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

st.set_page_config(page_title="MindCare AI Chat", layout="wide")

# Redirect if not logged in
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

CHAT_DB = "chat_history.json"

# Chat DB create (NOT for guest)
if not os.path.exists(CHAT_DB):
    with open(CHAT_DB, "w") as f:
        json.dump({}, f)


def load_chats():
    with open(CHAT_DB, "r") as f:
        return json.load(f)


def save_chats(data):
    with open(CHAT_DB, "w") as f:
        json.dump(data, f, indent=4)


def ask_ai(msg):
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        result = model.generate_content(msg)
        return result.text
    except Exception as e:
        return f"⚠️ Error: {e}"


user = st.session_state["user"]

# -------- GUEST MODE (NO SAVE) --------
if user == "guest":
    if "guest_messages" not in st.session_state:
        st.session_state["guest_messages"] = []

    st.title("🧘 MindCare AI — Guest Mode")

    # Show messages
    for msg in st.session_state["guest_messages"]:
        if msg["role"] == "user":
            st.markdown(f"🧍 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **AI:** {msg['content']}")

    st.markdown("### How are you feeling today?")
    emojis = ["😊", "😢", "😡", "😴", "😟"]
    cols = st.columns(5)

    for emoji, col in zip(emojis, cols):
        if col.button(emoji):
            st.session_state["guest_messages"].append({"role": "user", "content": emoji})
            ai_reply = ask_ai(emoji)
            st.session_state["guest_messages"].append({"role": "assistant", "content": ai_reply})
            st.rerun()

    user_input = st.text_input("Type your message...")

    if st.button("Send"):
        if user_input.strip():
            st.session_state["guest_messages"].append({"role": "user", "content": user_input})
            ai_reply = ask_ai(user_input)
            st.session_state["guest_messages"].append({"role": "assistant", "content": ai_reply})
            st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/1_Login.py")

    st.stop()

# -------- LOGGED IN USERS (SAVE CHAT) --------

all_chats = load_chats()
if user not in all_chats:
    all_chats[user] = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

# Ensure chat exists
if st.session_state.current_chat not in all_chats[user]:
    all_chats[user][st.session_state.current_chat] = []
    save_chats(all_chats)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("📚 Your Chats")

    # Chat list
    for chat_title in list(all_chats[user].keys()):
        if st.button(chat_title):
            st.session_state.current_chat = chat_title
            st.rerun()

    st.markdown("---")

    # New chat button
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(all_chats[user]) + 1}"
        all_chats[user][new_name] = []
        st.session_state.current_chat = new_name
        save_chats(all_chats)
        st.rerun()

    # Rename chat
    st.subheader("✏️ Rename Chat")
    new_name = st.text_input("Enter new name")

    if st.button("Rename"):
        old = st.session_state.current_chat
        if new_name.strip():
            all_chats[user][new_name] = all_chats[user].pop(old)
            st.session_state.current_chat = new_name
            save_chats(all_chats)
            st.success("Renamed successfully!")
            st.rerun()

    # Delete chat
    st.subheader("🗑️ Delete Chat")
    if st.button("Delete This Chat"):
        current = st.session_state.current_chat
        if current in all_chats[user]:
            all_chats[user].pop(current)
            save_chats(all_chats)

            # Move to new empty chat
            st.session_state.current_chat = "New Chat"
            if "New Chat" not in all_chats[user]:
                all_chats[user]["New Chat"] = []
                save_chats(all_chats)

            st.success("Chat deleted.")
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/1_Login.py")

# ---------------- MAIN UI ----------------

st.title("🧘 MindCare AI — Your Companion 🌿")

current_chat = st.session_state.current_chat
st.subheader(f"Chat: **{current_chat}**")

messages = all_chats[user][current_chat]

# Show messages
for msg in messages:
    role, content = msg["role"], msg["content"]
    if role == "user":
        st.markdown(f"🧍 **You:** {content}")
    else:
        st.markdown(f"🤖 **AI:** {content}")

# Emoji mood buttons
st.markdown("### How are you feeling right now?")
moods = ["😊", "😢", "😡", "😴", "😟"]
cols = st.columns(5)

for mood, col in zip(moods, cols):
    if col.button(mood):
        messages.append({"role": "user", "content": mood})
        ai_reply = ask_ai(mood)
        messages.append({"role": "assistant", "content": ai_reply})
        save_chats(all_chats)
        st.rerun()

# Input box
user_input = st.text_input("Type your message...")

if st.button("Send"):
    if user_input.strip():
        messages.append({"role": "user", "content": user_input})
        save_chats(all_chats)

        with st.spinner("Thinking..."):
            ai_reply = ask_ai(user_input)

        messages.append({"role": "assistant", "content": ai_reply})
        save_chats(all_chats)

        st.rerun()
