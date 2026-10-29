"""Streamlit UI for DocChat. Talks to the FastAPI backend over HTTP.

Run: streamlit run app.py
"""

import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="DocChat", page_icon="📄")
st.title("📄 DocChat")
st.caption("Ask questions about your PDFs. Answers cite the page they came from.")

with st.sidebar:
    st.header("Documents")
    upload = st.file_uploader("Upload a PDF", type="pdf")
    if upload and st.button("Ingest", use_container_width=True):
        with st.spinner("Chunking and embedding..."):
            response = requests.post(
                f"{API_URL}/documents",
                files={"file": (upload.name, upload.getvalue(), "application/pdf")},
            )
        if response.ok:
            st.success(f"Ingested {upload.name}")
        else:
            st.error(response.text)

    for doc in requests.get(f"{API_URL}/documents").json():
        st.write(f"**{doc['filename']}** · {doc['chunks']} chunks")

    k = st.slider("Chunks to retrieve (k)", 1, 10, 5)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            st.caption(f"{source['filename']} p.{source['page']} · similarity {source['similarity']}")

if question := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            result = requests.post(f"{API_URL}/ask", json={"question": question, "k": k}).json()
        st.markdown(result["answer"])
        for source in result["sources"]:
            st.caption(f"{source['filename']} p.{source['page']} · similarity {source['similarity']}")

    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "sources": result["sources"]}
    )
