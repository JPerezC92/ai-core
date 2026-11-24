# debt-050-oxlint-warnings

> **Status:** closed
> **Closed:** 2026-11-24
> **Disposition:** cancelled
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-16
> **Objective:** Resolver los nueve warnings type-aware de Oxlint que mantenían incumplido R8, mediante correcciones reales y mínimas, marcar R8 y retirar DEBT-050 en un único commit atómico.
> **Branch:** `feat/tooling/lint-and-format-adoption`, base `1a30e59` sobre `main` en `6e6d19b66ed43859ab605d5c363eb2d025198d84`.
> **Delivery:** Un slice coherente: seis reescrituras `[...x]` → `Array.from(x)`, tres correcciones `no-base-to-string`, nueve casos de prueba, el tick de R8 y el retiro de DEBT-050. Forecast de líneas propias añadidas+borradas: ~120.
> **Runner:** `pnpm verify:full`

## Specs

- S1 — El repositorio no reporta ningún warning de lint. Exact requirement: "Oxlint type-aware debe reportar cero errores y cero warnings." Acceptance: ejecutar `pnpm lint` y observar salida vacía.
- S2 — Las seis correcciones `no-misused-spread` preservan el comportamiento. Exact requirement: "para `no-misused-spread`, determina si la operación propuesta conserva el comportamiento, especialmente el procesamiento Unicode y la semántica de iteración." Acceptance: comparar `Array.from(x)` con `[...x]` sobre un conjunto de cadenas que incluye caracteres astrales y observar elementos y longitud idénticos.
- S3 — Ningún warning se elimina desactivando reglas ni suprimiendo. Exact requirement: "No quiero desactivar reglas, introducir supresiones para ocultar advertencias ni cambiar contratos funcionales únicamente para conseguir un lint limpio." Acceptance: inspeccionar `.oxlintrc.json` y el código cambiado y observar que no se añadió ninguna supresión ni exclusión.
- S4 — El mensaje de `clearance.ts` conserva la representación de los primitivos y rinde las estructuras explícitamente. Exact requirement: "Conserva el comportamiento de validación. Preserva la representación existente de valores primitivos. Utiliza una representación JSON para estructuras compatibles cuando sea apropiado." Acceptance: ejecutar las pruebas de primitivo, mapping y lista y observar los textos esperados.
- S5 — Los campos escalares de `records.ts` rechazan valores no escalares nombrando el campo. Exact requirement: "Si el contrato confirma que los valores no escalares son inválidos, implementa el rechazo con un mensaje claro que identifique el campo incorrecto". Acceptance: ejecutar las pruebas de mapping, lista y `Date` y observar el `InputError` con el nombre del campo.
- S6 — Existen pruebas de regresión dirigidas para cada corrección. Exact requirement: "Añade pruebas de regresión dirigidas cuando sean necesarias." y "Añade el caso mínimo de regresión con una cola Unicode astral en `scan.test.ts`, aprovechando los tests existentes." Acceptance: ejecutar la suite de cada paquete afectado y observar los casos nuevos en verde.
- S7 — Las verificaciones de la solución pasan. Exact requirement: "Ejecuta Oxlint con type-aware. Ejecuta los typechecks afectados. Ejecuta las pruebas de los paquetes modificados. Ejecuta `pnpm verify:full` cuando corresponda." Acceptance: ejecutar `pnpm verify:full` y observar código 0.
- S8 — Una revisión independiente cubre los cambios funcionales y sus contratos. Exact requirement: "Una revisión independiente debe comprobar los cambios funcionales y sus contratos." Acceptance: leer el veredicto de la revisión y observar que no deja hallazgos abiertos.
- S9 — R8 se marca solo después de verificar sus criterios originales, sin reescribirlos. Exact requirement: "Verifica el criterio original de R8 antes de marcarlo como cumplido." y "No modifiques los criterios originales de R8 ni los de DEBT-050 para justificar su cumplimiento." Acceptance: leer R8 en el archivo durable y observar su texto sin cambios y su casilla marcada.
- S10 — DEBT-050 se retira con su evidencia en el mismo commit que la implementación. Exact requirement: "No retires DEBT-050 hasta el commit autorizado que incluya tanto la implementación como el cierre de la deuda." Acceptance: inspeccionar el commit y observar que contiene el código, las pruebas y el retiro de la entrada.

## Tasks

