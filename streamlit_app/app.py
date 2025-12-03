import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="CampusAI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 50rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #0e1617;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .chat-input {
        position: fixed;
        bottom: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Title and description
st.markdown('<p class="main-header">🎓 CampusAI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your AI-powered guide for freshers on campus</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About CampusAI")
    st.info("""
    **CampusAI Assistant** helps freshers navigate campus life by answering common questions about:
    
    ✅ School fees payment  
    ✅ Clearance process  
    ✅ Finding lecture halls  
    ✅ Joining group chats  
    ✅ Department locations  
    ✅ Student ID cards  
    ✅ And much more!
    """)
    
    st.markdown("---")
    
    # Quick tips
    st.header("💡 Quick Tips")
    with st.expander("View Tips"):
        try:
            tips_response = requests.get(f"{API_URL}/chat/tips", timeout=5)
            if tips_response.status_code == 200:
                tips_data = tips_response.json()
                for i, tip in enumerate(tips_data.get("tips", [])[:5], 1):
                    st.write(f"{i}. {tip}")
        except:
            st.write("• Check your Gmail daily")
            st.write("• Join your dept group chat")
            st.write("• Save your MSRC contact")
    
    st.markdown("---")
    
    # System status
    st.header("🔧 System Status")
    if st.button("Check Status", use_container_width=True):
        with st.spinner("Checking..."):
            try:
                health = requests.get(f"{API_URL}/health", timeout=5)
                if health.status_code == 200:
                    data = health.json()
                    st.success("✅ System Online")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("API Status", "🟢 Active")
                    with col2:
                        node_status = "🟢 Connected" if data.get("node_service_connected") else "🔴 Disconnected"
                        st.metric("Node Service", node_status)
                else:
                    st.error("❌ System Error")
            except Exception as e:
                st.error(f"❌ Cannot connect to backend\n{str(e)}")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("Built with ❤️ for FUTO Freshers")
    st.caption(f"© {datetime.now().year} CampusAI")
    st.caption("Dev Enyinnaya")

# Main chat interface
st.header("💬 Ask Me Anything!")

# Quick action buttons
st.markdown("### 🚀 Quick Questions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💰 School Fees", use_container_width=True):
        st.session_state.pending_prompt = "How do I pay school fees?"
        st.rerun()

with col2:
    if st.button("📝 Clearance", use_container_width=True):
        st.session_state.pending_prompt = "Where do I do clearance?"
        st.rerun()

with col3:
    if st.button("📚 Timetable", use_container_width=True):
        st.session_state.pending_prompt = "How do I get my timetable?"
        st.rerun()

with col4:
    if st.button("👥 Group Chat", use_container_width=True):
        st.session_state.pending_prompt = "How do I join my department group chat?"
        st.rerun()
        
# Handle quick-button prompt
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Now trigger the same API request as below
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                request_data = {"question": prompt}

                if st.session_state.conversation_id:
                    request_data["conversation_id"] = st.session_state.conversation_id

                response = requests.post(f"{API_URL}/chat/ask", json=request_data, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    related_topics = data.get("related_topics", [])
                    conversation_id = data.get("conversation_id")

                    if conversation_id:
                        st.session_state.conversation_id = conversation_id

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "related": related_topics
                    })
                else:
                    st.error("Error processing your question.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

st.markdown("---")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "related" in message:
                if message["related"]:
                    st.caption(f"💡 Related topics: {', '.join(message['related'])}")

# Chat input
if prompt := st.chat_input("Ask about campus life... (e.g., 'What is MSRC?')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare request
                request_data = {
                    "question": prompt
                }
                
                # Add conversation_id if exists
                if st.session_state.conversation_id:
                    request_data["conversation_id"] = st.session_state.conversation_id
                
                # Make API call
                response = requests.post(
                    f"{API_URL}/chat/ask",
                    json=request_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    source = data.get("source", "CampusAI")
                    conversation_id = data.get("conversation_id")
                    related_topics = data.get("related_topics", [])
                    
                    # Store conversation ID for follow-ups
                    if conversation_id:
                        st.session_state.conversation_id = conversation_id
                    
                    # Display answer
                    st.markdown(answer)
                    st.caption(f"📚 Source: {source}")
                    
                    # Show related topics
                    if related_topics:
                        st.caption(f"💡 Related topics: {', '.join(related_topics)}")
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "related": related_topics
                    })
                else:
                    error_msg = "Sorry, I couldn't process that question. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "related": []
                    })
                    
            except requests.exceptions.ConnectionError:
                error_msg = "❌ Cannot connect to the backend server. Make sure the FastAPI server is running on port 8000."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "related": []
                })
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "related": []
                })

# Info section at bottom
st.markdown("---")
with st.expander("ℹ️ How to use CampusAI Assistant"):
    st.markdown("""
    **Getting Started:**
    1. Type your question in the chat box below
    2. Press Enter or click the send button
    3. Get instant answers about FUTO campus life!
    
    **Tips for better answers:**
    - Be specific with your questions
    - Use keywords like "fees", "clearance", "timetable", "MSRC"
    - Ask follow-up questions naturally
    - Use the quick question buttons for common queries
    
    **Example questions:**
    - "How do I pay my school fees?"
    - "Where is the ICT building?"
    - "What does MSRC mean?"
    - "How do I get my timetable?"
    - "Where do I do clearance?"
    """)

# Statistics (optional)
if st.session_state.messages:
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Session Stats")
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.sidebar.metric("Questions Asked", user_messages)
    st.sidebar.metric("Total Messages", total_messages)