import os

class ReportGenerator:
    def __init__(self):
        pass

    def generate_markdown(self, ddr_data):
        """
        Generates a markdown formatted string from the DDR JSON data.
        """
        if not ddr_data:
            return "## Error\nFailed to generate report data."

        md = "# Detailed Diagnostic Report (DDR)\n\n"
        
        # 1. Property Issue Summary
        md += "## 1. Property Issue Summary\n"
        md += f"{ddr_data.get('property_issue_summary', 'Not Available')}\n\n"
        
        # 2. Area-wise Observations
        md += "## 2. Area-wise Observations\n"
        observations = ddr_data.get('area_wise_observations', [])
        if not observations:
            md += "Not Available\n\n"
        else:
            for obs in observations:
                area = obs.get('area', 'Unknown Area')
                observation = obs.get('observation', 'Not Available')
                images = obs.get('associated_images', [])
                
                md += f"### {area}\n"
                md += f"**Observation:** {observation}\n\n"
                
                if images and len(images) > 0:
                    md += "**Associated Images:**\n\n"
                    for img in images:
                        # Assuming the image paths are valid relative paths or can be loaded by Streamlit
                        md += f"![{area} Image]({img})\n\n"
                else:
                    md += "*Image Not Available*\n\n"
        
        # 3. Probable Root Cause
        md += "## 3. Probable Root Cause\n"
        md += f"{ddr_data.get('probable_root_cause', 'Not Available')}\n\n"
        
        # 4. Severity Assessment
        md += "## 4. Severity Assessment\n"
        severity_data = ddr_data.get('severity_assessment', {})
        severity = severity_data.get('severity', 'Not Available')
        reasoning = severity_data.get('reasoning', 'Not Available')
        
        # Color coding severity for markdown if possible, but standard text is fine
        md += f"**Severity:** {severity}\n\n"
        md += f"**Reasoning:** {reasoning}\n\n"
        
        # 5. Recommended Actions
        md += "## 5. Recommended Actions\n"
        actions = ddr_data.get('recommended_actions', [])
        if not actions:
            md += "Not Available\n\n"
        else:
            for action in actions:
                md += f"- {action}\n"
            md += "\n"
            
        # 6. Additional Notes
        md += "## 6. Additional Notes\n"
        md += f"{ddr_data.get('additional_notes', 'Not Available')}\n\n"
        
        # 7. Missing or Unclear Information
        md += "## 7. Missing or Unclear Information\n"
        md += f"{ddr_data.get('missing_or_unclear_information', 'Not Available')}\n\n"
        
        return md
