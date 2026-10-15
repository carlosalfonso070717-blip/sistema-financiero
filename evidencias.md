# Evidencias · Unidad II · Actividad 5

- **Actor de las pruebas de configuración:** la membresía de Ana (ADMINISTRADOR).
- **Listas usadas:**
  - **S0:** accounts.read, concepts.read, transactions.read y transactions.write.
  - **S1:** S0 más accounts.write.
- **Dónde está cada cosa:** las operaciones en `operaciones.graphql`, las variables en `variables/`, el SQL en `comprobaciones.sql` y las capturas en `evidencias/`.
- **Seguridad:** las capturas no muestran contraseñas, tokens ni hashes.

---

## E01. Punto de partida

- **Precondición:** base con los 4 roles y los 10 permisos de la actividad 4; Capturista en S0.
- **Operación y variables:** `ConsultarRoles`, `ConsultarPermisos` y `ListaDeCapturista` con `variables/capturista.json`. SQL: consulta 2 de `comprobaciones.sql`.
- **Resultado esperado:** 4 roles, 10 permisos y 4 relaciones activas de Capturista, que coinciden con `configuracion_inicial.json`.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** la configuración inicial está guardada en `role_permissions` y coincide con el archivo de configuración.
- **Capturas:** `evidencias/E01-roles.png`, `evidencias/E01-permisos.png`, `evidencias/E01-capturista.png`

## E02. Catálogo

- **Precondición:** E01.
- **Operación y variables:**
  - `ExplorarCatalogo` (alias `cuentas` y `movimientos`, fragmento `DatosPermiso`) con `variables/actor.json`.
  - `CatalogoCompleto` con `variables/actor.json`.
  - `CatalogoRecursoInexistente` de `operaciones_error_e02.graphql`.
- **Resultado esperado:** 2 permisos en cada alias, 10 sin filtro, y un error de validación porque `PAYMENTS` no existe en el enum.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** el enum limita los valores posibles y el resolver filtra en la base por el prefijo del código.
- **Capturas:** `evidencias/E02-alias.png`, `evidencias/E02-sin-filtro.png`, `evidencias/E02-payments.png`

## E03. Previsualización

- **Precondición:** Capturista en S0.
- **Operación y variables:** `RevisarConfiguracion` con `variables/s1_capturista.json`. SQL: consulta 2 antes y después.
- **Resultado esperado:** toActivate = [accounts.write], toDeactivate = [], 4 en unchanged y finalCount = 5. El SQL de antes y el de después son idénticos.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** previsualizar solo lee y calcula; no cambia ninguna fila.
- **Capturas:** `evidencias/E03-respuesta.png`, `evidencias/E03-sql-antes.png`, `evidencias/E03-sql-despues.png`

## E04. Aplicación e idempotencia

- **Precondición:** Capturista en S0.
- **Operación y variables:** `AplicarConfiguracion` con `variables/s1_capturista.json`, dos veces. SQL: consultas 2 y 3.
- **Resultado esperado:**
  - Primera vez: `changed: true` y activated = [accounts.write].
  - Segunda vez: `changed: false`, activated y deactivated vacíos, y finalCount = 5.
  - En SQL, las mismas parejas con los mismos id, sin duplicados.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** repetir la misma lista deja el mismo estado y no inserta filas.
- **Capturas:** `evidencias/E04-primera.png`, `evidencias/E04-segunda.png`, `evidencias/E04-sql.png`

## E05. Desactivar y reactivar

- **Precondición:** Capturista en S1 (después de E04).
- **Operación y variables:** `AplicarConfiguracion` con `variables/s0_capturista.json` y luego con `variables/s1_capturista.json`. SQL: consulta 1, en los tres momentos.
- **Resultado esperado:** la fila de accounts.write pasa de activa a inactiva y otra vez a activa, con el **mismo** `relacion_id` en los tres momentos. `permiso_activo` sigue en 1.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** desactivar no borra la fila y reactivar reutiliza la misma relación; el catálogo del permiso no cambia.
- **Capturas:** `evidencias/E05-momento1.png`, `evidencias/E05-momento2.png`, `evidencias/E05-momento3.png`

## E06. Entradas inválidas

- **Precondición:** Capturista en S0. Antes de empezar, guarda el resultado de la consulta 1 de SQL para comparar.
- **Operación:** `RevisarConfiguracion` y `AplicarConfiguracion` con cada archivo. En ambos casos la respuesta trae `data` en `null` y el motivo en `errors`.

