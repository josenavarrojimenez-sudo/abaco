#!/usr/bin/env python3
"""
PDF Analyzer for Construction Blueprints
Rasterizes PDF pages and extracts technical data using vision models.
"""

import fitz  # PyMuPDF
import sys
import json
import os
import base64
from pathlib import Path

def rasterize_pdf(pdf_path, dpi=150):
    """Convert PDF pages to images."""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render page to image
        mat = fitz.Matrix(dpi/72, dpi/72)  # zoom factor
        pix = page.get_pixmap(matrix=mat)
        img_path = f"/tmp/page_{page_num}.png"
        pix.save(img_path)
        
        # Convert to base64 for API
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        
        images.append({
            "page": page_num + 1,
            "image_base64": img_b64,
            "path": img_path
        })
    
    doc.close()
    return images

def extract_data_from_image(img_b64, prompt):
    """Extract data using vision model via API."""
    # This will be called by the agent using sessions_spawn with vision model
    return {"status": "ready_for_analysis", "image_size": len(img_b64)}

def analyze_blueprint(pdf_path):
    """Main function to analyze a construction blueprint."""
    print(f"Analyzing: {pdf_path}")
    
    # Step 1: Rasterize
    print("Rasterizing PDF pages...")
    images = rasterize_pdf(pdf_path)
    print(f"Converted {len(images)} pages to images")
    
    # Save image paths for vision model analysis
    result = {
        "pdf_path": pdf_path,
        "pages_analyzed": len(images),
        "images": images,
        "status": "rasterized"
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_pdf.py <pdf_path> [--output <json_file>]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_file = None
    
    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]
    
    result = analyze_blueprint(pdf_path)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to: {output_file}")
    else:
        print(json.dumps(result, indent=2))