- T1 | S2, S3 | inline (seis reescrituras mecánicas con equivalencia demostrable) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T2 | S1, S3 | inline (una corrección en test con estrechamiento de tipo) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T3 | S4 | inline (representación explícita en un mensaje de error) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T4 | S5 | inline (rechazo tipado con verificación previa de contrato) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T5 | S6 | inline (tres archivos de prueba, nueve casos) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T6 | S7, S8 | delegated (revisión independiente del diff funcional) — Inquisitor 🔎 (PR Reviewer) | in progress | commit: pending
- T7 | S9, S10 | inline (tick de R8 y retiro de la deuda con evidencia) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending

## Log

- L1 — Pedido original, verbatim:

  ```
  Acepto el cierre de DEBT-051 y el commit `1a30e59`.

  Continuaremos resolviendo las deudas técnicas una por una. La siguiente es **DEBT-050 — Nine Oxlint warnings**.

  ## Objetivo

  Eliminar los nueve warnings que mantienen R8 incumplido, mediante correcciones reales y mínimas, preservando el comportamiento del código.

  No quiero desactivar reglas, introducir supresiones para ocultar advertencias ni cambiar contratos funcionales únicamente para conseguir un lint limpio.

  ## 1. Investigar los nueve warnings

  Obtén el inventario exacto, incluyendo:

  - Archivo y línea.
  - Regla de Oxlint.
  - Código que origina la advertencia.
  - Tipo real de los valores involucrados.
  - Causa técnica.
  - Solución propuesta.
  - Posibles cambios de comportamiento.

  Separa el análisis de los seis `no-misused-spread` y los tres `no-base-to-string`.

  No asumas que todos los warnings de una misma regla tienen la misma solución.

  ## 2. Implementación

  Autorizo correcciones locales, mínimas y demostrablemente seguras.

  Para `no-misused-spread`, determina si la operación propuesta conserva el comportamiento, especialmente el procesamiento Unicode y la semántica de iteración.

  Para `no-base-to-string`, identifica los contratos de los mensajes y los tipos reales. No sustituyas automáticamente las conversiones por `JSON.stringify()` ni modifiques información observable.

  Añade pruebas de regresión dirigidas cuando sean necesarias.

  Si alguna corrección requiere modificar un contrato funcional, no la implementes todavía. Preséntame el problema, las alternativas y sus consecuencias.

  Evita refactorizaciones y abstracciones innecesarias.

  ## 3. Validaciones

  Después de aplicar las correcciones seguras:

  - Ejecuta Oxlint con type-aware.
  - Ejecuta los typechecks afectados.
  - Ejecuta las pruebas de los paquetes modificados.
  - Ejecuta `pnpm verify:full` cuando corresponda.
  - Comprueba que las correcciones no introducen warnings nuevos.

  Solicita una revisión independiente del diff de DEBT-050 antes de recomendar su cierre.

  ## 4. Gestión de la deuda

  Mantén DEBT-050 abierta hasta que se cumplan sus criterios originales de resolución.

  Si se eliminan los nueve warnings y se demuestra que las correcciones son válidas, comprueba si R8 puede marcarse como cumplido sin modificar sus criterios.

  No retires DEBT-050 hasta el work unit autorizado que incluya el cierre y la implementación.

  ## 5. Restricciones

  - Trabaja únicamente en DEBT-050.
  - No modifiques DEBT-049 ni DEBT-052.
  - No reabras DEBT-051 sin una regresión demostrada.
  - No reformatees masivamente el repositorio.
  - No modifiques TISMART ni proyectos destino.
  - Herald es el único agente autorizado para operaciones Git/GitHub.
  - No crees commits, pushes ni PR sin autorización.

  Al finalizar, quiero ver cuántos warnings se resolvieron, qué cambios se hicieron, qué pruebas pasaron y si queda alguna decisión funcional pendiente.

  **Prioriza la solución más sencilla que preserve el comportamiento.**
  ```

