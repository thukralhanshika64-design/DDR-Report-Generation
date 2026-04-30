import streamlit as st
import os
import shutil
from extractor import PDFExtractor
from ai_processor import AIProcessor
from dotenv import load_dotenv

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="DDR Report Generator", page_icon="📄", layout="wide")

st.title("🏗️ Applied AI Builder: DDR Report Generation")
st.markdown("This system takes an **Inspection Report** and a **Thermal Report**, extracts observations and images, and generates a structured **Detailed Diagnostic Report (DDR)** using AI.")

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

    # Ensure output image directory exists and is clean
    if os.path.exists(OUTPUT_IMG_DIR):
        shutil.rmtree(OUTPUT_IMG_DIR)
    os.makedirs(OUTPUT_IMG_DIR)

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
