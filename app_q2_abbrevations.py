import streamlit as st # type: ignore
import requests # type: ignore
from io import StringIO

from docx import Document # type: ignore
import PyPDF2 # type: ignore
from bs4 import BeautifulSoup # type: ignore

# ---------- Ollama / LLM config ----------
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
        resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"Error contacting local LLM: {e}"


# ---------- File reading helpers ----------

def read_txt(file) -> str:
    return file.read().decode("utf-8", errors="ignore")


def read_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text.append(page_text)
    return "\n".join(text)


def read_docx(file) -> str:
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)


def read_html(file) -> str:
    html_bytes = file.read()
    html_str = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text(separator="\n")


def extract_text_from_file(uploaded_file) -> str:
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


# ---------- Streamlit UI ----------

def main():
    st.set_page_config(page_title="LLM App – Q1 & Q2", layout="wide")

    st.title("Web-based LLM App (Project 2)")

    mode = st.sidebar.radio(
        "Select mode",
        ["Question Answering (Q1)", "Abbreviation Index (Q2)"],
    )

    if mode == "Question Answering (Q1)":
        run_q1_ui()
    else:
        run_q2_ui()


def run_q1_ui():
    st.subheader("Question 1: Document Question Answering")

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

                    if context_text.startswith("Unsupported file type"):
                        st.error(context_text)
                    else:
                        prompt = f"""You are a helpful assistant for question answering with documents.

You are given a user question and OPTIONAL document text.
Use the document as supporting context when possible.
If the document does not contain enough information, say you are not sure rather than guessing.

Document context:
-----------------
{context_text[:8000]}

-----------------
User question: {question}

Answer clearly and concisely:
"""

                        answer = query_ollama(prompt)
                        col2.write("### Answer")
                        col2.write(answer)

    with col2:
        uploaded_file = st.session_state.get("uploaded_file_q1", None)
        # We can't reliably re-use the uploader state here across reruns,
        # so just show a note instead of preview if needed.
        st.info("Upload a document on the left and click **Get Answer** to see the response here.")


def run_q2_ui():
    st.subheader("Question 2: Generate Abbreviation Index")

    st.markdown(
        """
Upload each article (e.g., **Article1.pdf**, **Article2.pdf**, **Article3.pdf**).  
For each file, the app will ask the local LLM to extract abbreviations in the format:

`WDC: weighted degree centrality`  
`SH: structural holes`  
`…`
"""
    )

    uploaded_files = st.file_uploader(
        "Upload one or more articles",
        type=["pdf", "txt", "doc", "docx", "html", "htm"],
        accept_multiple_files=True,
    )

    if st.button("Generate Abbreviation Index", type="primary"):
        if not uploaded_files:
            st.warning("Please upload at least one article.")
            return

        for file in uploaded_files:
            st.markdown("---")
            st.write(f"### Abbreviation index for: `{file.name}`")

            with st.spinner(f"Extracting abbreviations from {file.name} using local LLM..."):
                text = extract_text_from_file(file)

                if text.startswith("Unsupported file type"):
                    st.error(text)
                    continue

                # You can increase the slice if your model/context allows it
                limited_text = text[:10000]

                prompt = f"""You are an assistant that extracts abbreviations from scientific articles.

You are given the text of a single article. 
Your task is to build an **abbreviation index**.

Instructions:
- Find all abbreviations defined in forms like "full term (ABBR)" or "ABBR (full term)".
- Only include abbreviations that actually appear in the article.
- For each abbreviation, output exactly one line with the format:
  ABBR: full term
- Sort the output **alphabetically by abbreviation**.
- Do NOT add explanations beyond "ABBR: full term".
- If you are unsure about an item, skip it instead of guessing.

Article text:
-----------------
{limited_text}
-----------------

Now output the abbreviation index in the requested format:
"""

                answer = query_ollama(prompt)
                st.text(answer)


if __name__ == "__main__":
    main()
