#!/usr/bin/env python3
"""
PDF Analyzer - Complete Workflow
Orquesta el análisis completo de planos PDF:
1. Convierte PDF a imágenes
2. Analiza cada imagen con visión (Gemma 4)
3. Extrae datos estructurados para presupuesto
4. Genera reportes técnicos

Uso: python analyze_pdf_complete.py <plano.pdf> [output_dir]
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Asegurar que podemos importar los otros scripts
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


def run_command(cmd, description):
    """Ejecuta un comando y muestra progreso"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error en paso: {description}")
        return False
    
    print(f"✅ {description} completado")
    return True


def analyze_pdf_workflow(pdf_path, output_dir=None, skip_vision=False):
    """
    Ejecuta el flujo completo de análisis de PDF.
    
    Args:
        pdf_path: Ruta al archivo PDF
        output_dir: Directorio de salida
        skip_vision: Si es True, omite el análisis con visión (para testing)
    
    Returns:
        Dict con rutas a todos los archivos generados
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
    
    # Crear estructura de directorios
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_analysis"
    else:
        output_dir = Path(output_dir)
    
    images_dir = output_dir / "images"
    results_dir = output_dir / "results"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🏗️ ÁBACO - ANALIZADOR DE PLANOS PDF")
    print("=" * 60)
    print(f"📄 PDF: {pdf_path}")
    print(f"📁 Salida: {output_dir}")
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "pdf_path": str(pdf_path),
        "output_dir": str(output_dir),
        "steps_completed": [],
        "files_generated": {}
    }
    
    # Paso 1: Convertir PDF a imágenes
    print("\n📌 PASO 1/4: Rasterización del PDF")
    print("-" * 60)
    
    try:
        from pdf_to_images import pdf_to_images
        images = pdf_to_images(
            pdf_path=str(pdf_path),
            output_dir=str(images_dir),
            dpi=200,
            zoom_factor=2
        )
        results["steps_completed"].append("pdf_to_images")
        results["files_generated"]["images"] = images
        print(f"✅ {len(images)} imágenes generadas")
    except Exception as e:
        print(f"❌ Error en rasterización: {e}")
        return results
    
    # Paso 2: Análisis con visión
    analysis_file = results_dir / "analisis_vision.json"
    
    if skip_vision:
        print("\n⏭️ PASO 2/4: Análisis con visión (OMITIDO)")
        print("-" * 60)
        print("Modo testing: Se omite el análisis con modelo de visión")
        # Crear archivo de análisis vacío para testing
        dummy_analysis = {
            "paginas_analizadas": len(images),
            "resultados_por_pagina": [],
            "resumen_consolidado": {},
            "modo_testing": True
        }
        with open(analysis_file, 'w') as f:
            json.dump(dummy_analysis, f, indent=2)
    else:
        print("\n📌 PASO 2/4: Análisis con modelo de visión (Gemma 4)")
        print("-" * 60)
        
        try:
            from analyze_with_vision import batch_analyze_images
            analysis = batch_analyze_images(
                image_paths=images,
                output_file=str(analysis_file)
            )
            results["steps_completed"].append("vision_analysis")
            results["files_generated"]["analysis"] = str(analysis_file)
            print(f"✅ Análisis guardado: {analysis_file}")
        except Exception as e:
            print(f"❌ Error en análisis de visión: {e}")
            print("Nota: Asegúrate de que Ollama esté corriendo con Gemma 4")
            return results
    
    # Paso 3: Extraer datos de presupuesto
    print("\n📌 PASO 3/4: Extracción de datos para presupuesto")
    print("-" * 60)
    
    try:
        from extract_budget_data import process_analysis_file
        budget_data = process_analysis_file(
            input_file=str(analysis_file),
            output_dir=str(results_dir)
        )
        results["steps_completed"].append("budget_extraction")
        results["files_generated"]["budget"] = str(results_dir / "datos_presupuesto.json")
        results["files_generated"]["summary"] = str(results_dir / "resumen_tecnico.json")
        results["files_generated"]["report"] = str(results_dir / "reporte_tecnico.txt")
        print("✅ Datos de presupuesto extraídos")
    except Exception as e:
        print(f"❌ Error en extracción de datos: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # Paso 4: Generar resumen final
    print("\n📌 PASO 4/4: Generación de resumen final")
    print("-" * 60)
    
    summary_file = results_dir / "resumen_final.json"
    
    final_summary = {
        "proyecto": budget_data["resumen_tecnico"].get("informacion_general", {}),
        "superficies": budget_data["resumen_tecnico"].get("superficies", {}),
        "estadisticas": {
            "paginas_analizadas": len(images),
            "ambientes_identificados": len(
                budget_data["resumen_tecnico"].get("superficies", {}).get("ambientes", [])
            ),
            "partidas_presupuesto": len(budget_data["datos_presupuesto"].get("partidas", {}))
        },
        "archivos_generados": results["files_generated"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(final_summary, f, indent=2, ensure_ascii=False)
    
    results["steps_completed"].append("final_summary")
    results["files_generated"]["final_summary"] = str(summary_file)
    print(f"✅ Resumen final: {summary_file}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 60)
    print(f"\n📊 RESULTADOS:")
    print(f"  • Páginas procesadas: {len(images)}")
    print(f"  • Ambientes identificados: {final_summary['estadisticas']['ambientes_identificados']}")
    print(f"  • Superficie total: {final_summary['superficies'].get('total_construccion_m2', 0):.2f} m²")
    print(f"\n📁 ARCHIVOS GENERADOS:")
    for name, path in results["files_generated"].items():
        if isinstance(path, list):
            print(f"  • {name}: {len(path)} archivos")
        else:
            print(f"  • {name}: {path}")
    
    print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_pdf_complete.py <plano.pdf> [output_dir] [--skip-vision]")
        print("")
        print("Ejemplos:")
        print("  python analyze_pdf_complete.py plano_casa.pdf")
        print("  python analyze_pdf_complete.py plano_casa.pdf ./resultados/")
        print("  python analyze_pdf_complete.py plano.pdf ./out/ --skip-vision  # Modo testing")
        print("")
        print("Nota: Asegúrate de tener Ollama corriendo con el modelo Gemma 4:")
        print("  ollama run gemma3:4b")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    skip_vision = "--skip-vision" in sys.argv
    
    try:
        results = analyze_pdf_workflow(pdf_path, output_dir, skip_vision)
        
        # Guardar resultado del proceso
        result_file = Path(results["output_dir"]) / "results" / "proceso_resultado.json"
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Resultado del proceso guardado: {result_file}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
