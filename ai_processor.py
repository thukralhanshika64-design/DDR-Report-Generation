import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your environment or .env file.")
        self.client = Groq(api_key=self.api_key)

    def generate_ddr(self, inspection_data, thermal_data):
        """
        Takes extracted text and image paths from both reports and sends to Groq LLM
        to generate a structured DDR.
        """
        
        # Prepare context
        context = "### INSPECTION REPORT CONTENT ###\n"
        for page_num, data in inspection_data.items():
            context += f"--- Page {page_num} ---\nTEXT:\n{data['text']}\nIMAGES FOUND ON PAGE: {data['images']}\n\n"
            
        context += "\n### THERMAL REPORT CONTENT ###\n"
        for page_num, data in thermal_data.items():
            context += f"--- Page {page_num} ---\nTEXT:\n{data['text']}\nIMAGES FOUND ON PAGE: {data['images']}\n\n"

        # Truncate context to stay within Groq's 6000 TPM free tier limit
        # 1 token is roughly 4 characters. 6000 tokens = ~24000 characters. 
        # Using 15000 to be safe and leave room for the response.
        if len(context) > 15000:
            context = context[:15000] + "\n...[CONTENT TRUNCATED DUE TO FREE TIER API LIMITS]..."

        system_prompt = """
        You are an expert technical inspector and report writer. Your task is to analyze extracted text and image paths from an Inspection Report and a Thermal Report, and combine them into a single, cohesive, client-ready Detailed Diagnostic Report (DDR).

        The input includes the text for each page and the file paths of images found on that page.
        
        Your output MUST be a valid JSON object with the following schema:
        {
          "property_issue_summary": "Overall summary of the issues...",
          "area_wise_observations": [
            {
              "area": "Name of the area (e.g., Roof, HVAC, Master Bedroom)",
              "observation": "Detailed observation logically combining regular and thermal findings...",
              "associated_images": ["path/to/image1.png", "path/to/image2.png"] 
            }
          ],
          "probable_root_cause": "The likely root cause(s) of the issues...",
          "severity_assessment": {
            "severity": "Low | Medium | High | Critical",
            "reasoning": "Why this severity was chosen..."
          },
          "recommended_actions": ["Action 1", "Action 2"],
          "additional_notes": "Any other notes. If information conflicts between reports, note it here.",
          "missing_or_unclear_information": "List anything missing. If nothing is missing, write 'Not Available'."
        }

        CRITICAL RULES:
        1. ONLY return valid JSON. Do not include markdown code fences or conversational text.
        2. Do NOT invent facts not present in the documents.
        3. If information is missing for a section, write "Not Available".
        4. If information conflicts between the reports, mention the conflict.
        5. Use simple, client-friendly language and avoid unnecessary technical jargon.
        6. Combine points logically and avoid duplicates.
        7. For 'associated_images', use the image paths provided in the page context that match the observation. If no images support the observation, leave the array empty.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            raw_output = response.choices[0].message.content.strip()
            
            # Clean possible markdown wrapping
            if raw_output.startswith("```json"):
                raw_output = raw_output[7:-3].strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output[3:-3].strip()
                
            return json.loads(raw_output)
            
        except Exception as e:
            raise RuntimeError(f"Error calling LLM: {e}")

