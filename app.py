import streamlit as st
import os
import shutil
from extractor import PDFExtractor
from ai_processor import AIProcessor
from dotenv import load_dotenv

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="DDR Report Generator", page_icon="📄", layout="wide")

# Custom CSS for Premium Aesthetics
st.markdown("""
    <style>
    /* Main Typography */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 700;
    }
    
    /* Primary Button */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.5);
    }
    
    /* Expander / Cards */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Information Boxes */
    div[data-testid="stInfo"] {
        background-color: #eff6ff;
        border-left-color: #3b82f6;
    }
    
    div[data-testid="stWarning"] {
        background-color: #fffbeb;
        border-left-color: #f59e0b;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✨ Applied AI Builder: DDR Generation")
st.markdown("An intelligent system that merges **Inspection** and **Thermal** reports into a cohesive, client-ready **Detailed Diagnostic Report (DDR)**.")

# Sidebar for configuration
st.sidebar.header("Upload Reports")
inspection_file = st.sidebar.file_uploader("Upload Inspection Report (PDF)", type=["pdf"])
thermal_file = st.sidebar.file_uploader("Upload Thermal Report (PDF)", type=["pdf"])

use_defaults = st.sidebar.button("Use Default Data Folder Files")

# Working directory setup
TEMP_DIR = "temp_uploads"
OUTPUT_IMG_DIR = "extracted_images"

if st.button("Generate DDR", type="primary"):
    
    # Check API key
    final_api_key = os.environ.get("GROQ_API_KEY")
    if not final_api_key:
        st.error("Please provide a Groq API Key in the .env file.")
        st.stop()
        
    insp_path = None
    therm_path = None
    
    if use_defaults:
        if os.path.exists("data/Sample Report.pdf") and os.path.exists("data/Thermal Images.pdf"):
            insp_path = "data/Sample Report.pdf"
            therm_path = "data/Thermal Images.pdf"
        else:
            st.error("Default files not found in 'data/' folder.")
            st.stop()
    else:
        if not inspection_file or not thermal_file:
            st.error("Please upload BOTH the Inspection Report and the Thermal Report, or click 'Use Default Data Folder Files'.")
            st.stop()
            
        # Save uploaded files temporarily
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
        insp_path = os.path.join(TEMP_DIR, "inspection.pdf")
        with open(insp_path, "wb") as f:
            f.write(inspection_file.getbuffer())
            
        therm_path = os.path.join(TEMP_DIR, "thermal.pdf")
        with open(therm_path, "wb") as f:
            f.write(thermal_file.getbuffer())

    # Ensure output image directory exists
    os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

    with st.spinner("Extracting text and images from PDFs..."):
        extractor = PDFExtractor(output_img_dir=OUTPUT_IMG_DIR)
        insp_data = extractor.extract(insp_path)
        therm_data = extractor.extract(therm_path)
        
    with st.spinner("Analyzing data and generating structured DDR using AI..."):
        processor = AIProcessor(api_key=final_api_key)
        ddr_json = processor.generate_ddr(insp_data, therm_data)
        
    if not ddr_json:
        st.error("Failed to generate report. Please check the logs or try again.")
        st.stop()
        
    st.success("DDR Generation Complete!")
    
    # -----------------------------------------------------
    # Render the Report Beautifully in Streamlit
    # -----------------------------------------------------
    st.markdown("---")
    st.header("📋 Detailed Diagnostic Report (DDR)")
    
    # 1. Property Issue Summary
    st.subheader("1. Property Issue Summary")
    st.info(ddr_json.get("property_issue_summary", "Not Available"))
    
    # 2. Area-wise Observations
    st.subheader("2. Area-wise Observations")
    observations = ddr_json.get("area_wise_observations", [])
    if not observations:
        st.write("Not Available")
    else:
        for obs in observations:
            with st.expander(f"📍 {obs.get('area', 'Unknown Area')}", expanded=True):
                st.write(f"**Observation:** {obs.get('observation', 'Not Available')}")
                images = obs.get("associated_images", [])
                if images and len(images) > 0:
                    st.write("**Associated Images:**")
                    cols = st.columns(min(len(images), 3))
                    for i, img_path in enumerate(images):
                        if os.path.exists(img_path):
                            cols[i % 3].image(img_path, use_column_width=True)
                        else:
                            st.warning(f"Image Not Available: {img_path}")
                else:
                    st.markdown("*Image Not Available*")
                    
    # 3. Probable Root Cause
    st.subheader("3. Probable Root Cause")
    st.warning(ddr_json.get("probable_root_cause", "Not Available"))
    
    # 4. Severity Assessment
    st.subheader("4. Severity Assessment")
    severity_data = ddr_json.get("severity_assessment", {})
    sev_level = severity_data.get("severity", "Not Available")
    
    # Color code severity
    sev_color = "gray"
    if sev_level.lower() == "critical": sev_color = "red"
    elif sev_level.lower() == "high": sev_color = "orange"
    elif sev_level.lower() == "medium": sev_color = "blue"
    elif sev_level.lower() == "low": sev_color = "green"
        
    st.markdown(f"**Severity:** :{sev_color}[{sev_level}]")
    st.write(f"**Reasoning:** {severity_data.get('reasoning', 'Not Available')}")
    
    # 5. Recommended Actions
    st.subheader("5. Recommended Actions")
    actions = ddr_json.get("recommended_actions", [])
    if not actions:
        st.write("Not Available")
    else:
        for action in actions:
            st.markdown(f"- {action}")
            
    # 6. Additional Notes
    st.subheader("6. Additional Notes")
    st.write(ddr_json.get("additional_notes", "Not Available"))
    
    # 7. Missing or Unclear Information
    st.subheader("7. Missing or Unclear Information")
    st.write(ddr_json.get("missing_or_unclear_information", "Not Available"))

    # Optional Raw JSON Expander
    with st.expander("View Raw AI Output (JSON)"):
        st.json(ddr_json)
