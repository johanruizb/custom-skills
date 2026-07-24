---
name: pr-test-checklist
description: "Analiza cambios en uno o más Pull Requests y genera una checklist de pruebas manuales para validar la aplicación. Revisa el diff real y el código fuente para producir tests accionables, trazables y libres de suposiciones. No hace regresión completa — solo valida lo que cambió y sus efectos directos."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, pull-requests, checklist, qa, manual-testing, code-review, github]
    related_skills: [issue-enrichment, investigate-before-edit, requesting-code-review, test-suite-improver, systematic-debugging]
---

# PR Test Checklist

## Overview

Cuando uno o más Pull Requests llegan para revisión, el equipo necesita saber qué probar manualmente — qué vistas abrir, qué flujos ejercitar, qué casos borde verificar. Hacerlo de memoria o leyendo solo el título del PR produce validaciones incompletas y bugs en producción.

Este skill analiza los cambios reales de cada PR (diff, archivos modificados, código fuente afectado) y genera una checklist de pruebas manuales organizada por módulo, con enlaces navegables a las vistas cuando es posible generarlos. Cada ítem de la checklist es trazable al PR que lo originó y está respaldado por evidencia del código — no por suposiciones.

El entregable es un documento Markdown listo para que un QA o desarrollador ejecute las pruebas sin haber leído el código.

## When to Use

- El usuario pide "generar checklist de pruebas", "crear plan de testing para este PR", "qué tengo que probar de este cambio", o equivalente.
- Llegan uno o varios PRs y se necesita una guía de pruebas manuales antes de hacer merge.
- Se quiere validar que los cambios no rompen flujos adyacentes sin hacer una regresión completa.
- El usuario quiere traceabilidad: saber exactamente qué prueba cubre qué cambio de qué PR.

Don't use for:
- Escribir tests automatizados (unitarios, integración, e2e) — para eso usar `test-suite-improver` o `test-driven-development`.
- Hacer code review del PR — para eso usar `requesting-code-review`.
- Depurar un bug específico reportado en un PR — usar `systematic-debugging`.
- Generar documentación de la aplicación completa — esto es una checklist de validación de cambios, no un manual de usuario.

## Input

Aceptar los PRs a analizar desde una de estas fuentes, en orden de prioridad:

1. **Número de PR** — `gh pr view <num>` y `gh pr diff <num>`.
2. **URL del PR** — extraer el número y repo, luego `gh pr view`.
3. **Rama local** — si el usuario indica una rama, usar `gh pr list --head <rama>` para encontrar el PR asociado.
4. **Lista explícita** — el usuario pasa varios números de PR separados por coma o espacio.

Si el usuario no especifica qué PRs analizar, preguntar. No asumir "el PR más reciente" o "la rama actual".

### Información que el usuario debe proporcionar

Hay datos que el skill no puede inferir del código ni de GitHub. Preguntar al usuario cuando sean necesarios:

- **URL base del entorno de testing** (ej. `https://test.miapp.com`). Sin esto no se pueden generar enlaces navegables.
- **Credenciales y roles** necesarios para probar ciertos flujos (ej. "admin", "usuario con permiso X"). El skill los lista como prerequisitos; el usuario debe proporcionar los valores concretos.
- **IDs dinámicos** para URLs que requieren un registro existente (ej. `{usuarioId}`). Si el usuario no los proporciona, dejar el placeholder.
- **PRs a analizar** si no los proporcionó en el input inicial.

No inventar URLs, rutas, permisos, datos de prueba, ni comportamientos que no estén respaldados por el código o por la información proporcionada por el usuario.

## Phase 1: Recolección de datos de los PRs

Para cada PR a analizar:

1. **Obtener metadatos del PR** con `gh pr view <num>`. Registrar: título, descripción, autor, rama base, etiquetas, milestone, y — críticamente — todos los comentarios del PR (`gh pr view <num> --comments`). Los comentarios frecuentemente contienen decisiones de diseño, cambios de alcance, bugs encontrados durante la revisión, o notas del autor que afectan qué debe probarse.

