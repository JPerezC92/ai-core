# debt-051-parent-relative-imports

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-16
> **Objective:** Eliminar los imports relativos padre de `mcp-servers/system-one` y `.opencode/plugins/odd-adviser` mediante Node subpath imports, y aplicar `import/no-relative-parent-imports` a los cuatro árboles fuente sin excepciones que oculten infracciones.
> **Branch:** `feat/tooling/lint-and-format-adoption`, base `8541d11` sobre `main` en `6e6d19b66ed43859ab605d5c363eb2d025198d84`.
> **Delivery:** Un solo slice coherente (84 líneas de specifier reescritas + 3 bloques de configuración + regla de lint) más la actualización del registro de deuda. Forecast de líneas propias añadidas+borradas: ~95, por debajo del umbral de estrategia. Sin commits: la autorización de esta intervención excluye crearlos.
> **Runner:** `pnpm verify:full`

## Specs

- S1 — Ningún specifier relativo padre permanece en los dos paquetes. Exact requirement: "La condición de aceptación es que no queden imports relativos padre en los paquetes donde la restricción aplica". Acceptance: ejecutar el escaneo acotado de statements sobre ambos árboles y observar 0 coincidencias en cada uno.
- S2 — La resolución de módulos se conserva en desarrollo, en ejecución y en los tests. Exact requirement: "Cada cambio debe conservar la resolución correcta del módulo tanto en desarrollo como en ejecución." Acceptance: ejecutar typecheck, la suite del paquete y una carga real del entry con Node y observar éxito en las tres.
- S3 — La regla de lint cubre todos los árboles de la convención y rechaza una infracción nueva. Exact requirement: "Quiero que la restricción `import/no-relative-parent-imports` se aplique a todos los paquetes cubiertos por el contrato arquitectónico." y "Comprueba que Oxlint detecte un import relativo padre introducido deliberadamente en una prueba aislada". Acceptance: introducir un import padre deliberado en cada árbol recién cubierto y observar error de la regla y código de salida distinto de cero.
- S4 — No cambian la lógica funcional, la API pública ni la disposición de directorios. Exact requirement: "No alteres la lógica funcional. No cambies la API pública de los paquetes innecesariamente. No reorganices directorios ni muevas módulos únicamente para eliminar imports." Acceptance: comparar las exportaciones de ambos entries antes y después y observar la misma superficie, sin ningún archivo movido.
- S5 — No se añaden dependencias. Exact requirement: "Evita introducir nuevas dependencias." Acceptance: inspeccionar los manifiestos y observar que ningún paquete declara una dependencia nueva.
- S6 — El trabajo permanece en la rama local existente y no crea commits, PR ni push. Exact requirement: "Mantén el trabajo en la rama local existente `feat/tooling/lint-and-format-adoption`" y "no crees nuevos commits, no publiques la rama, no abras un PR y no realices merge sin mi autorización". Acceptance: inspeccionar el estado del repositorio y observar la misma rama y el mismo HEAD que al inicio.
- S7 — DEBT-051 queda con evidencia concreta y DEBT-049 no se cierra automáticamente. Exact requirement: "Actualiza DEBT-051 con la evidencia concreta de las correcciones. Verifica su relación con DEBT-049. Cierra DEBT-051 únicamente si se cumplen sus criterios de resolución originales. No cierres DEBT-049 automáticamente". Acceptance: leer el registro de deuda y observar DEBT-051 con evidencia medida y una declaración explícita sobre DEBT-049.

## Tasks

- T1 | S3 | delegated (dictamen arquitectónico: el contrato y su alcance son del arquitecto) — Bastion 🧱 (Backend & Scripts Architect) | in progress | commit: pending
- T2 | S1, S2, S4, S5 | inline (transformación mecánica verificable en una sola pasada) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T3 | S1, S2, S4, S5 | inline (segundo paquete, solo tras verificar el primero) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T4 | S3 | inline (una línea de configuración con prueba de detección) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T5 | S2, S6 | inline (validación integral y frontera de rama) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T6 | S7 | inline (registro de deuda y evidencia gobernante) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending

## Log

