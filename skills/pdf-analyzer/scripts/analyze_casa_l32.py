#!/usr/bin/env python3
"""
Script to analyze all 16 plans for Casa L-32 (Modelo Zante)
Generates structured data for budget calculation.
"""

import fitz
import json
import os
from pathlib import Path

PLANOS_DIR = "/root/.openclaw/media/inbound/planos_proyecto_2/Planos"
OUTPUT_DIR = "/root/.openclaw/workspace-abaco/analisis_L32"

PLANOS = {
    "general": [
        "General/G-000-PORTADA-Rev.0.pdf",
        "General/G-001-UBICACION-Rev.0.pdf",
        "General/G-002-RESTRICCIONES-Rev.0.pdf"
    ],
    "arquitectonico": [
        "Arquitectónico/A-100-PLANTAS-ARQUITECTONICAS-N1-Rev.0.pdf",
        "Arquitectónico/A-200-ELEVACIONES-Rev.0.pdf",
        "Arquitectónico/A-300-SECCIONES-Rev.0.pdf",
        "Arquitectónico/A-400-DETALLES-Rev.0.pdf",
        "Arquitectónico/A-002-TABLAS-DE-PUERTAS-Y-VENTANAS-Rev.0.pdf"
    ],
    "estructural": [
        "Estructural/S-01-PORTADA-ESTRUCTURAL-Rev.0.pdf",
        "Estructural/S-02-DETALLE-LOSA-DE-ENTREPISO-Rev.0.pdf",
        "Estructural/S-03-DETALLE-MUROS-DE-CARGA-Rev.0.pdf",
        "Estructural/S-04-DETALLE-FUNDACION-Rev.0.pdf",
        "Estructural/S-05-PLANTA-FUNDACION-Rev.0.pdf"
    ],
    "electrico": [
        "Eléctrico/E-000-LEYENDA-Rev.0.pdf",
        "Eléctrico/E-101-LÁMINA-ELÉCTRICA-Rev.2.pdf"
    ],
    "mecanico": [
        "Mecánico/M-000-PORTADA-Rev.0.pdf",
        "Mecánico/M-100-PLANO-MECÁNICO-Rev.0.pdf"
    ],
    "croquis": [
        "Croquis/C-Croquis-L-32-Rev.0.pdf"
    ]
}

def rasterize_all_pdfs():
    """Rasterize all PDF plans to images."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_images = {}
    
    for category, files in PLANOS.items():
        print(f"\n📁 Processing {category}...")
        all_images[category] = []
        
        for pdf_file in files:
            pdf_path = os.path.join(PLANOS_DIR, pdf_file)
            if not os.path.exists(pdf_path):
                print(f"  ⚠️  Not found: {pdf_file}")
                continue
            
            print(f"  📄 {pdf_file}")
            
            try:
                doc = fitz.open(pdf_path)
                category_dir = os.path.join(OUTPUT_DIR, category)
                os.makedirs(category_dir, exist_ok=True)
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    mat = fitz.Matrix(150/72, 150/72)  # 150 DPI
                    pix = page.get_pixmap(matrix=mat)
                    
                    base_name = os.path.splitext(os.path.basename(pdf_file))[0]
                    img_path = os.path.join(category_dir, f"{base_name}_page{page_num+1}.png")
                    pix.save(img_path)
                    
                    all_images[category].append({
                        "pdf": pdf_file,
                        "page": page_num + 1,
                        "image": img_path
                    })
                
                doc.close()
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    return all_images

if __name__ == "__main__":
    print("🏗️  Casa L-32 PDF Analyzer")
    print("=" * 50)
    print(f"Input: {PLANOS_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 50)
    
    images = rasterize_all_pdfs()
    
    # Save manifest
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(images, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Manifest saved to: {manifest_path}")
    
    total_pages = sum(len(imgs) for imgs in images.values())
    print(f"📄 Total pages rasterized: {total_pages}")