2. **Obtener el diff completo** con `gh pr diff <num>`. Analizar:
   - Archivos agregados, modificados y eliminados.
   - Líneas cambiadas, insertadas y eliminadas por archivo.
   - Naturaleza del cambio: nueva funcionalidad, bug fix, refactor, cambio de configuración, migración, cambio de dependencias.

3. **Clasificar los archivos modificados** en categorías:
   - **Frontend**: componentes, páginas, rutas, hooks, estilos, assets.
   - **Backend**: modelos, vistas/controladores, serializers, servicios, migraciones, configuración.
   - **Infraestructura**: CI/CD, Docker, configs de deploy, variables de entorno.
   - **Dependencias**: cambios en `package.json`, `requirements.txt`, `Cargo.toml`, etc.
   - **Documentación**: README, docs, comentarios.

4. **Identificar los módulos/funcionalidades afectados** a partir de:
   - Las rutas de los archivos (ej. `src/modules/usuarios/` → módulo Usuarios).
   - Los nombres de componentes/vistas modificados.
   - Las entidades/modelos afectados.
   - Los endpoints de API tocados.

**Criterio de finalización:** Cada PR tiene registrados sus metadatos, diff completo, archivos clasificados por categoría, y módulos identificados. Los comentarios del PR fueron leídos.

### Fallback cuando `gh` no está disponible

Si `gh` no está instalado o no está autenticado, usar la API de GitHub:

```bash
curl -s https://api.github.com/repos/{owner}/{repo}/pulls/{num}
curl -s https://api.github.com/repos/{owner}/{repo}/pulls/{num}/files
curl -s -H "Accept: application/vnd.github.v3.diff" https://api.github.com/repos/{owner}/{repo}/pulls/{num}
curl -s https://api.github.com/repos/{owner}/{repo}/issues/{num}/comments
```

Si ninguna de las dos opciones funciona, pedir al usuario que proporcione el diff (pegado o como archivo) y los metadatos del PR.

## Phase 2: Análisis del código fuente

El diff muestra qué cambió, pero no por qué ni cómo funciona el contexto alrededor. Esta fase investiga el código fuente real para entender el impacto de los cambios.

### 2.1 Leer los archivos modificados

Para cada archivo en el diff que no sea de configuración ni documentación, leer el archivo completo (o las secciones relevantes). El diff solo muestra líneas cambiadas; el archivo completo revela:

- Qué hace la función/clase/componente completo donde ocurrió el cambio.
- Qué imports y dependencias tiene.
- Cómo se relaciona con el resto del sistema.

No asumir comportamiento por el nombre del archivo o la función. Leer.

### 2.2 Trazar el flujo afectado

Para cada cambio significativo, seguir la traza de ejecución:

- **Frontend**: componente → hook/proveedor → llamada API → estado → renderizado. Identificar qué ruta muestra ese componente, qué props recibe, qué interacciones de usuario disparan el código cambiado.
- **Backend**: request → middleware → vista/controlador → serializador/validador → modelo → respuesta. Identificar el endpoint, método HTTP, parámetros, permisos requeridos.
- **Full-stack**: cuando un PR toca frontend y backend, trazar el flujo completo para verificar que ambos lados del contrato son consistentes.

### 2.3 Identificar rutas y vistas

Buscar las rutas que exponen los componentes/vistas modificados:

- **React Router / Vue Router / Angular Router**: buscar archivos de rutas, identificar el path y los parámetros de URL.
- **Next.js**: estructura de `pages/` o `app/`.
- **Backend**: `urls.py`, `routes.rb`, `web.php`, anotaciones de controladores.
- **API**: endpoints REST o GraphQL afectados.

Para cada vista identificada, construir la URL de testing si el usuario proporcionó la URL base. Formato: `{url_base}/{ruta}` con placeholders `{parametro}` para IDs dinámicos.

