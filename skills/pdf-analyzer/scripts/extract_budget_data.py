#!/usr/bin/env python3
"""
Budget Data Extractor
Procesa los resultados del análisis de visión y extrae datos estructurados
para cálculo de presupuestos de construcción.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def extract_material_quantities(analysis_data: Dict) -> Dict[str, Any]:
    """
    Extrae cantidades de materiales del análisis de visión.
    
    Returns:
        Dict con materiales organizados por categoría
    """
    materials = {
        "estructura": [],
        "acabados_pisos": [],
        "acabados_muros": [],
        "acabados_techos": [],
        "instalaciones": [],
        "puertas_ventanas": []
    }
    
    # Procesar todas las páginas
    for page in analysis_data.get("resultados_por_pagina", []):
        analisis = page.get("analisis", {})
        
        # Materiales identificados
        mats = analisis.get("materiales_identificados", [])
        for mat in mats:
            material_data = {
                "material": mat.get("material", ""),
                "ubicacion": mat.get("ubicacion", ""),
                "cantidad": mat.get("cantidad_aprox", ""),
                "pagina": page.get("pagina", 0)
            }
            
            # Clasificar por tipo
            mat_lower = mat.get("material", "").lower()
            if any(x in mat_lower for x in ["concreto", "cemento", "acero", "hierro", "varilla", "malla"]):
                materials["estructura"].append(material_data)
            elif any(x in mat_lower for x in ["ceramica", "porcelanato", "piso", "loseta", "pavimento"]):
                materials["acabados_pisos"].append(material_data)
            elif any(x in mat_lower for x in ["pintura", "azulejo", "enlucido", "repello", "fachada"]):
                materials["acabados_muros"].append(material_data)
            elif any(x in mat_lower for x in ["drywall", "cielo", "techo", "laminado"]):
                materials["acabados_techos"].append(material_data)
            elif any(x in mat_lower for x in ["tuberia", "cable", "switch", "tomacorriente", "sanitario", "griferia"]):
                materials["instalaciones"].append(material_data)
            else:
                materials["instalaciones"].append(material_data)
        
        # Puertas y ventanas
        pv_list = analisis.get("puertas_ventanas", [])
        for pv in pv_list:
            materials["puertas_ventanas"].append({
                "tipo": pv.get("tipo", ""),
                "medida": pv.get("medida", ""),
                "cantidad": pv.get("cantidad", 0),
                "material": pv.get("material", ""),
                "pagina": page.get("pagina", 0)
            })
    
    return materials


def calculate_total_areas(analysis_data: Dict) -> Dict[str, float]:
    """
    Calcula áreas totales por tipo de espacio.
    
    Returns:
        Dict con áreas consolidadas
    """
    areas = {
        "total_construccion": 0,
        "total_interiores": 0,
        "total_exteriores": 0,
        "por_tipo_espacio": {},
        "detalle_ambientes": []
    }
    
    seen_rooms = set()  # Evitar duplicados
    
    for page in analysis_data.get("resultados_por_pagina", []):
        analisis = page.get("analisis", {})
        
        # Áreas de espacios
        espacios = analisis.get("espacios", [])
        for esp in espacios:
            nombre = esp.get("nombre", "").lower().strip()
            area = esp.get("area_total", 0) or 0
            cantidad = esp.get("cantidad", 1)
            
            # Evitar contar el mismo espacio dos veces
            room_key = f"{nombre}_{page.get('pagina', 0)}"
            if room_key not in seen_rooms:
                seen_rooms.add(room_key)
                
                areas["detalle_ambientes"].append({
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "area": area,
                    "pagina": page.get("pagina", 0)
                })
                
                # Acumular por tipo
                if nombre not in areas["por_tipo_espacio"]:
                    areas["por_tipo_espacio"][nombre] = 0
                areas["por_tipo_espacio"][nombre] += area
                
                areas["total_construccion"] += area
        
        # Áreas específicas
        for area_data in analisis.get("areas", []):
            tipo = area_data.get("tipo", "").lower()
            area_val = area_data.get("area_m2", 0) or 0
            
            if "interior" in tipo:
                areas["total_interiores"] += area_val
            elif "exterior" in tipo:
                areas["total_exteriores"] += area_val
    
    return areas


def generate_quantity_takeoff(analysis_data: Dict) -> Dict[str, Any]:
    """
    Genera un quantity takeoff completo para presupuesto.
    
    Returns:
        Dict con cantidades organizadas por partida
    """
    takeoff = {
        "proyecto": {},
        "areas": {},
        "partidas": {}
    }
    
    # Extraer información del proyecto
    for page in analysis_data.get("resultados_por_pagina", []):
        analisis = page.get("analisis", {})
        proyecto = analisis.get("proyecto", {})
        if proyecto:
            takeoff["proyecto"] = proyecto
            break
    
    # Calcular áreas
    takeoff["areas"] = calculate_total_areas(analysis_data)
    
    # Extraer materiales
    materials = extract_material_quantities(analysis_data)
    
    # Organizar partidas
    areas = takeoff["areas"]
    total_area = areas.get("total_construccion", 0)
    
    # Partida 1: Preliminares (3-5% del proyecto)
    takeoff["partidas"]["preliminares"] = {
        "descripcion": "Limpieza, trazo, instalación de obra",
        "unidad": "m²",
        "cantidad": round(total_area, 2),
        "notas": "Incluye instalación provisional y limpieza"
    }
    
    # Partida 2: Estructura
    estructura = takeoff["partidas"]["estructura"] = {
        "descripcion": "Cimentación, columnas, vigas, losas",
        "items": [],
        "notas": "Basado en materiales identificados"
    }
    
    for mat in materials["estructura"]:
        estructura["items"].append({
            "material": mat["material"],
            "ubicacion": mat["ubicacion"],
            "cantidad": mat["cantidad"]
        })
    
    # Partida 3: Albañilería (muros)
    takeoff["partidas"]["albanileria"] = {
        "descripcion": "Muros de carga y divisorios",
        "unidad": "m²",
        "cantidad": round(total_area * 2.5, 2),  # Estimado: 2.5x área para muros
        "notas": "Incluye muros interiores y exteriores"
    }
    
    # Partida 4: Acabados
    acabados = takeoff["partidas"]["acabados"] = {
        "descripcion": "Pisos, muros y techos",
        "pisos": materials["acabados_pisos"],
        "muros": materials["acabados_muros"],
        "techos": materials["acabados_techos"]
    }
    
    # Partida 5: Instalaciones
    takeoff["partidas"]["instalaciones"] = {
        "descripcion": "Instalaciones hidráulicas, eléctricas y sanitarias",
        "materiales": materials["instalaciones"],
        "notas": "Revisar planos eléctricos y sanitarios específicos"
    }
    
    # Partida 6: Carpintería (puertas y ventanas)
    takeoff["partidas"]["carpinteria"] = {
        "descripcion": "Puertas, ventanas y accesorios",
        "items": materials["puertas_ventanas"],
        "resumen": {}
    }
    
    # Resumen de puertas y ventanas por tipo
    for pv in materials["puertas_ventanas"]:
        tipo = pv.get("tipo", "desconocido")
        if tipo not in takeoff["partidas"]["carpinteria"]["resumen"]:
            takeoff["partidas"]["carpinteria"]["resumen"][tipo] = {
                "cantidad": 0,
                "medidas": set()
            }
        takeoff["partidas"]["carpinteria"]["resumen"][tipo]["cantidad"] += pv.get("cantidad", 1)
        takeoff["partidas"]["carpinteria"]["resumen"][tipo]["medidas"].add(pv.get("medida", ""))
    
    # Convertir sets a listas para JSON
    for tipo in takeoff["partidas"]["carpinteria"]["resumen"]:
        takeoff["partidas"]["carpinteria"]["resumen"][tipo]["medidas"] = list(
            takeoff["partidas"]["carpinteria"]["resumen"][tipo]["medidas"]
        )
    
    return takeoff


def generate_technical_summary(analysis_data: Dict) -> Dict[str, Any]:
    """
    Genera un resumen técnico completo del proyecto.
    
    Returns:
        Dict con información técnica consolidada
    """
    summary = {
        "informacion_general": {},
        "caracteristicas": {},
        "superficies": {},
        "estructura": {},
        "acabados": {},
        "instalaciones": {},
        "observaciones": []
    }
    
    all_observations = []
    
    for page in analysis_data.get("resultados_por_pagina", []):
        analisis = page.get("analisis", {})
        
        # Información general
        if not summary["informacion_general"]:
            summary["informacion_general"] = analisis.get("proyecto", {})
        
        # Características
        dims = analisis.get("dimensiones", {})
        if dims:
            summary["caracteristicas"]["dimensiones_lote"] = dims.get("lote", {})
            summary["caracteristicas"]["dimensiones_construccion"] = dims.get("construccion", {})
        
        # Estructura
        struct = analisis.get("estructura", {})
        if struct:
            summary["estructura"].update(struct)
        
        # Acabados
        acab = analisis.get("acabados", {})
        if acab:
            for key in ["pisos", "muros", "techos"]:
                if key in acab and acab[key]:
                    if key not in summary["acabados"]:
                        summary["acabados"][key] = []
                    summary["acabados"][key].extend(acab[key])
                    # Eliminar duplicados
                    summary["acabados"][key] = list(set(summary["acabados"][key]))
        
        # Instalaciones
        inst = analisis.get("instalaciones", {})
        if inst:
            summary["instalaciones"].update(inst)
        
        # Observaciones
        obs = analisis.get("observaciones", "")
        if obs:
            all_observations.append(f"Página {page.get('pagina', '?')}: {obs}")
    
    summary["observaciones"] = all_observations
    
    # Calcular superficies
    areas = calculate_total_areas(analysis_data)
    summary["superficies"] = {
        "total_construccion_m2": areas.get("total_construccion", 0),
        "area_interiores_m2": areas.get("total_interiores", 0),
        "area_exteriores_m2": areas.get("total_exteriores", 0),
        "desglose_por_tipo": areas.get("por_tipo_espacio", {}),
        "ambientes": [
            {"nombre": a["nombre"], "area": a["area"], "cantidad": a["cantidad"]}
            for a in areas.get("detalle_ambientes", [])
        ]
    }
    
    return summary


def process_analysis_file(input_file: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Procesa un archivo de análisis JSON y genera todos los entregables.
    
    Args:
        input_file: Ruta al archivo JSON de análisis
        output_dir: Directorio para guardar archivos de salida
    
    Returns:
        Dict con todas las salidas generadas
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {input_file}")
    
    # Cargar análisis
    with open(input_path, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # Generar entregables
    results = {
        "datos_presupuesto": generate_quantity_takeoff(analysis_data),
        "resumen_tecnico": generate_technical_summary(analysis_data)
    }
    
    # Guardar archivos si se especificó directorio
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar datos de presupuesto
        budget_file = output_path / "datos_presupuesto.json"
        with open(budget_file, 'w', encoding='utf-8') as f:
            json.dump(results["datos_presupuesto"], f, indent=2, ensure_ascii=False)
        print(f"💾 Datos de presupuesto guardados: {budget_file}")
        
        # Guardar resumen técnico
        summary_file = output_path / "resumen_tecnico.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results["resumen_tecnico"], f, indent=2, ensure_ascii=False)
        print(f"💾 Resumen técnico guardado: {summary_file}")
        
        # Generar reporte de texto
        report_file = output_path / "reporte_tecnico.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(generate_text_report(results["resumen_tecnico"]))
        print(f"💾 Reporte técnico guardado: {report_file}")
    
    return results


def generate_text_report(summary: Dict) -> str:
    """Genera un reporte técnico en formato texto."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("REPORTE TÉCNICO DE PROYECTO DE CONSTRUCCIÓN")
    lines.append("=" * 60)
    lines.append("")
    
    # Información general
    info = summary.get("informacion_general", {})
    if info:
        lines.append("📋 INFORMACIÓN GENERAL")
        lines.append("-" * 40)
        if info.get("nombre"):
            lines.append(f"Nombre: {info['nombre']}")
        if info.get("tipo"):
            lines.append(f"Tipo: {info['tipo']}")
        if info.get("escala"):
            lines.append(f"Escala: {info['escala']}")
        lines.append("")
    
    # Superficies
    sup = summary.get("superficies", {})
    lines.append("📐 SUPERFICIES")
    lines.append("-" * 40)
    lines.append(f"Total construcción: {sup.get('total_construccion_m2', 0):.2f} m²")
    lines.append(f"Área interiores: {sup.get('area_interiores_m2', 0):.2f} m²")
    lines.append(f"Área exteriores: {sup.get('area_exteriores_m2', 0):.2f} m²")
    lines.append("")
    
    # Ambientes
    if sup.get("ambientes"):
        lines.append("🏠 AMBIENTES IDENTIFICADOS")
        lines.append("-" * 40)
        for amb in sup["ambientes"]:
            lines.append(f"  • {amb['nombre']}: {amb['cantidad']} x {amb['area']:.2f} m²")
        lines.append("")
    
    # Estructura
    struct = summary.get("estructura", {})
    if struct:
        lines.append("🏗️ ESTRUCTURA")
        lines.append("-" * 40)
        if struct.get("tipo"):
            lines.append(f"Tipo: {struct['tipo']}")
        if struct.get("cimentacion"):
            lines.append(f"Cimentación: {struct['cimentacion']}")
        if struct.get("entrepiso"):
            lines.append(f"Entrepiso: {struct['entrepiso']}")
        lines.append("")
    
    # Acabados
    acab = summary.get("acabados", {})
    if acab:
        lines.append("🎨 ACABADOS")
        lines.append("-" * 40)
        if acab.get("pisos"):
            lines.append(f"Pisos: {', '.join(acab['pisos'])}")
        if acab.get("muros"):
            lines.append(f"Muros: {', '.join(acab['muros'])}")
        if acab.get("techos"):
            lines.append(f"Techos: {', '.join(acab['techos'])}")
        lines.append("")
    
    # Instalaciones
    inst = summary.get("instalaciones", {})
    if inst:
        lines.append("⚡ INSTALACIONES")
        lines.append("-" * 40)
        if inst.get("hidraulica"):
            lines.append(f"Hidráulica: {inst['hidraulica']}")
        if inst.get("electrica"):
            lines.append(f"Eléctrica: {inst['electrica']}")
        if inst.get("sanitaria"):
            lines.append(f"Sanitaria: {inst['sanitaria']}")
        lines.append("")
    
    # Observaciones
    obs = summary.get("observaciones", [])
    if obs:
        lines.append("📝 OBSERVACIONES")
        lines.append("-" * 40)
        for o in obs:
            lines.append(f"  • {o}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("Generado por Ábaco - Especialista en Presupuestos")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Uso: python extract_budget_data.py <analisis.json> [output_dir]")
        print("Ejemplo: python extract_budget_data.py analisis.json ./resultados/")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        results = process_analysis_file(input_file, output_dir)
        
        print("\n" + "=" * 60)
        print("RESUMEN DE DATOS EXTRAÍDOS")
        print("=" * 60)
        
        # Mostrar resumen técnico
        tech = results["resumen_tecnico"]
        sup = tech.get("superficies", {})
        print(f"\n📐 Superficie total: {sup.get('total_construccion_m2', 0):.2f} m²")
        print(f"🏠 Ambientes: {len(sup.get('ambientes', []))}")
        
        # Mostrar datos de presupuesto
        budget = results["datos_presupuesto"]
        print(f"\n💰 Partidas identificadas: {len(budget.get('partidas', {}))}")
        
        print("\n✅ Proceso completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
