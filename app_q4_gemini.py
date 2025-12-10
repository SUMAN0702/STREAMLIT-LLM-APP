import os
from io import BytesIO

import streamlit as st # type: ignore

from docx import Document # type: ignore
import PyPDF2 # type: ignore
from bs4 import BeautifulSoup # type: ignore

# Gemini SDK
from google import genai


# ------------- Gemini client setup -------------

# The client will read GEMINI_API_KEY from the environment if not passed explicitly.
# Recommended: set GEMINI_API_KEY in your environment before running.
# Docs: https://ai.google.dev/gemini-api/docs/quickstart
client = genai.Client()  # uses GEMINI_API_KEY env var


def query_gemini(prompt: str,
                 model: str = "gemini-2.5-flash") -> str:
    """
    Send a prompt to the Gemini API and return the response text.
    Handles common transient errors more gracefully.
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return (response.text or "").strip()

    except Exception as e:
        # Convert exception to string to inspect
        msg = str(e)

        # Handle overloaded / 503-style messages
        if "503" in msg or "UNAVAILABLE" in msg or "overloaded" in msg:
            return (
                "The Gemini model is temporarily overloaded and returned 503 UNAVAILABLE.\n"
                "This is a server-side issue from Google. Please wait a bit and try again, "
                "or try using a different Gemini model name in the code."
            )

        # Generic fallback
        return f"Error calling Gemini API: {e}"



# ------------- File reading helpers -------------

def read_txt_bytes(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def read_pdf_bytes(data: bytes) -> str:
    pdf_file = BytesIO(data)
    reader = PyPDF2.PdfReader(pdf_file)
    text_pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_pages.append(page_text)
    return "\n".join(text_pages)


def read_docx_bytes(data: bytes) -> str:
    doc_file = BytesIO(data)
    doc = Document(doc_file)
    return "\n".join(p.text for p in doc.paragraphs)


def read_html_bytes(data: bytes) -> str:
    html_str = data.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text(separator="\n")


def extract_text_from_file(uploaded_file) -> str:
    """
    Detect file type based on extension and return extracted text.
    Reads the uploaded file once into memory (bytes) so we can
    safely pass it to different parsers.
    """
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()
    data = uploaded_file.read()  # bytes

    if filename.endswith(".txt"):
        return read_txt_bytes(data)
    elif filename.endswith(".pdf"):
        return read_pdf_bytes(data)
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        return read_docx_bytes(data)
    elif filename.endswith(".html") or filename.endswith(".htm"):
        return read_html_bytes(data)
    else:
        return "Unsupported file type. Please upload .txt, .pdf, .docx, or .html."


# ------------- Streamlit UI (Q1 app, Gemini backend) -------------

def main():
    st.set_page_config(page_title="Web-based LLM App (Gemini)", layout="centered")

    st.title("Web-based LLM App – Question 4 (Gemini API)")

    st.write(
        """
This is the **Question 1 app rebuilt with a closed-source LLM (Google Gemini)**.

- Enter a question.
- Optionally upload a document (TXT, PDF, Word, HTML).
- The app will use the **Gemini API** to answer using the document as context.
        """
    )

    # Main layout: left (inputs) and right (answer / preview)
    col1, col2 = st.columns(2)

    with col1:
        question = st.text_area(
            "Enter your question:",
            height=140,
            placeholder="e.g., What is the main contribution of this article?",
        )

        uploaded_file = st.file_uploader(
            "Upload an optional document",
            type=["txt", "pdf", "doc", "docx", "html", "htm"],
            help="Accepted formats: TXT, PDF, Word, HTML",
        )

        max_chars = st.slider(
            "Max characters to send from document (to stay within context limits)",
            min_value=2000,
            max_value=20000,
            value=8000,
            step=1000,
        )

        if st.button("Get Answer with Gemini", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Reading document and querying Gemini..."):
                    context_text = ""
                    if uploaded_file is not None:
                        context_text = extract_text_from_file(uploaded_file)

                    if context_text.startswith("Unsupported file type"):
                        st.error(context_text)
                    else:
                        # Truncate context to avoid over-long prompts
                        context_slice = context_text[:max_chars] if context_text else ""

                        prompt = f"""You are a helpful assistant for question answering with documents.

You are given a user question and OPTIONAL document text.
Use the document as supporting context when possible.
If the document does not contain enough information, say you are not sure rather than guessing.

Document context:
-----------------
{context_slice}

-----------------
User question: {question}

Answer clearly and concisely:
"""

                        answer = query_gemini(prompt)
                        col2.write("### Answer (Gemini)")
                        col2.write(answer)

    with col2:
        st.write("### Document Preview (if uploaded)")
        if uploaded_file is not None:
            # Re-read for preview only (Streamlit re-runs script; uploader resets pointer)
            preview_text = extract_text_from_file(uploaded_file)
            if not preview_text.startswith("Unsupported file type"):
                st.text(preview_text[:2000])
            else:
                st.info("Unsupported file type for preview.")


if __name__ == "__main__":
    main()