- L1 — Pedido original: el alcance y los requisitos se resumen arriba en las Specs, y el mensaje completo del usuario se conserva verbatim en el bloque literal al final de esta entrada. «Quiero comenzar a resolver las deudas técnicas de AICore de forma individual. Empezaremos exclusivamente por DEBT-051 — Parent-relative imports en system-one y odd-adviser. No trabajes en DEBT-050 ni DEBT-052 durante esta intervención. […] Me pregunto si conviene prohibir los imports relativos padre de forma consistente, utilizando mecanismos de resolución de módulos apropiados para cada paquete. Si existe una contradicción con un contrato vigente, explícala antes de modificarlo. No redefinas silenciosamente la arquitectura.» El pedido completo fija además: verificar el contrato y pedir dictamen a Bastion; no asumir que cada línea es un import distinto; sustituir por aliases o package imports sin resolutores propios, sin dependencias nuevas, sin mover módulos y sin tocar la API pública; trabajar un paquete y verificar antes del segundo; aplicar la regla en todos los paquetes cubiertos y probar la detección con una infracción deliberada; ejecutar typecheck, lint, suites y `verify:full`; actualizar DEBT-051 sin cerrar DEBT-049; no crear commits, PR, push ni merge; no tocar TISMART ni destinos.

  Mensaje completo del usuario, verbatim:

  ```
  Quiero comenzar a resolver las deudas técnicas de AICore de forma individual. Empezaremos exclusivamente por **DEBT-051 — Parent-relative imports en system-one y odd-adviser**.

  No trabajes en DEBT-050 ni DEBT-052 durante esta intervención.

  ## 1. Objetivo

  Eliminar los imports relativos padre que incumplen la arquitectura de AICore y garantizar que Oxlint aplique la restricción de forma consistente en todos los paquetes donde corresponda.

  El reporte anterior identificó:

  - `mcp-servers/system-one`: 43 líneas.
  - `.opencode/plugins/odd-adviser`: 41 líneas.

  No asumas que cada línea representa necesariamente un import distinto. Verifica el inventario real.

  **No quiero conservar excepciones en Oxlint únicamente porque el código existente todavía no cumple una regla arquitectónica.**

  ## 2. Verificar el contrato arquitectónico

  Antes de modificar el código:

  1. Examina las reglas arquitectónicas vigentes de AICore.
  2. Revisa DEBT-049 y su relación con DEBT-051.
  3. Solicita el dictamen de Bastion sobre el alcance de la restricción `import/no-relative-parent-imports`.
  4. Identifica cómo resuelven actualmente los módulos cada uno de los dos paquetes.

  Mi preferencia es prohibir los imports relativos padre de forma consistente, utilizando mecanismos de resolución de módulos apropiados para cada paquete.

  Si existe una contradicción con un contrato vigente, explícala antes de modificarlo. No redefinas silenciosamente la arquitectura.

  ## 3. Implementar las correcciones

  Una vez confirmado el contrato:

  - Sustituye los imports relativos padre por imports apropiados, preferentemente mediante los mecanismos de aliases o package imports que soporte cada paquete.
  - Reutiliza las convenciones existentes cuando sea posible.
  - Utiliza los mecanismos estándar de TypeScript y Node.js, sin introducir resolutores personalizados innecesarios.
  - Comprueba la compatibilidad con ESM, Node.js, TypeScript y los runners de pruebas.
  - No alteres la lógica funcional.
  - No cambies la API pública de los paquetes innecesariamente.
  - No reorganices directorios ni muevas módulos únicamente para eliminar imports.
  - Evita introducir nuevas dependencias.

  No realices sustituciones masivas a ciegas. Cada cambio debe conservar la resolución correcta del módulo tanto en desarrollo como en ejecución.

  Trabaja primero sobre un paquete y verifica su funcionamiento antes de continuar con el segundo.

  Si descubres que la solución requiere una reestructuración arquitectónica considerable, presenta el impacto y una alternativa más sencilla antes de ejecutarla.

  ## 4. Fortalecer Oxlint

  Revisa `.oxlintrc.json`.

  Quiero que la restricción `import/no-relative-parent-imports` se aplique a todos los paquetes cubiertos por el contrato arquitectónico.

  No mantengas overrides que oculten infracciones reales.

  Comprueba que Oxlint detecte un import relativo padre introducido deliberadamente en una prueba aislada y que la configuración definitiva rechace ese patrón.

  No introduzcas excepciones injustificadas ni desactives la regla.

  ## 5. Validaciones

  Ejecuta las verificaciones necesarias para demostrar que la migración es segura:

  - Resolución de módulos en ambos paquetes.
  - Typecheck.
  - Lint.
  - Pruebas unitarias e integración relevantes.
  - Arranque y carga de módulos cuando corresponda.
  - `pnpm verify:full`, si los cambios están listos para la validación integral.

  Confirma que no se han introducido regresiones en las interfaces ni en el comportamiento de los agentes.

  La condición de aceptación es que no queden imports relativos padre en los paquetes donde la restricción aplica y que Oxlint pueda detectar nuevas infracciones.

  ## 6. Gestión de la deuda

  Cuando la implementación esté validada:

  1. Actualiza DEBT-051 con la evidencia concreta de las correcciones.
  2. Verifica su relación con DEBT-049.
  3. Cierra DEBT-051 únicamente si se cumplen sus criterios de resolución originales.
  4. No cierres DEBT-049 automáticamente: determina si su propio criterio está satisfecho.
  5. Si aparece trabajo adicional que deba diferirse, regístralo como deuda técnica, sin duplicar entradas existentes.

  No cambies los criterios retrospectivamente para justificar el cierre.

  ## 7. Restricciones

  Todo el trabajo debe limitarse a AICore.

  No modifiques:

  `G:\projects-tismart\tismart-belcorp-l2-support\mcp-servers`

  No modifiques ni sincronices proyectos destino.

  Mantén el trabajo en la rama local existente `feat/tooling/lint-and-format-adoption`, sin reformateos masivos ni cambios ajenos a DEBT-051.

  Herald continúa siendo el único agente autorizado para ejecutar operaciones Git/GitHub.

  Puedes realizar las correcciones y validaciones locales, pero **no crees nuevos commits, no publiques la rama, no abras un PR y no realices merge sin mi autorización**.

  ## 8. Resultado esperado

  Al finalizar, entrégame:

  1. Diagnóstico del contrato arquitectónico y dictamen de Bastion.
  2. Cantidad real de imports corregidos por paquete.
  3. Estrategia de resolución de módulos adoptada y justificación.
  4. Configuración definitiva de Oxlint.
  5. Resultados de las pruebas y verificaciones.
  6. Estado final de DEBT-051 y relación con DEBT-049.
  7. Riesgos o problemas pendientes.

  Quiero **una solución definitiva, mínima y mantenible**, sin excepciones arbitrarias y sin convertir esta corrección en una refactorización general.

  No avances con otras deudas. Terminaremos DEBT-051 antes de decidir cuál resolver después.
  ```
