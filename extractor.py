import fitz  # PyMuPDF
import os
import io
from PIL import Image

class PDFExtractor:
    def __init__(self, output_img_dir="extracted_images"):
        self.output_img_dir = output_img_dir
        if not os.path.exists(self.output_img_dir):
            os.makedirs(self.output_img_dir)

    def extract(self, pdf_path):
        """
        Extracts text and images from a PDF.
        Returns a dictionary mapping page numbers to text and image paths.
        """
        doc = fitz.open(pdf_path)
        extracted_data = {}
        
        # Determine a prefix based on filename to avoid image name collisions
        file_prefix = os.path.splitext(os.path.basename(pdf_path))[0]

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            
            image_list = page.get_images(full=True)
            saved_images = []
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_name = f"{file_prefix}_page{page_num+1}_img{img_index+1}.{image_ext}"
                image_path = os.path.join(self.output_img_dir, image_name)
                
                # Save image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                saved_images.append(image_path)
            
            extracted_data[page_num + 1] = {
                "text": text,
                "images": saved_images
            }
            
        return extracted_data

if __name__ == "__main__":
    # Simple test
    extractor = PDFExtractor(output_img_dir="data/extracted")
    # Provide a dummy test if running directly
    print("Extractor initialized.")
