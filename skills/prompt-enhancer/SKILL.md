---
name: prompt-enhancer
description: "Mejora prompts para claridad, estructura y accionabilidad."
version: 1.2.0
author: johanruizb, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompts, rewriting, clarity, ai-assistance, communication]
    related_skills: []
---

# Prompt Enhancer Skill

Transforma ideas, notas rápidas o prompts mal redactados en prompts claros, accionables y útiles para cualquier IA. No cambia la intención original — solo mejora claridad, estructura y precisión. No corrige gramática pura ni traduce prompts.

## When to Use

- User asks to "mejorar este prompt", "reescribir prompt", "hacer más claro", "pulir prompt".
- User sends a raw idea, note, or rough draft and wants it turned into a usable prompt.
- User needs variations of a prompt (more direct, more technical, more detailed).

Don't use for:
- Corrección gramatical pura sin mejora de estructura.
- Traducción de prompts.
- Generación de contenido que no sea un prompt.

## Core Rules

Aplicar en orden antes de generar cualquier salida:

1. **Entender la intención principal.** Extraer qué quiere lograr el usuario. Si la intención es ambigua, elegir la interpretación más probable y anotarlo en Suposiciones.

2. **Conservar el significado.** No inventar requisitos, no añadir funcionalidad no pedida, no cambiar el objetivo. Lo que el usuario no dijo, no se asume.

3. **Mejorar claridad y precisión.** Eliminar ambigüedad, frases redundantes, rodeos. Cada oración debe aportar información accionable.

4. **Convertir vaguedades en instrucciones concretas.** "Hazlo bonito" → "Usa paleta monocromática con sombras sutiles, espaciado de 16px y tipografía sans-serif". "Que funcione bien" → "Debe manejar hasta 1000 registros sin degradación, responder en <200ms y mostrar un estado de carga".

5. **Estructurar en secciones cuando ayude.** Para prompts complejos: Objetivo, Contexto, Requisitos, Restricciones, Criterios de aceptación, Entregables. Para prompts simples, una versión directa sin secciones es mejor.

6. **Ajustar el tono según contexto:**
   - **Desarrollo de software:** técnico, preciso, con restricciones, alcance y criterios de aceptación.
   - **UI/UX:** consistencia visual, jerarquía, espaciado, alineación, interacción, coherencia con el sistema existente.
   - **Análisis:** objetivos, contexto, pasos de revisión y entregables esperados.
   - **Creativo/General:** tono natural, descriptivo, con margen para interpretación.

7. **No sobrecomplicar.** Si el prompt original ya es claro con 3 líneas, no lo conviertas en 20.

8. **Preservar términos técnicos.** Nombres de componentes, rutas, variables, IDs, URLs, comandos — se conservan exactamente como el usuario los escribió.

9. **Resolver ambigüedad con herramientas antes de entregar.** Si falta información importante, agregar "Suposiciones" al final. Si hay múltiples interpretaciones razonables y la ambigüedad es crítica (cambia el resultado de forma significativa), usar la herramienta `clarify` para preguntar al usuario antes de entregar. Si `clarify` no está disponible o el usuario pide entrega inmediata, incluir "Preguntas opcionales" para que refine después.

10. **Entregar listo para copiar y pegar.** El resultado debe ser autocontenido, sin necesidad de edición adicional.

## Tool Usage

- Usar `clarify` cuando la ambigüedad del prompt original sea crítica y haya múltiples interpretaciones razonables que cambian el resultado.
- No usar `clarify` para ambigüedades menores que se resuelven con una suposición documentada.
- Si `clarify` no está disponible, documentar Suposiciones y Preguntas opcionales en la respuesta.

## Response Format

Entregar en este orden:

1. **Versión mejorada** — el prompt reescrito, listo para usar.
2. **Versión alternativa** (si aplica) — más directa, más técnica, o con enfoque distinto. Omitir si el original ya es óptimo en un solo enfoque.
3. **Suposiciones** (si aplica) — breve lista de lo asumido para resolver ambigüedades.
4. **Preguntas opcionales** (si aplica) — preguntas concretas cuya respuesta mejoraría el prompt significativamente.

Regla de idioma: si el prompt original está en español, responder en español. Si está en inglés, responder en inglés.

## Example

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

## Pitfalls

- **Over-engineering prompts simples.** Un prompt de 3 líneas no necesita 5 secciones. Si la versión directa es clara, entrégala sin más.
- **Inventar requisitos por "ayudar".** Añadir features, tecnologías o criterios que el usuario no mencionó cambia la intención. Lo que no dijo, no se asume.
- **Asumir demasiado en lugar de preguntar.** Si la ambigüedad cambia el resultado de forma significativa, usar `clarify` en vez de elegir una interpretación y seguir. Las suposiciones son para ambigüedades menores, no para decisiones de diseño.
- **Stripping jargon que parece vago pero es preciso.** Términos domain-specific que el usuario usó pueden ser exactamente correctos en su contexto — preservarlos.
- **Ignorar el idioma del original.** Responder en inglés cuando el prompt estaba en español (o viceversa) rompe la utilidad para el usuario.
- **Sobre-especificar hasta hacer el prompt single-use.** Si el usuario quería una plantilla reutilizable, no la conviertas en un prompt que solo sirve para un escenario narrow.

## Verification

- [ ] Intención principal del prompt original entendida y conservada.
- [ ] Sin requisitos inventados.
- [ ] Términos técnicos preservados tal cual.
- [ ] Estructura con secciones solo si aporta claridad.
- [ ] Tono ajustado al contexto (técnico, diseño, análisis, general).
- [ ] Versión alternativa incluida si aporta valor.
- [ ] Suposiciones documentadas si hubo ambigüedad.
- [ ] `clarify` usado cuando la ambigüedad era crítica (o se documentó por qué no).
- [ ] Resultado listo para copiar y pegar.
- [ ] Idioma de respuesta coincide con idioma del prompt original.