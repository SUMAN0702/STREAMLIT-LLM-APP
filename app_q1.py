import streamlit as st # type: ignore
import requests # type: ignore
from io import StringIO

# For reading different file types
from docx import Document # type: ignore
import PyPDF2 # type: ignore
from bs4 import BeautifulSoup # type: ignore

# ------------- Ollama helper -----------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest"

def query_ollama(prompt: str) -> str:
    """
    Send a prompt to the local Ollama server and return the full response text.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Ollama /api/generate returns "response" containing the text
        return data.get("response", "").strip()
    except Exception as e:
        return f"Error contacting local LLM: {e}"

# ------------- File reading helpers -----------------

def read_txt(file) -> str:
    return file.read().decode("utf-8", errors="ignore")

def read_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)

def read_docx(file) -> str:
    # file is a BytesIO from Streamlit
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_html(file) -> str:
    html_bytes = file.read()
    html_str = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text(separator="\n")

def extract_text_from_file(uploaded_file) -> str:
    """
    Detect file type based on extension and return extracted text.
    """
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        return read_txt(uploaded_file)
    elif filename.endswith(".pdf"):
        return read_pdf(uploaded_file)
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        return read_docx(uploaded_file)
    elif filename.endswith(".html") or filename.endswith(".htm"):
        return read_html(uploaded_file)
    else:
        return "Unsupported file type. Please upload .txt, .pdf, .docx, or .html."

# ------------- Streamlit UI -----------------

def main():
    st.set_page_config(page_title="Document QA with Local LLM", layout="centered")

    st.title("Web-based LLM App (Question 1)")
    st.write(
        """
        Ask a question and optionally upload a document.  
        The app will use your **local LLM (`llama3.2:latest` via Ollama)** and try to
        answer using the document as context.
        """
    )

    # Layout similar to common homework screenshot: left controls, right answer
    col1, col2 = st.columns(2)

    with col1:
        question = st.text_area(
            "Enter your question:",
            height=120,
            placeholder="e.g., What is the main contribution of this article?",
        )

        uploaded_file = st.file_uploader(
            "Upload an optional document",
            type=["txt", "pdf", "doc", "docx", "html", "htm"],
            help="Accepted formats: TXT, PDF, Word, HTML",
        )

        if st.button("Get Answer", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Reading document and querying local LLM..."):
                    context_text = ""
                    if uploaded_file is not None:
                        context_text = extract_text_from_file(uploaded_file)

                    # If reading failed or unsupported
                    if context_text.startswith("Unsupported file type"):
                        st.error(context_text)
                    else:
                        # Build prompt for local LLM
                        prompt = f"""You are a helpful assistant for question answering with documents.

You are given a user question and OPTIONAL document text.
Use the document **only** as supporting context.
If the document does not contain enough information, say you are not sure rather than guessing.

Document context:
-----------------
{context_text[:8000]}  # truncated if very long

-----------------
User question: {question}

Answer clearly and concisely:
"""

                        answer = query_ollama(prompt)
                        col2.write("### Answer")
                        col2.write(answer)

    # Show document preview on the right if uploaded
    with col2:
        if uploaded_file is not None:
            st.write("### Document Preview (first 2000 chars)")
            preview_text = extract_text_from_file(uploaded_file)
            st.text(preview_text[:2000])

if __name__ == "__main__":
    main()