### 2.4 Identificar permisos y autorización

Revisar:

- Decoradores de permisos (Django: `@permission_required`, DRF: `permission_classes`).
- Middleware de autenticación/autorización.
- Guards en frontend (rutas protegidas, condiciones de renderizado basadas en roles).
- Lógica condicional que depende del rol o permisos del usuario.

Cada permiso identificado se convierte en un caso de prueba: "usuario sin permiso X no debería poder acceder".

### 2.5 Identificar validaciones y edge cases

Revisar:

- Validadores de formularios/serializers (campos requeridos, formatos, rangos, unicidad).
- Manejo de errores (try/catch, estados de error en frontend, mensajes de error).
- Estados vacíos (listas sin datos, campos nulos, relaciones vacías).
- Casos borde en la lógica de negocio: valores límite, entradas inválidas, condiciones de carrera visibles desde UI.
- Integraciones externas: si el cambio toca una llamada a API externa, verificar qué sucede cuando falla.

**Solo incluir edge cases que el código realmente contemple o que el cambio hace probables.** No inventar escenarios hipotéticos.

### 2.6 Evaluar blast radius

Buscar referencias a los símbolos/archivos/componentes modificados en el resto del código. Un cambio en una función utilitaria puede afectar docenas de callers. Identificar qué otros módulos o vistas dependen del código cambiado — esas vistas también deben probarse.

**Criterio de finalización:** Para cada PR, se entiende el flujo completo afectado, las rutas/vistas están identificadas con sus URLs, los permisos y validaciones están documentados, y el blast radius está evaluado.

## Phase 3: Generación de la checklist

### Principios de generación

Cada ítem de la checklist debe ser:

1. **Trazable**: incluye referencia al PR que lo originó.
2. **Accionable**: un tester que no ha leído el código debe poder ejecutarlo.
3. **Específico**: describe la acción concreta, la vista donde se ejecuta, y el resultado esperado.
4. **Basado en evidencia**: todo lo que afirma viene del diff o del código fuente leído. Nada inventado.
5. **Acotado**: solo pruebas relacionadas con los cambios detectados y sus efectos directos. Se asume que la funcionalidad previa funcionaba correctamente — esto es validación de cambios, no regresión completa.

### Estructura de la checklist

Organizar por módulo/funcionalidad. Dentro de cada módulo, agrupar por vista o flujo. Priorizar: flujos de alto impacto/riesgo primero, luego casos complementarios.

```markdown
# Checklist de Pruebas — PRs #[nums]

**Entorno:** {URL base proporcionada por el usuario}
**PRs analizados:** #123, #456
**Fecha:** {fecha de generación}

> ⚠️ **Instrucciones:** Las pruebas marcadas 🔴 son obligatorias (cubren cambios críticos o de alto riesgo). Las marcadas 🟡 son recomendadas (casos borde o verificaciones complementarias).

---

## Módulo: {Nombre del módulo}

### Vista: {Nombre de la vista}

**URL:** `{url_base}/{ruta}`
**Origen:** PR #{num} — {descripción breve del cambio}

**Prerequisitos:**
- {rol/permiso necesario}
- {dato o estado previo necesario}

#### 🔴 Obligatorias

- [ ] **{Acción}**: {Descripción precisa de lo que el tester debe hacer.}  
  **Resultado esperado:** {Qué debe observar el tester.}

- [ ] **{Otra acción}**: {Descripción.}  
  **Resultado esperado:** {Qué debe observar.}

#### 🟡 Recomendadas

- [ ] **{Acción}**: {Descripción.}  
  **Resultado esperado:** {Qué debe observar.}

---

## Módulo: {Otro módulo}
...
```

### Clasificación de severidad

- 🔴 **Obligatorias**: cambios en lógica de negocio, permisos, validaciones, flujos de datos, integraciones, endpoints de API. Si estas pruebas fallan, el PR no debería hacer merge.
- 🟡 **Recomendadas**: casos borde, estados vacíos, pruebas de regresión en vistas adyacentes afectadas por el blast radius, verificaciones de UI/estilos, pruebas con diferentes roles cuando el cambio no toca permisos directamente.

