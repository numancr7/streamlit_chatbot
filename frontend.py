import streamlit as st
from backend import chatbot , retrieve_all_threads
from langchain_core.messages import HumanMessage , AIMessage , ToolMessage
import uuid

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    st.session_state['chat_titles'] = st.session_state.get('chat_titles' , {})

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable' : {'thread_id' : thread_id}})
    return state.values.get('messages', []) if state.values else []


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])

st.sidebar.title("Ali Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    chat_title = st.session_state['chat_titles'].get(str(thread_id) , f"Chat {str(thread_id)[:8]}")
    if st.sidebar.button(chat_title , key = str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg , HumanMessage):

                role = 'user'

            else:
                
                role = 'assistant'

            temp_messages.append({'role' : role , 'content' : msg.content})

        st.session_state['message_history'] = temp_messages

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    if str(st.session_state['thread_id']) not in st.session_state['chat_titles']:
        title = user_input[:30] + "..." if len(user_input) > 30 else user_input
        st.session_state['chat_titles'][str(st.session_state['thread_id'])] = title

    st.session_state['message_history'].append({'role' : 'user' , 'content' : user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # CONFIG = {'configurable' : {'thread_id' : st.session_state['thread_id']}}

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }


    # response = chatbot.invoke({'messages' : [HumanMessage(content=user_input)]} , config=CONFIG)
    # ai_message = response['messages'][-1].content

    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    st.session_state['message_history'].append({'role' : 'assistant' , 'content' : ai_message})