- L2 — Decisión del usuario sobre los dos warnings restantes, verbatim:

  ```
  He revisado los resultados de DEBT-050. Acepto las siete correcciones implementadas y quiero resolver los dos warnings restantes.

  ### Decisiones

  **1. clearance.ts — Opción A**

  Autorizo una representación explícita de valores no escalares en el mensaje de error.

  - Conserva el comportamiento de validación.
  - Preserva la representación existente de valores primitivos.
  - Utiliza una representación JSON para estructuras compatibles cuando sea apropiado.
  - Comprueba que la representación no introduzca errores nuevos ni exponga información que no debería incluirse en el diagnóstico.
  - Añade pruebas dirigidas para valores primitivos, objetos y arrays.

  No introduzcas un serializador genérico ni abstracciones innecesarias.

  **2. records.ts — Opción B, condicionada al contrato**

  Mi preferencia es rechazar objetos y arrays cuando un campo de `AnalysisHeader` requiere un valor escalar.

  Antes de implementarlo:

  - Verifica los contratos, fixtures y consumidores reales de `AnalysisHeader`.
  - Confirma qué tipos escalares están permitidos y cómo se tratan `null`, booleanos y números.
  - Comprueba la compatibilidad con los registros existentes y con la implementación Python anterior, cuando corresponda.
  - No cambies representaciones históricas por una supuesta mejora de paridad sin comprobar el contrato.

  Si el contrato confirma que los valores no escalares son inválidos, implementa el rechazo con un mensaje claro que identifique el campo incorrecto y añade pruebas de entradas válidas e inválidas.

  Si descubres que arrays u objetos son entradas legítimas o existe un contrato incompatible, detente exclusivamente en ese caso y presenta la evidencia antes de cambiar el comportamiento.

  ### Pruebas de las siete correcciones anteriores

  Añade el caso mínimo de regresión con una cola Unicode astral en `scan.test.ts`, aprovechando los tests existentes.

  No amplíes innecesariamente la suite.

  ### Condiciones para cerrar DEBT-050

  1. Oxlint type-aware debe reportar cero errores y cero warnings.
  2. Los tests afectados y typechecks deben pasar.
  3. `pnpm verify:full` debe pasar.
  4. Una revisión independiente debe comprobar los cambios funcionales y sus contratos.
  5. Verifica el criterio original de R8 antes de marcarlo como cumplido.
  6. No retires DEBT-050 hasta el commit autorizado que incluya tanto la implementación como el cierre de la deuda.

  No modifiques otras deudas ni realices refactorizaciones generales.

  No crees commits, pushes ni PRs todavía. Herald conserva la autoridad exclusiva sobre Git/GitHub.

  Al finalizar, informa si ambos warnings quedaron resueltos, qué cambios observables se introdujeron y qué pruebas demuestran que son correctos.
  ```

- L3 — Autorización del commit de cierre, verbatim:

  ```
  Acepto el resultado técnico de DEBT-050 y autorizo a Herald a crear el commit local de cierre.

  Antes de realizarlo, verifica que el conjunto de cambios incluya **la totalidad de la solución de DEBT-050**, no únicamente los dos últimos warnings.

  ### Alcance autorizado

  El commit debe incluir:

  1. Las seis correcciones de `no-misused-spread`.
  2. Las tres correcciones de `no-base-to-string`, incluyendo la realizada previamente en el test de system-one.
  3. Las tres nuevas pruebas de regresión y sus casos correspondientes.
  4. La actualización del requisito R8, marcándolo como cumplido únicamente tras verificar nuevamente sus criterios originales.
  5. El retiro formal de DEBT-050 del registro de deudas abiertas.
  6. La evidencia y el registro ODD correspondientes al cierre.

  El código, las pruebas y el retiro de la deuda deben formar **un único commit atómico**.

  ### Verificación de Herald

  Antes del staging y del commit:

  - Comprueba que los nueve warnings estén realmente eliminados.
  - Confirma que `pnpm verify:full` pasa sobre el contenido definitivo.
  - Verifica que la revisión independiente cubre los cambios funcionales relevantes.
  - Comprueba que no haya archivos ajenos a DEBT-050.
  - Preserva la evidencia histórica y la trazabilidad del cierre.
  - No modifiques los criterios originales de R8 ni los de DEBT-050 para justificar su cumplimiento.

  Documenta expresamente que `records.ts` ahora rechaza valores YAML no escalares y valores `Date` en los campos afectados.

  ### Estado de la feature

  Si los diez requisitos quedan satisfechos, actualiza el estado de `code-style-enforcement` conforme a las reglas reales del workflow ODD.

  No fuerces el cierre de tareas o registros si existen otros requisitos procedimentales pendientes.

  ### Restricciones

  - No modifiques DEBT-049 ni DEBT-052.
  - No reabras DEBT-051.
  - No realices cambios adicionales de arquitectura.
  - No modifiques TISMART ni proyectos destino.
  - Herald es el único autorizado para operaciones Git/GitHub.
  - **No hagas push, no abras un PR y no realices merge.**
  ```