| Variante | Variables | Preparación SQL | Error esperado | Resultado obtenido |
| --- | --- | --- | --- | --- |
| Rol inexistente | `e06_rol_inexistente.json` | — | `ROLE_NOT_FOUND`: el rol no existe | |
| Rol inactivo | `e06_rol_inactivo.json` | sección 6, CONTADOR inactivo; restaurar al terminar | `ROLE_NOT_FOUND`: el rol CONTADOR está inactivo | |
| ADMINISTRADOR | `e06_administrador.json` | — | `PROTECTED_ROLE` | |
| Permiso inexistente | `e06_permiso_inexistente.json` | — | `PERMISSION_NOT_FOUND`: no existen los permisos | |
| Permiso inactivo | `e06_permiso_inactivo.json` | sección 6, concepts.write inactivo; restaurar al terminar | `PERMISSION_NOT_FOUND`: permisos inactivos | |
| Permiso repetido | `e06_permiso_repetido.json` | — | `VALIDATION_ERROR`: la lista repite permisos | |

- **Comparación SQL:** el resultado de la consulta 1 es igual antes y después de todas las variantes.
- **Regla demostrada:** una entrada inválida se rechaza antes de escribir, y la configuración no cambia.
- **Capturas:** `evidencias/E06-<variante>.png` y `evidencias/E06-sql.png`

## E07. Reversión de un fallo

- **Precondición:** ninguna; la prueba crea su propia base temporal.
- **Operación:** `python -m unittest tests.test_e07_rollback -v`
- **Punto de fallo:** se reemplaza el `commit` de la sesión, con `unittest.mock`, por uno que lanza un error. En ese momento ya se hizo el `flush` de 3 cambios: quitar transactions.write y agregar accounts.write y concepts.write.
- **Resultado esperado:** la prueba confirma que los 3 cambios estaban escritos sin confirmar, y desde una **sesión nueva** confirma que la configuración es la de antes. Las dos pruebas salen `ok`.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** la actualización completa se confirma o se revierte como una sola unidad.
- **Captura:** `evidencias/E07-test.png`

## E08. Lista vacía y reinicio

- **Precondición:** Capturista en S0.
- **Operación y variables:** `AplicarConfiguracion` con `variables/vacia_capturista.json`. Luego Ctrl+C, volver a arrancar el servidor y repetir `ListaDeCapturista`. SQL: consultas 2 y 5.
- **Resultado esperado:** deactivated trae los 4 permisos y finalCount = 0. Antes y después del reinicio hay 0 relaciones activas y las filas siguen ahí, inactivas. Siguen siendo 4 roles y 10 permisos.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** la carga inicial distingue un rol sin inicializar de una lista vacía decidida a propósito.
- **Capturas:** `evidencias/E08-respuesta.png`, `evidencias/E08-reinicio.png`, `evidencias/E08-sql.png`

## E09. Restauración

- **Precondición:** Capturista vacío (después de E08).
- **Operación y variables:** `AplicarConfiguracion` con `variables/s0_capturista.json`. SQL: consultas 3 y 4.
- **Resultado esperado:** la matriz activa es igual a `configuracion_final.json`, que a su vez es igual a `configuracion_inicial.json`, y no hay parejas duplicadas.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** al terminar, la configuración vuelve a la inicial.
- **Capturas:** `evidencias/E09-respuesta.png`, `evidencias/E09-sql.png`

## E10. Continuidad del proyecto

- **Precondición:** empresa con una cuenta, y un concepto de ingreso asignado a esa cuenta. Ana tiene sesión iniciada; el token va en Headers y no aparece en la captura.
- **Operación y variables:** `ConsultarCuentas` con `variables/e10_consultar_cuentas.json` y `RegistrarMovimiento` con `variables/e10_registrar_movimiento.json`. SQL: consulta 7.
- **Resultado esperado:** la consulta devuelve las cuentas y el movimiento queda guardado con su cuenta, su concepto y un monto de 1500.00.
- **Resultado obtenido:** _(completar)_
- **Regla demostrada:** las operaciones anteriores siguen funcionando.
- **Capturas:** `evidencias/E10-cuentas.png`, `evidencias/E10-movimiento.png`, `evidencias/E10-sql.png`
