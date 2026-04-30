import os
from ai_processor import AIProcessor

def test():
    print("Testing AI Processor...")
    processor = AIProcessor()
    
    mock_insp = {1: {"text": "Roof is leaking.", "images": []}}
    mock_therm = {1: {"text": "Thermal anomaly detected on roof.", "images": []}}
    
    try:
        res = processor.generate_ddr(mock_insp, mock_therm)
        print("Success! Output:")
        print(res)
    except Exception as e:
        print("Error:")
        print(str(e))

if __name__ == "__main__":
    test()
