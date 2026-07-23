---
name: prompt-enhancer
description: "Reescribe y mejora prompts para hacerlos claros, accionables y útiles para ChatGPT, agentes de código, herramientas de diseño, análisis de producto o cualquier IA. Usa cuando el usuario pida mejorar, reescribir, clarificar o pulir un prompt."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompts, rewriting, clarity, ai-assistance, communication]
    related_skills: []
---

# Prompt Enhancer

## Overview

Esta skill transforma ideas, notas rápidas o prompts mal redactados en prompts claros, accionables y útiles para cualquier IA. No cambia la intención original, solo mejora la claridad, estructura y precisión.

## When to Use

- User asks to "mejorar este prompt", "reescribir prompt", "hacer más claro", "pulir prompt".
- User sends a raw idea, note, or rough draft and wants it turned into a usable prompt.
- User needs variations of a prompt (more direct, more technical, more detailed).

Don't use for:
- Corrección gramatical pura sin mejora de estructura.
- Traducción de prompts.
- Generación de contenido que no sea un prompt.

## Core Rules

Antes de generar cualquier salida, aplicar estas reglas en orden:

1. **Entender la intención principal.** Extraer qué quiere lograr el usuario con el prompt original. Si la intención es ambigua a pesar del contexto, elegir la interpretación más probable y anotarlo en Suposiciones.

2. **Conservar el significado.** No inventar requisitos, no añadir funcionalidad que el usuario no pidió, no cambiar el objetivo. Lo que el usuario no dijo, no se asume.

3. **Mejorar claridad y precisión.** Eliminar ambigüedad, frases redundantes, rodeos. Cada oración debe aportar información accionable.

4. **Convertir vaguedades en instrucciones.** "Hazlo bonito" → "Usa una paleta monocromática con sombras sutiles, espaciado de 16px y tipografía sans-serif". "Que funcione bien" → "Debe manejar hasta 1000 registros sin degradación, responder en <200ms y mostrar un estado de carga mientras procesa".

5. **Estructurar en secciones cuando ayude.** Para prompts complejos, usar secciones como: Objetivo, Contexto, Requisitos, Restricciones, Criterios de aceptación, Entregables. Para prompts simples, una versión directa sin secciones es mejor.

6. **Ajustar el tono según contexto:**
   - **Desarrollo de software:** técnico, preciso, con restricciones, alcance y criterios de aceptación.
   - **UI/UX:** enfocado en consistencia visual, jerarquía, espaciado, alineación, interacción y coherencia con el sistema existente.
   - **Análisis:** enfocado en objetivos, contexto, pasos de revisión y entregables esperados.
   - **Creativo/General:** tono natural, descriptivo, con margen para interpretación.

7. **No sobrecomplicar.** Si el prompt original ya es claro con 3 líneas, no lo conviertas en 20. La versión simple es válida.

8. **Preservar términos técnicos.** Nombres de componentes, rutas, variables, IDs, referencias, URLs, comandos — se conservan exactamente como el usuario los escribió.

9. **Manejar ambigüedad sin bloquear.** Si falta información importante, agregar una sección breve de "Suposiciones" al final del prompt, sin detener la entrega. Si la ambigüedad es crítica y hay múltiples interpretaciones razonables, incluir "Preguntas opcionales" para que el usuario refine.

10. **Entregar listo para copiar y pegar.** El resultado debe ser autocontenido, sin necesidad de edición adicional.

## Response Format

Entregar el resultado en este orden:

1. **Versión mejorada** — el prompt reescrito y pulido, listo para usar.

2. **Versión alternativa** (si aplica) — una segunda versión más directa, más técnica, o con un enfoque distinto. Si el prompt original ya es óptimo en un solo enfoque, omitir.

3. **Suposiciones** (si aplica) — breve lista de lo que se asumió para resolver ambigüedades.

4. **Preguntas opcionales** (si aplica) — preguntas concretas cuya respuesta mejoraría el prompt significativamente.

Regla de idioma: si el prompt original está en español, responder en español. Si está en inglés, responder en inglés.

## Ejemplo

**Prompt original:**
> necesito un script que lea csv y haga gráficos

**Versión mejorada:**
> Escribe un script en Python que lea un archivo CSV y genere gráficos a partir de sus datos.
>
> **Requisitos:**
> - Leer el archivo desde una ruta proporcionada como argumento.
> - Detectar automáticamente las columnas numéricas.
> - Generar un gráfico de líneas o barras por cada columna numérica.
> - Guardar los gráficos como PNG en un directorio `output/`.
> - Usar pandas y matplotlib.
>
> **Criterios de aceptación:**
> - Manejar archivos CSV con encoding UTF-8 y Latin-1.
> - Manejar valores nulos saltándolos sin romper.
> - Mostrar barra de progreso si el archivo tiene más de 1000 filas.

**Versión más técnica:**
> Python CLI script. Args: `--input <path>`, `--output <dir>`, `--format png|svg`. Lee CSV con pandas, columnas numéricas → matplotlib lineplot/barplot. Encoding: UTF-8 con fallback a Latin-1. Nulls → dropna por columna. >1000 filas → tqdm progress bar. Salida: PNG/SVG en output dir.

**Suposiciones:**
> - Se asume Python como lenguaje (por ser el más común para datos).
> - Se asume gráficos de líneas/barras. Si se requieren otros tipos (dispersión, pastel), especificar.

---

## Verification Checklist

- [ ] Intención principal del prompt original entendida y conservada.
- [ ] Sin requisitos inventados.
- [ ] Términos técnicos preservados tal cual.
- [ ] Estructura con secciones solo si aporta claridad.
- [ ] Tono ajustado al contexto (técnico, diseño, análisis, general).
- [ ] Versión alternativa incluida si aporta valor.
- [ ] Suposiciones documentadas si hubo ambigüedad.
- [ ] Resultado listo para copiar y pegar.
- [ ] Idioma de respuesta coincide con idioma del prompt original.
