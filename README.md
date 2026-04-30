# 🏗️ Applied AI Builder: DDR Report Generator

An automated, AI-powered Detailed Diagnostic Report (DDR) generation system that intelligently merges findings from structural Inspection Reports and Thermal Reports into a cohesive, client-ready document.

## 🚀 Features

- **Automated PDF Parsing**: Extracts text and embedded images from both Inspection and Thermal PDF reports using `PyMuPDF`.
- **AI Context Merging**: Leverages the **Groq Llama 3.1 8B** model to intelligently synthesize findings, match anomalies, and deduce root causes.
- **Smart Formatting**: Dynamically structures the DDR with Area-wise Observations, Severity Assessments, and Recommended Actions.
- **Image Mapping**: Automatically associates extracted images with their corresponding observations for rich, visual reporting.
- **Streamlit Web UI**: Provides a clean, aesthetic, and responsive web interface for seamless operation.

## 🛠️ Technology Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **AI/LLM Engine**: [Groq API](https://groq.com/) (llama-3.1-8b-instant)
- **PDF Extraction**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **Environment Management**: `python-dotenv`

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thukralhanshika64-design/DDR-Report-Generation.git
   cd DDR-Report-Generation
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a hidden `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🖥️ Usage

Run the Streamlit application locally:
```bash
streamlit run app.py
```

1. Open your browser to `http://localhost:8501`.
2. Upload your **Inspection Report (PDF)** and **Thermal Report (PDF)**.
3. Click **Generate DDR**.
4. The system will extract the data, process it through the AI model, and render a beautifully formatted Detailed Diagnostic Report directly on the screen!

## 🔒 Security
The API key is strictly read from the `.env` file, ensuring complete security and avoiding accidental exposure in the source code.

---
*Built for the Applied AI Builder Assignment*
