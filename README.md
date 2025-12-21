# 📚 Web-based LLM App – Project 2

A multi-question **web-based LLM application** built with **Python + Streamlit**.

The app supports:

1. **Question 1 – Document Question Answering (Q1)**  
   Uses a **local open-source LLM** (`llama3.2:latest` via **Ollama**) to answer questions using an uploaded document as context.

2. **Question 2 – Abbreviation Index (Q2)**  
   Uses the same local LLM to extract **abbreviations + full forms** from multiple uploaded research articles.

3. **Question 4 – Gemini API (Q4)**  
   Rebuilds Q1 with a **closed-source LLM (Google Gemini)** and is **deployed on Streamlit Cloud**, with GitHub as the deployment source (Q3 requirement).

---

## 🧩 Features

### Q1 – Document Question Answering (Local LLM)

- Input a **free-text question**.
- Optionally upload a document in **TXT, PDF, DOC/DOCX, HTML**.
- The app:
  - Extracts text from the uploaded document.
  - Sends a combined prompt (question + document context) to `llama3.2:latest` running in **Ollama**.
  - Displays the answer in the UI.

**Screenshot (local run):**  

<img width="1918" height="1030" alt="Screenshot 2025-12-09 192806" src="https://github.com/user-attachments/assets/ac1854d0-d62f-43e4-aabf-781affb38cdb" />

Q1 – Local LLM and VS Code

<img width="1919" height="1032" alt="Screenshot 2025-12-09 192840" src="https://github.com/user-attachments/assets/fcc5ade0-35e0-4b78-8c33-aeec18a932cb" />

Combined Q1 & Q2 App

<img width="1918" height="1029" alt="Screenshot 2025-12-09 192904" src="https://github.com/user-attachments/assets/ede60b0d-eb37-41c2-a118-0be7f793c9f0" />

Q2 – Abbreviation Index Screen

<img width="1916" height="904" alt="Screenshot 2025-12-09 222406" src="https://github.com/user-attachments/assets/4fb68701-fcdc-4dca-8203-2d886262800e" />

Q4 – Gemini Cloud Deployment