### Contenido de cada ítem

Para cada ítem, incluir cuando aplique:

| Campo | Descripción |
|---|---|
| **Módulo/funcionalidad** | Área de la aplicación |
| **Vista/ruta** | Dónde se ejecuta la prueba |
| **URL** | Enlace directo a la vista (con placeholders si faltan IDs) |
| **Prerequisitos** | Rol, datos, estado previo necesario |
| **Acción** | Qué hace el tester, paso a paso si es necesario |
| **Resultado esperado** | Qué debe observar |
| **Edge cases** | Variaciones de la misma prueba (diferentes inputs, roles, estados) |
| **Origen** | PR que motiva esta prueba |

No incluir campos que no tengan información — un ítem no necesita los 8 campos si solo 4 aplican.

### Filtrado de calidad

Antes de dar la checklist por terminada, revisar cada ítem contra estos criterios:

- ¿Está respaldado por evidencia del diff o del código? Si no, eliminar.
- ¿Es genérico o redundante? Tests como "probar que la página carga", "verificar que no hay errores en consola" sin relación concreta con un cambio → eliminar o reformular con especificidad.
- ¿Es una regresión no relacionada? "Probar el login", "probar el registro" cuando el PR no toca auth → eliminar. Solo efectos directos.
- ¿Podría ejecutarlo alguien que no leyó el código? Si la acción es ambigua ("revisar el módulo de usuarios"), reformular con instrucciones concretas.

**Criterio de finalización:** La checklist está completa, organizada por módulo, cada ítem tiene trazabilidad al PR de origen, no hay ítems genéricos ni inventados, las URLs son correctas (o usan placeholders documentados), y la clasificación obligatoria/recomendada es consistente.

## Phase 4: Revisión con el usuario

1. **Presentar la checklist** al usuario para revisión. Destacar:
   - Cantidad de pruebas generadas (obligatorias y recomendadas).
   - PRs cubiertos.
   - Módulos identificados.
   - Cualquier limitación (ej. "no se pudo determinar la URL del módulo X porque no se encontró el archivo de rutas", "los placeholders `{id}` necesitan ser reemplazados por IDs reales del entorno de testing").

2. **Recoger feedback** del usuario:
   - ¿Faltan pruebas que el usuario considera necesarias?
   - ¿Sobra alguna prueba que no aplica?
   - ¿Los placeholders necesitan valores concretos?
   - ¿El nivel de detalle es adecuado?

3. **Iterar** si el usuario pide ajustes.

4. **Formato de entrega final** — preguntar al usuario:
   - ¿Escribir la checklist a un archivo Markdown? (ej. `pr-test-checklist-{nums}.md`)
   - ¿Publicar como comentario en el PR? (usar `gh pr comment <num> --body-file`)
   - ¿Entregar solo en la conversación?

No publicar en GitHub sin confirmación explícita del usuario.

**Criterio de finalización:** El usuario revisó y aprobó la checklist, o pidió ajustes que fueron aplicados. El formato de entrega está definido y ejecutado.

## Common Pitfalls

1. **Generar tests basados solo en el título/descripción del PR.** El título dice "Agregar filtro por fecha" pero el diff muestra que también se modificó la paginación. Sin leer el diff y el código, la checklist estaría incompleta. Siempre leer el diff completo y los archivos modificados.

2. **Inventar URLs, rutas o comportamientos.** Si no se encontró el archivo de rutas, no asumir que la URL es `/usuarios/{id}/editar`. Usar placeholders y documentar la limitación. Si el código no muestra un cierto comportamiento, no afirmar que existe.

3. **Incluir tests genéricos no relacionados con los cambios.** "Verificar que el login funciona" no pertenece a la checklist de un PR que cambió el formato de fechas en un reporte. Cada ítem debe trazarse a un cambio concreto en el diff.