- L4 — Inventario real re-medido antes de tocar código, separado por regla. Seis `no-misused-spread` en cinco archivos, todos `[...x]` sobre un `string` estático: `scan.ts:112` (columna de un hallazgo UTF-8), `feature_validation/domain/rules.ts:55` y `feature_file_validation/domain/rules.ts:46` (`decimalDigitsToAscii`), `feature_validation/domain/rules.ts:203` y `:364` (guarda de dígitos del Log), `cli/aicore/tests/support/core-sync-parity/tree.ts:217` (volcado de code points). Tres `no-base-to-string`: uno en un test de system-one sobre `BodyInit`, y dos donde el valor es genuinamente `unknown` (`clearance.ts` y `records.ts`). Se comprobó que los seis comparten causa pero que los tres no comparten solución.
- L5 — Equivalencia demostrada antes de corregir. `[...x]` y `Array.from(x)` consumen el mismo iterador de cadena; se compararon ocho muestras (ASCII, emoji astral, secuencia ZWJ, marca combinante, dígitos árabe-índicos, surrogate aislado, vacía) y en todas coincidieron elementos y longitud. El registro de deuda afirmaba que la única salida era segmentación por grafemas: era falso, y se corrigió en DEBT-050.
- L6 — Correcciones aplicadas y separadas por naturaleza. Las seis reescrituras son mecánicas y no cambian comportamiento. La del test de system-one estrecha el tipo del body antes de parsearlo, conservando lo que la prueba demuestra y mejorando el fallo si el body no fuese string. Para los dos sitios `unknown` se pidió decisión al usuario en lugar de improvisar, porque toda corrección cambiaba texto observable.
- L7 — Ambas decisiones implementadas con verificación de contrato previa. `clearance.ts` mantiene `String()` para primitivos y rinde JSON para estructuras. `records.ts` acepta solo `null` (`None`), booleanos (`True`/`False`), strings y números, y rechaza el resto nombrando el campo; el contrato se verificó antes de cambiarlo: los siete campos de `AnalysisHeader` son `readonly string`, las listas legítimas son solo `symptom_ids` y `known_problem_ids`, y `stringList` las maneja antes de `scalarText`. **Cambios observables, todos sobre entrada inválida o previamente mal manejada:** un mapping o una lista en un campo escalar ahora se rechazan en vez de convertirse en `[object Object]` o texto unido por comas, y un timestamp que la YAML 1.1 resuelve a `Date` —sello ISO completo con segundos, o fecha sin hora; la forma documentada `YYYY-MM-DDTHH:MM` sigue siendo string— ahora se rechaza con `found a Date value` en lugar de producir un timestamp que no coincidía y saltaba los chequeos de SLA.
- L8 — Pruebas de regresión añadidas, nueve casos: `cli/aicore/tests/unit/clearance.role-message.spec.ts` (primitivos, mapping, lista), `.agents/skills/incident-workflow/tests/unit/state-header-scalars.test.ts` (escalares aceptados, mapping y lista rechazados, `Date` nombrado, lista legítima intacta) y un caso de cola astral en `.agents/skills/op-skill-creator/tests/unit/scan.test.ts`. Se verificó que los casos de rechazo fallan contra el código anterior, es decir que discriminan.
- L9 — Revisión independiente en dos rondas sobre el diff funcional. Primera ronda `[ADVISORY]` con dos hallazgos: el diagnóstico llamaba «mapping» a cualquier objeto, y yo había arrastrado el conteo de archivos lintados sin re-medirlo. El primero se corrigió con un descriptor que nombra el tipo real, y el segundo se resolvió midiendo: 320 archivos. Su lectura de la librería era correcta en el fondo pero su ejemplo era impreciso, así que medí el parser en vez de aceptarlo: con YAML 1.1, `2099-01-01T00:00` es string y `2099-01-01T00:00:00Z` es `Date`. Segunda ronda **[PASS]**, cero hallazgos abiertos.
- L10 — Verificación final y cierre de la deuda. `pnpm lint` no emite nada (cero errores, cero warnings) sobre 320 archivos. R8 se marcó tras re-verificar sus dos conjunciones sin tocar su texto: toda regla activa pasa, y la convención de import aplica solo donde cada paquete ya la usa, porque los cuatro árboles usan subpath maps desde DEBT-051. La feature durable queda en `achieved` (10 de 10) por derivación de sus propias casillas. DEBT-050 se retira del registro abierto con su evidencia preservada aquí. No se cierra el registro de la adopción de tooling: su aceptación semántica de conjunto sigue pendiente y su entrega no está autorizada.

- L11 — Close: 2026-11-24 — The user authorized cancellation of the remaining historical verification and administrative closure work, verbatim: "I approve the four proposed closure entries and their cancelled dispositions." PR #192 delivered the corrections; that implementation is not cancelled or reverted. The recorded component checks and historical review remain as recorded. The later `pnpm verify:full` did not pass because of the two documented pre-existing formatting failures; the user accepted that S7 limitation. This closure does not claim literal S7 success or a new whole-record acceptance. PR #192 F2 remains an accepted ADVISORY.
