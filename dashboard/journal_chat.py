#!/usr/bin/env python3
"""
Journal Chat Interface
Chat with your journal entries using RAG and local LLM
"""

import streamlit as st
from pathlib import Path
import sys

# Page config
st.set_page_config(
    page_title="Journal Chat",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Chat with Your Journals")

st.markdown("""
Ask questions about your journal entries and get AI-powered answers based on what you've written.
The system searches your journals and optionally uses a local LLM to provide insights.
""")

# Sidebar configuration
st.sidebar.header("Configuration")

rag_db_path = st.sidebar.text_input(
    "RAG Database Path",
    value="../rag/vector_db",
    help="Path to your RAG vector database"
)

# Check if database exists
db_path = Path(rag_db_path)
if not db_path.exists():
    st.warning("⚠️ RAG database not found!")
    st.info("""
    **To get started:**
    1. Make sure you've processed your journal photos with OCR
    2. Run ingestion: `python ../rag/journal_rag.py ingest ../ocr/ocr_output`
    3. Or use the dashboard's "📥 Ingest to RAG" button
    4. Refresh this page
    """)
    st.stop()

# LLM configuration
st.sidebar.header("LLM Settings")

use_llm = st.sidebar.checkbox(
    "Use LLM for answers",
    value=False,
    help="Enable AI-generated answers (requires Ollama installed and running)"
)

llm_model = "llama3.3"
if use_llm:
    llm_model = st.sidebar.selectbox(
        "LLM Model",
        ["llama3.3", "mistral", "llama2"],
        help="Choose which Ollama model to use"
    )
    
    st.sidebar.info("""
    **LLM Mode**: AI reads relevant journal entries and generates personalized answers.
    
    **Search-only Mode**: Shows relevant journal excerpts without AI interpretation.
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources if available
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**{i}. Entry from {source['date']}**")
                    st.text(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask a question about your journals..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching your journals..."):
            try:
                # Import RAG system
                sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
                from journal_rag import JournalRAG, OllamaLLM
                
                # Search for relevant entries
                rag = JournalRAG(db_path=rag_db_path)
                results = rag.search(prompt, n_results=3)
                
                if not results:
                    response = "❌ I couldn't find any relevant journal entries for that question. Try rephrasing or asking about different topics."
                    sources = []
                
                elif use_llm:
                    # Use LLM to generate answer
                    try:
                        with st.spinner("Generating answer with AI..."):
                            llm = OllamaLLM(model=llm_model)
                            context = [r['text'] for r in results]
                            response = llm.generate(prompt, context)
                        sources = results
                    except ConnectionError as e:
                        response = f"❌ Could not connect to Ollama. Make sure it's installed and running.\n\nError: {e}\n\nHere are the relevant entries I found:"
                        sources = results
                    except Exception as e:
                        response = f"❌ LLM error: {e}\n\nHere are the relevant entries I found instead:"
                        sources = results
                
                else:
                    # Just show search results without LLM
                    response = "📚 Here are the most relevant journal entries I found:"
                    sources = results
                
                # Display response
                st.markdown(response)
                
                # Display sources
                if sources:
                    with st.expander("📚 View Sources", expanded=(not use_llm)):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**{i}. Entry from {source['date']}**")
                            st.text(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))
                            st.divider()
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })
                
            except FileNotFoundError:
                error_msg = "❌ RAG database not found. Please ingest your journal entries first."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })

# Sidebar actions
st.sidebar.header("Actions")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Example questions
with st.sidebar.expander("💡 Example Questions"):
    st.markdown("""
    - What was I worried about last week?
    - When did I last mention [person's name]?
    - What patterns do I see in my anxiety?
    - What made me happy this month?
    - How have I been sleeping lately?
    - What goals did I set recently?
    """)

# Stats
st.sidebar.header("Statistics")
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
    from journal_rag import JournalRAG
    rag = JournalRAG(db_path=rag_db_path)
    stats = rag.get_stats()
    
    st.sidebar.metric("Total Entries", stats['total_entries'])
    st.sidebar.metric("Total Words", f"{stats['total_words']:,}")
    if stats['date_range']['first']:
        st.sidebar.text(f"Date Range:")
        st.sidebar.text(f"{stats['date_range']['first']}")
        st.sidebar.text(f"to")
        st.sidebar.text(f"{stats['date_range']['last']}")
except:
    pass


if __name__ == "__main__":
    pass  # Streamlit handles execution