4. **Convertir la checklist en una regresión completa.** El objetivo es validar cambios, no re-verificar toda la aplicación. Si el PR toca 3 archivos en el módulo de Reportes, la checklist cubre Reportes y los módulos que dependen de él, no los 20 módulos de la aplicación.

5. **No leer los comentarios del PR.** Los comentarios frecuentemente contienen información crítica: "esto solo aplica para usuarios admin", "el cambio de UI es solo para mobile", "quité la validación X porque Y". Sin leerlos, la checklist puede incluir pruebas para comportamientos que ya no existen u omitir casos que los revisores pidieron.

6. **Asumir permisos o roles sin verificarlos en el código.** "Probablemente solo admin puede acceder" no sirve. Leer los decoradores de permisos, guards, o middleware. Si el código no muestra restricción de permisos, no inventarla.

7. **No preguntar cuando falta información.** Si la URL base del entorno de testing no se proporcionó, preguntar. Si se necesita un ID de usuario de prueba, preguntar. Una checklist llena de placeholders sin valores es menos accionable que una donde el usuario proporcionó los datos.

8. **Generar pruebas redundantes.** Dos ítems que describen esencialmente la misma acción con el mismo resultado esperado confunden al tester. Consolidar o eliminar el redundante.

9. **No verificar el blast radius.** Un cambio en una función utilitaria como `formatDate()` puede afectar 15 vistas. Si solo se genera la prueba para la vista mencionada en el PR, las otras 14 no se validan. Buscar referencias.

10. **Omisión del análisis de frontend cuando el PR toca backend (y viceversa).** Un cambio en el serializador de la API puede romper el contrato con el frontend. Un cambio en un componente puede asumir un campo que el backend no envía. Siempre verificar ambos lados cuando el proyecto es full-stack.

11. **Checklist demasiado vaga.** "Probar que el filtro funciona" no le dice al tester qué filtro, con qué valores, dónde, y qué esperar. "En la vista de Reportes, seleccionar filtro 'Desde' con fecha 2024-01-01 y 'Hasta' con 2024-12-31. Verificar que la tabla muestra solo registros en ese rango." es accionable.

12. **No clasificar por severidad (obligatorio vs recomendado).** Si todas las pruebas se presentan con igual peso, el tester no sabe por dónde empezar ni qué es bloqueante para el merge.

## Verification Checklist

- [ ] PRs identificados: números, títulos, autores, ramas registrados
- [ ] Comentarios de cada PR leídos y considerados
- [ ] Diff de cada PR analizado: archivos modificados, agregados, eliminados
- [ ] Archivos clasificados por categoría (frontend, backend, infra, dependencias, docs)
- [ ] Módulos y funcionalidades afectados identificados a partir de rutas de archivos
- [ ] Código fuente de archivos modificados leído (no solo el diff)
- [ ] Flujo de ejecución trazado para cada cambio significativo (frontend: componente→API, backend: request→respuesta)
- [ ] Rutas y vistas identificadas con paths y parámetros de URL
- [ ] URLs de testing construidas (con placeholders cuando faltan datos)
- [ ] Permisos y reglas de autorización verificados en el código
- [ ] Validaciones y edge cases identificados a partir del código
- [ ] Blast radius evaluado (referencias a símbolos modificados en todo el código)
- [ ] Información faltante solicitada al usuario (URL base, credenciales, IDs, PRs)
- [ ] Checklist generada organizada por módulo con enlaces navegables
- [ ] Cada ítem trazable a un PR de origen
- [ ] Ítems clasificados como 🔴 obligatorios o 🟡 recomendados con criterio consistente
- [ ] Sin ítems genéricos, redundantes o no relacionados con los cambios
- [ ] Sin datos inventados (URLs, permisos, comportamientos, datos de prueba)
- [ ] Checklist revisada por el usuario y ajustes aplicados
- [ ] Formato de entrega definido y ejecutado (archivo, comentario en PR, o conversación)
