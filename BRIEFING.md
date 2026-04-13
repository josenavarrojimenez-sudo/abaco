# BRIEFING PARA ÁBACO - Proyecto L.32

## TU MISIÓN
Procesar el plano arquitectónico A-100 y generar un presupuesto inmobiliario completo en Excel (formato L.32) y HTML interactivo.

## RECURSOS DISPONIBLES

### 1. Planos del Proyecto L-32
**Ubicación:** `/root/.openclaw/workspace-abaco/data/ejemplos/Planos/Arquitectónico/`

- **Principal:** `A-100-PLANTAS-ARQUITECTONICAS-N1-Rev.0.pdf` (574KB)
- Imagen extraída: `A100_page_1.png` (729KB)

### 2. Rendimientos de Construcción
**Archivo:** `/root/.openclaw/workspace-abaco/data/rendimientos/RENDIMIENTOS_2.xlsx`
**Contenido:** Factores de compactación, desperdicio, dosificaciones por m³

### 3. Plantilla Excel L.32 (Referencia)
**Archivo:** `/root/.openclaw/workspace-abaco/data/plantilla_excel/PRESUPUESTO_L32_BASE.xlsx`
**Estructura:** 23 hojas incluyendo:
- ANALISIS
- DESGLOSE
- Resumen Presupuesto
- BASE DATOS PRECIOS
- COSTOS MO CUADRILLA
- Gastos generales
- Y 17 hojas más...

### 4. Excel L.32 Generado (Demo)
**Archivo:** `/root/.openclaw/workspace-abaco/data/presupuesto_l32_generado.xlsx`
**Nota:** Estructura correcta, necesita datos reales del plano

### 5. Modelos Configurados por Tarea
**Archivo:** `/root/.openclaw/workspace-abaco/model-presets.json`

| Tarea | Modelo |
|-------|--------|
| Análisis Planos PDF | `kimi-k2.5:cloud` |
| Generación Excel | `qwen3-coder-next:cloud` |
| Cálculos Matemáticos | `deepseek-v3.2:cloud` |
| Contexto General | `kimi-k2.5:cloud` |

## FLUJO DE TRABAJO

### Paso 1: Analizar Plano A-100
1. Cargar imagen `A100_page_1.png`
2. Usar modelo `kimi-k2.5:cloud` para visión
3. Extraer:
   - Lista de ambientes (habitaciones, baños, cocina, etc.)
   - Áreas en m² por ambiente
   - Dimensiones totales del proyecto

### Paso 2: Aplicar Rendimientos
1. Cargar `RENDIMIENTOS_2.xlsx`
2. Calcular cantidades de materiales según áreas extraídas
3. Factores: compactación 0.30, desperdicio 0.05, MO concreto 1.10

### Paso 3: Generar Excel L.32
1. Usar script: `generate_l32_excel.py`
2. Llenar las 23 hojas con datos reales
3. Incluir costos directos e indirectos
4. Formato profesional con precios en colones (₡)

### Paso 4: Generar HTML Interactivo
1. Usar script: `generate_html.py`
2. Dashboard con gráficos por área
3. Filtros por tipo de costo

## COMANDOS DE REFERENCIA

```bash
# Analizar plano con visión
python3 /root/.openclaw/workspace-abaco/skills/pdf-plan-analyzer/scripts/analyze_plan.py /root/.openclaw/workspace-abaco/data/ejemplos/Planos/Arquitectónico/A-100-PLANTAS-ARQUITECTONICAS-N1-Rev.0.pdf

# Generar Excel
python3 /root/.openclaw/workspace-abaco/skills/excel-generator/scripts/generate_l32_excel.py

# Generar HTML
python3 /root/.openclaw/workspace-abaco/skills/html-report/scripts/generate_html.py
```

## LÓGICA DE CÁLCULO DE PRESUPUESTO (de Jose - 2026-04-12)

### Estructura de Costos

```
COSTO DIRECTO (materiales + mano de obra + equipos)
    ↓
COSTOS INDIRECTOS (% del directo)
    - Administración: X%
    - Imprevistos: X%
    - Utilidad: X%
    ↓
COSTO DE VENTA (se agrega después)
    ↓
TOTAL PRESUPUESTO
```

### Sistema de Pesos (CORRECCIÓN - Jose 2026-04-12)

**IMPORTANTE:** El sistema de pesos NO aplica a todas las actividades.

