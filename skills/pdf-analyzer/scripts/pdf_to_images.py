#!/usr/bin/env python3
"""
PDF to Images Converter
Rasteriza cada página del PDF a imágenes PNG de alta calidad.
Usa PyMuPDF (fitz) para extracción rápida.
"""

import sys
import os
import fitz  # PyMuPDF
from pathlib import Path


def pdf_to_images(pdf_path, output_dir=None, dpi=200, zoom_factor=2):
    """
    Convierte cada página de un PDF a imágenes PNG.
    
    Args:
        pdf_path: Ruta al archivo PDF
        output_dir: Directorio de salida (default: mismo directorio que PDF)
        dpi: Resolución DPI deseada (default: 200)
        zoom_factor: Factor de zoom adicional (default: 2)
    
    Returns:
        Lista de rutas a las imágenes generadas
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
    
    # Crear directorio de salida
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Abrir PDF
    doc = fitz.open(pdf_path)
    images = []
    
    print(f"📄 PDF con {len(doc)} páginas")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Calcular matriz de zoom basada en DPI
        # 72 DPI es la base de PDF, así que: zoom = dpi / 72
        zoom = (dpi / 72) * zoom_factor
        mat = fitz.Matrix(zoom, zoom)
        
        # Renderizar página a imagen
        pix = page.get_pixmap(matrix=mat)
        
        # Guardar imagen
        img_path = output_dir / f"page_{page_num + 1:03d}.png"
        pix.save(str(img_path))
        images.append(str(img_path))
        
        print(f"  ✓ Página {page_num + 1}: {img_path.name} ({pix.width}x{pix.height}px)")
    
    doc.close()
    
    print(f"\n✅ {len(images)} imágenes generadas en: {output_dir}")
    return images


def main():
    if len(sys.argv) < 2:
        print("Uso: python pdf_to_images.py <pdf_path> [output_dir] [dpi]")
        print("Ejemplo: python pdf_to_images.py plano.pdf ./imagenes 300")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    
    try:
        images = pdf_to_images(pdf_path, output_dir, dpi)
        print("\nRutas de imágenes:")
        for img in images:
            print(f"  - {img}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
