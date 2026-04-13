---
name: pdf-analyzer
description: Analyze construction blueprints and technical PDFs to extract architectural data, dimensions, materials, and quantities. Use when processing PDF construction plans to extract areas, dimensions, room counts, door/window specifications, and material quantities (concrete, steel, pipes, etc.). Rasterizes PDF pages to images using PyMuPDF and analyzes with vision models for OCR extraction.
---

# PDF Analyzer - Construction Plans

Analyzes construction blueprints and technical PDFs to extract data for budget calculations.

## Workflow

1. **Rasterize PDF pages** using PyMuPDF (fitz)
2. **Analyze images** with vision model to extract:
   - Areas and dimensions
   - Room distribution (bedrooms, bathrooms, living, dining, kitchen)
   - Door and window specifications
   - Material quantities (concrete m³, steel, pipes, etc.)
   - Structural details
3. **Generate structured output** for budget calculation

## Scripts

### analyze_pdf.py
```python
scripts/analyze_pdf.py <pdf_path> --output <json_output>
```

Extracts all technical data from a construction plan PDF:
- Areas by level
- Room counts and types
- Door/window quantities
- Material specifications
- Dimensions

## Usage

For Casa L-32 analysis:
```bash
scripts/analyze_pdf.py /planos/L-32/A-100.pdf --output a100_data.json
scripts/analyze_pdf.py /planos/L-32/A-002.pdf --output a002_data.json
```

## Reference

See references/blueprint-patterns.md for common blueprint layouts and data extraction patterns.