- L2 — Dictamen de Bastion 🧱, literal: la regla de `stacks/typescript/nestjs.md:51` **no** obliga a ninguno de los dos paquetes, porque esa guía se acota a código de aplicación NestJS y nombra los aliases de esa aplicación; `implementation/architecture.md:9,:13` obliga la dirección de dependencias pero no fija forma de import; `shapes/scripts.md:17` delega las convenciones de import a una stack guide que no existe, de modo que la convención concreta estaba sin asignar y no había infracción reportable. Mecanismo si se adopta: subpath `imports` de Node en el `package.json` de cada paquete, nunca `paths` de tsconfig, porque Node ESM no lee tsconfig. La propagación normativa a un owner quedaría bloqueada por el diferimiento vigente de DEBT-049 (no crear stack guide de scripts ahora). DEBT-049 queda parcialmente satisfecha: responde su pregunta de propiedad pero no su contabilidad de extracción.
- L3 — Diagnóstico propio del inventario, corrigiendo la premisa de conteo: los 43 y 41 no eran líneas sueltas sino statements, y se verificaron como tales (system-one 43 statements en 18 archivos con 22 specifiers distintos; odd-adviser 41 en 19 archivos con 12). Sin re-exports ni imports dinámicos; `mcp-servers/system-one/evals` no contiene ninguno, por lo que el inventario era completo. Aparece un caso que una sustitución ingenua habría omitido: `../../index.ts` en el factory de tests del plugin, que resuelve al entry del paquete y no encaja en el patrón `<carpeta>/<archivo>`; se trató con un mapeo explícito `#index.ts`.
- L4 — Base de autoridad. El dictamen dice que el contrato no obliga, pero no prohíbe: adoptar la convención es una selección de mecanismo propiedad del proyecto, igual que la que ya rigen `cli/aicore` y los seis skills sin que ningún owner arquitectónico la declare. Por eso no se editó ningún documento de arquitectura, no se creó stack guide y no se redefinió el contrato: se ejecutó la preferencia explícita del usuario como decisión de proyecto.
- L5 — Migración aplicada por paquete y verificada por separado. system-one: mapa `#application/#domain/#infrastructure/#mcp/#test`, 43 statements reescritos en 18 archivos; typecheck verde, 40 tests verdes, carga real en Node ESM de dos módulos, y el entry MCP lanzado por subproceso salió con código 0 sin error de resolución y con 0 bytes en stdout (stdout debe llevar solo frames de protocolo). odd-adviser: mapa `#application/#domain/#index.ts/#infrastructure/#test`, 41 statements en 19 archivos; typecheck verde, 73 tests verdes, y el entry del plugin cargado en Node ESM devolvió la misma superficie pública exportada, sin cambios de API.
- L6 — Lint fortalecido y probado. `import/no-relative-parent-imports` se movió del override de dos árboles al bloque global de `rules`, y se eliminó el override que ocultaba estos dos paquetes; el único override restante es el de `typescript/unbound-method` en tests. Con la regla global el lint da 0 errores y los mismos 9 warnings de DEBT-050, sin cambios. Prueba de detección: se introdujeron dos infracciones deliberadas, una por árbol recién cubierto, y ambas produjeron error de la regla con código de salida 1; las sondas se eliminaron y se verificó que no quedara ninguna.
- L7 — Verificación integral. `pnpm verify:full` verde: 480 archivos de formato, 0 errores de lint, 10 proyectos de typecheck, 665 tests (533 de paquetes, 40 de system-one, 73 de odd-adviser, 19 e2e). Re-medición del inventario después del cambio: 0 statements relativos padre en ambos árboles. Sin dependencias nuevas; ningún archivo movido; ningún cambio de lógica.
- L8 — Prerrequisito abierto para cerrar la feature: no se ha creado ningún commit porque esta intervención lo prohíbe expresamente, y el retiro de DEBT-051 exige un work unit autorizado y commiteado con la evidencia de resolución en este registro.
- L9 — Integración real verificada dentro de OpenCode, cerrando la única brecha que quedaba. `opencode plugin list` reporta el plugin como local. Un servidor nuevo registró `msg="loading plugin"` con `entrypoint=file:///…/odd-adviser/src/index.ts` y a continuación suscribió un watcher por cada módulo del grafo resuelto, lo que sólo ocurre cuando los specifiers `#` resuelven. Siguió un evento `hook_registered`, y una sesión completa en una instancia standalone nueva produjo la secuencia `candidate_found → evaluate_started → evaluate_finished → advisory_injected` con 5 partes inyectadas (sesión `ses_e196b073dffeTKPWehF6nbHpoc`). El código `tool_error` de `evaluate_finished` no es un fallo de resolución: `stdio-mcp-client.ts:107` sólo lo emite cuando la llamada MCP devuelve `isError: true`, mientras que un fallo de arranque o de import emite `transport_error`; por tanto esa misma corrida prueba además que el entry de `mcp-servers/system-one` arrancó y respondió a nivel de protocolo con sus nuevos specifiers. Control diferencial: `tool_error` aparece en las once sesiones registradas, incluidas todas las anteriores al cambio, así que refleja la ausencia del endpoint local del modelo y no una regresión. No se modificó ningún import como consecuencia de esta prueba, porque la resolución ya estaba demostrada.
- L10 — Retiro formal de **DEBT-051** del registro de deuda, en este mismo work unit. Se eliminó su entrada de `.aicore/core/knowledge/debt.md` porque ese registro guarda solo deudas abiertas y declara a Git como registro permanente de las retiradas; quedan 10 entradas (DEBT-042…050 y DEBT-052), con IDs ascendentes y el contador `DEBT-053` intacto, de modo que el hueco es historia válida y no se reutiliza. **Deuda retirada:** «DEBT-051 — Parent-relative imports in the two non-workspace TypeScript roots». **Decisión original de diferimiento, preservada verbatim:** «Lo posponemos.» y «No quiero una migración arquitectónica adicional dentro de esta feature. Documenta el hallazgo si corresponde, sin modificar esos imports.» **Criterios de resolución originales y su cumplimiento:** (a) obtener el dictamen arquitectónico que DEBT-049 reclama — cumplido por Bastion 🧱, que dictaminó que la convención concreta estaba sin asignar y que el mecanismo sería subpath `imports` de Node; (b) migración de cada árbol a su propio mapa de subpath imports, con cero specifiers relativos padre — cumplido, 43 y 41 statements reescritos, re-medido en 0; (c) suite completa y typecheck del paquete en verde — cumplido, 40 y 73 tests más typecheck; (d) regla de lint extendida para cubrirlos — cumplido, movida al bloque global con prueba de detección en ambos árboles. **Validaciones registradas:** `pnpm verify:full` (480 archivos de formato, 0 errores de lint, 10 proyectos de typecheck, 665 tests), escaneo de inventario posterior en 0, resolución real en Node ESM, arranque del servidor MCP con exit 0, y la integración funcional dentro de OpenCode descrita en L9. **Revisión independiente:** el dictamen de Bastion 🧱 sobre el contrato y la aceptación explícita del usuario sobre la evidencia técnica; no hubo revisión independiente de agente sobre el diff de imports. **Commit de entrega:** el commit único que contiene este registro y el retiro de la deuda; un commit no puede citar su propio identificador, por lo que las filas de Tasks permanecen `in progress` con `commit: pending` y su SHA queda para un work unit posterior autorizado. **Alcance preservado:** DEBT-049 sigue abierta y sin modificar, porque su criterio de contabilidad de extracción sigue pendiente; DEBT-050 y DEBT-052 no se tocaron. **Nota sobre S7:** su aceptación literal hablaba de leer DEBT-051 en el registro, pero el retiro elimina la entrada por regla del propio registro; el criterio no cambió y su evidencia vive ahora en este registro gobernante.
