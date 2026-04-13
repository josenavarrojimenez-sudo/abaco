# Lecciones Aprendidas - Ábaco

Repositorio de conocimiento y lecciones aprendidas del especialista en presupuestos inmobiliarios.

## Índice de Lecciones

1. [Enviar archivos por Telegram](#leccion-1-enviar-archivos-por-telegram)

---

## Lección 1: Enviar archivos por Telegram

**Fecha:** 2026-04-13  
**Contexto:** Tratando de enviar Excel de presupuesto al usuario José

### Problema
El usuario necesitaba recibir un archivo Excel generado, pero las instrucciones estándar del sistema no funcionaban.

### Intentos fallidos
1. `MEDIA:/ruta/absoluta/archivo.xlsx` - No funcionó
2. `MEDIA:./archivo.xlsx` - No funcionó
3. `read` tool con ruta relativa - Devolvía contenido binario en lugar de adjuntar
4. `openclaw message send` - Comandos fallaban con "unknown option"

### Solución correcta
Para enviar archivos como documentos adjuntos en Telegram:

```bash
# 1. Copiar archivo a carpeta outbound
mkdir -p ~/.openclaw/media/outbound
cp /ruta/al/archivo.xlsx ~/.openclaw/media/outbound/

# 2. En mensaje de respuesta, incluir:
MEDIA:/root/.openclaw/media/outbound/archivo.xlsx
```

### Key Points
- El archivo DEBE estar en `~/.openclaw/media/outbound/`
- La línea MEDIA: debe estar sola, sin texto adicional en esa línea
- La ruta debe ser absoluta
- No usar comillas ni espacios después de MEDIA:

### Referencias
- Issue relacionado: https://github.com/sipeed/picoclaw/issues/126
- Documentación OpenClaw: MEDIA: debe apuntar a archivo en outbound folder

---

*Ábaco - Especialista Presupuestos Inmobiliarios* 🏗️