**Regla correcta:**
- Solo las líneas que dicen **"GLOBAL"** en la columna de **UNIDAD** usan el sistema de pesos
- Las demás líneas muestran **cantidades reales** de materiales/actividades

**Tipos de unidades:**
| Tipo de Unidad | Comportamiento |
|----------------|----------------|
| `m³`, `kg`, `pza`, `jornada` | Cantidades REALES del material/actividad |
| `GLOBAL` | Escala con el peso × (área_nueva / área_base) |
| `FIJO` | Monto fijo que no cambia (ej: Pago Brenes) |

**Ejemplo:**
```
Concreto f'c 200  | m³    | 25.5 m³  ← cantidad real
Instalaciones prov | GLOBAL | 1 x peso  ← escala con área
Pago Brenes        | FIJO   | ₡85,000   ← siempre igual
```

### Rubros Fijos (NO escalan)

- **"Pago Brenes"** = monto FIJO por cada casa
- Nunca cambia con el área
- Se suma al final como rubro independiente

### Unidades Globales

- Hay líneas en el presupuesto que son **GLOBALES**
- No dependen del área
- Son fijas para toda la obra

### Resumen de Tipos de Rubros

| Tipo | Comportamiento |
|------|----------------|
| Proporcional al área | Se escala con peso × factor |
| Fijo por casa | Pago Brenes, global |
| Porcentual | Costos indirectos sobre directo |

---

## ENTREGABLES ESPERADOS

1. **Excel L.32 completo** con:
   - Hoja ANALISIS populated
   - Hoja DESGLOSE populated
   - Resumen Presupuesto con costos por m²
   
2. **HTML Interactivo** con:
   - Gráficos de costos por categoría
   - Filtros interactivos
   - Total en colones y dólares

---

_Ejecuta tu conocimiento. Genera el presupuesto completo._

---

## 🚨 LÓGICA DE CÁLCULO (Jose - 2026-04-12) - CRÍTICO

### 1. Costos Indirectos
- **Vienen en PORCENTAJES** del costo directo total
- Componentes:
  - Administración (%)
  - Imprevistos (%)
  - Utilidad (%)
- **Fórmula:** `indirectos = costo_directo_total × (admin% + imprev% + util%) / 100`

### 2. Costo de Venta
- **Se agrega DESPUÉS de los indirectos**
- Porcentaje típico: 3%
- **Fórmula:** `costo_venta = (directo + indirectos) × 3%`

### 3. Sistema de Pesos (Proporcionalidad por Área)
- Cada actividad tiene un **PESO** en el presupuesto base
- Cuando el plano tiene diferente área, el costo cambia **EN PROPORCIÓN** a ese peso
- **Fórmula:** `nuevo_costo = peso × (nueva_area / area_base)`
- **Área base del proyecto L.32:** 73.7 m²

### 4. Rubros Fijos (NO cambian con área)
- Ejemplo: **"Pago Brenes"**
- Son montos **FIJOS por cada casa**
- **Nunca se escalan con el área**
- Siempre se suman al final, después de todo lo demás

### 5. Unidades Globales
- Líneas en materiales/unidades que son **GLOBALES**
- **No dependen del área** - son fijas
- Ejemplos: conexiones principales, permisos, instalaciones base

### 6. Estructura del Presupuesto Final

```
1. COSTOS DIRECTOS (escalables con área)
   └─ Materiales, Mano de Obra, Equipos

2. COSTOS INDIRECTOS (% del directo)
   ├─ Administración (10%)
   ├─ Imprevistos (5%)
   └─ Utilidad (15%)

3. COSTO DE VENTA (% de directo + indirectos)
   └─ Típicamente 3%

4. RUBROS FIJOS (NO escalan)
   └─ Pago Brenes, permisos, etc.

═══════════════════════════════════════
TOTAL PRESUPUESTO = (1) + (2) + (3) + (4)

COSTO POR M² = TOTAL / Área_Total
```

### 7. Implementación en Script

El script `generate_l32_formulas.py` debe:
- ✅ Separar costos directos (escalables) de rubros fijos (no escalables)
- ✅ Calcular indirectos como % del directo total
- ✅ Agregar costo de venta después de indirectos
- ✅ Sumar rubros fijos al final
- ✅ Incluir fórmula de scaling: `nuevo_costo = peso × (nueva_area / 73.7)`
- ✅ Identificar unidades globales en la descripción del ítem
