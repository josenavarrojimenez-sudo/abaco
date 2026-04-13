#!/usr/bin/env python3
"""
PDF Image Analyzer with Vision Model
Analiza imágenes de planos usando el modelo Gemma 4 via Ollama Cloud.
Extrae datos técnicos para presupuestos de construcción.
"""

import sys
import os
import json
import base64
from pathlib import Path
import requests


def encode_image(image_path):
    """Codifica imagen a base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_image_with_gemma(image_path, prompt=None, api_url=None):
    """
    Analiza una imagen usando Gemma 4 via Ollama Cloud.
    
    Args:
        image_path: Ruta a la imagen PNG/JPG
        prompt: Prompt personalizado para el análisis
        api_url: URL base de Ollama (default: http://localhost:11434)
    
    Returns:
        Dict con la respuesta estructurada del modelo
    """
    if api_url is None:
        api_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    # Prompt por defecto para análisis de planos
    if prompt is None:
        prompt = """Analiza este plano arquitectónico de construcción y extrae toda la información técnica relevante.

Proporciona un JSON estructurado con:

{
  "proyecto": {
    "nombre": "nombre del proyecto si aparece",
    "tipo": "residencial/comercial/industrial/etc",
    "escala": "escala del plano"
  },
  "areas": [
    {"espacio": "nombre", "area_m2": numero, "tipo": "interior/exterior"}
  ],
  "dimensiones": {
    "lote": {"frente": numero, "fondo": numero, "area_total": numero},
    "construccion": {"altura": numero, "pisos": numero}
  },
  "materiales_identificados": [
    {"material": "nombre", "ubicacion": "donde se usa", "cantidad_aprox": "texto"}
  ],
  "espacios": [
    {"nombre": "sala/cocina/etc", "cantidad": numero, "area_total": numero}
  ],
  "puertas_ventanas": [
    {"tipo": "puerta/ventana", "medida": "ej: 0.90x2.10", "cantidad": numero, "material": "texto"}
  ],
  "acabados": {
    "pisos": ["ceramica", "porcelanato", etc],
    "muros": ["pintura", "azulejo", etc],
    "techos": ["drywall", "estructura", etc]
  },
  "estructura": {
    "tipo": "mamposteria/concreto/mixto",
    "cimentacion": "descripcion",
    "entrepiso": "descripcion"
  },
  "instalaciones": {
    "hidraulica": "descripcion breve",
    "electrica": "descripcion breve",
    "sanitaria": "descripcion breve"
  },
  "observaciones": "notas importantes del plano"
}

Responde ÚNICAMENTE con el JSON válido, sin texto adicional."""

    # Codificar imagen
    base64_image = encode_image(image_path)
    
    # Llamar a Ollama API
    try:
        response = requests.post(
            f"{api_url}/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 8192
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            # Intentar extraer JSON de la respuesta
            try:
                # Buscar JSON en la respuesta (puede estar entre markdown)
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"raw_response": content}
            except json.JSONDecodeError:
                return {"raw_response": content, "parse_error": True}
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    
    except requests.exceptions.ConnectionError:
        return {"error": "No se pudo conectar a Ollama", "details": f"Verificar que Ollama esté corriendo en {api_url}"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def batch_analyze_images(image_paths, output_file=None, api_url=None):
    """
    Analiza múltiples imágenes y combina los resultados.
    
    Args:
        image_paths: Lista de rutas a imágenes
        output_file: Archivo JSON para guardar resultados
        api_url: URL de Ollama
    
    Returns:
        Dict con resultados combinados de todas las páginas
    """
    all_results = {
        "paginas_analizadas": len(image_paths),
        "resultados_por_pagina": [],
        "resumen_consolidado": {}
    }
    
    for i, img_path in enumerate(image_paths, 1):
        print(f"\n🔍 Analizando página {i}/{len(image_paths)}: {img_path}")
        
        result = analyze_image_with_gemma(img_path, api_url=api_url)
        
        page_result = {
            "pagina": i,
            "imagen": str(img_path),
            "analisis": result
        }
        
        all_results["resultados_por_pagina"].append(page_result)
        
        # Mostrar resumen rápido
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            areas = result.get("areas", [])
            print(f"  ✓ Espacios detectados: {len(areas)}")
            espacios = result.get("espacios", [])
            if espacios:
                print(f"  ✓ Tipos de espacio: {', '.join([e.get('nombre', '') for e in espacios[:3]])}")
    
    # Guardar resultados si se especificó archivo
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados guardados en: {output_file}")
    
    return all_results


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_with_vision.py <imagen1> [imagen2] [...] [--output resultado.json]")
        print("Ejemplo: python analyze_with_vision.py ./imagenes/*.png --output analisis.json")
        sys.exit(1)
    
    # Parsear argumentos
    image_paths = []
    output_file = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif not arg.startswith("--"):
            image_paths.append(arg)
            i += 1
        else:
            i += 1
    
    if not image_paths:
        print("❌ No se especificaron imágenes")
        sys.exit(1)
    
    # Verificar que las imágenes existen
    valid_paths = []
    for path in image_paths:
        if Path(path).exists():
            valid_paths.append(path)
        else:
            print(f"⚠️ Imagen no encontrada: {path}")
    
    if not valid_paths:
        print("❌ No se encontraron imágenes válidas")
        sys.exit(1)
    
    # Analizar
    results = batch_analyze_images(valid_paths, output_file)
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN:")
    print(f"  Páginas analizadas: {results['paginas_analizadas']}")
    print(f"  Errores: {sum(1 for r in results['resultados_por_pagina'] if 'error' in r['analisis'])}")


if __name__ == "__main__":
    main()
