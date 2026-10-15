-- Unidad II · Actividad 5 · Consultas de verificación (SQLite: financial.db)
-- Ábrelas con DB Browser for SQLite o con la extensión SQLite Viewer de VS Code.
-- En SQLite los booleanos se guardan como 1 (verdadero) y 0 (falso).

-- 1. Relaciones rol-permiso con su id y sus dos estados (E01, E03, E04, E05, E08, E09)
SELECT rp.id        AS relacion_id,
       r.code       AS rol,
       p.code       AS permiso,
       rp.is_active AS relacion_activa,
       p.is_active  AS permiso_activo
FROM role_permissions rp
JOIN roles r       ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
ORDER BY r.code, p.code;

-- 2. Solo las relaciones de CAPTURISTA (E03, E04, E05, E06, E08)
SELECT rp.id AS relacion_id, p.code AS permiso, rp.is_active AS relacion_activa
FROM role_permissions rp
JOIN roles r       ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
WHERE r.code = 'CAPTURISTA'
ORDER BY p.code;

-- 3. Parejas duplicadas: debe devolver cero filas (E04, E09)
SELECT role_id, permission_id, COUNT(*) AS repeticiones
FROM role_permissions
GROUP BY role_id, permission_id
HAVING COUNT(*) > 1;

-- 4. Matriz activa por códigos, para comparar con configuracion_final.json (E09)
SELECT r.code AS rol, p.code AS permiso
FROM role_permissions rp
JOIN roles r       ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id
WHERE rp.is_active = 1
ORDER BY r.code, p.code;

-- 5. Catálogos sin duplicados después de reiniciar (E08)
SELECT COUNT(*) AS roles FROM roles;            -- 4
SELECT COUNT(*) AS permisos FROM permissions;   -- 10

-- 6. Preparación y restauración de E06 (datos de laboratorio)
--    El proyecto no tiene mutación para reactivar un rol ni para desactivar
--    un permiso del catálogo, por eso se preparan con SQL y se restauran
--    al terminar cada variante.

-- E06 · rol inactivo: preparar
UPDATE roles SET is_active = 0 WHERE code = 'CONTADOR';
-- (ejecutar RevisarConfiguracion y AplicarConfiguracion con variables/e06_rol_inactivo.json)
-- E06 · rol inactivo: restaurar
UPDATE roles SET is_active = 1 WHERE code = 'CONTADOR';

-- E06 · permiso inactivo: preparar
UPDATE permissions SET is_active = 0 WHERE code = 'concepts.write';
-- (ejecutar RevisarConfiguracion y AplicarConfiguracion con variables/e06_permiso_inactivo.json)
-- E06 · permiso inactivo: restaurar
UPDATE permissions SET is_active = 1 WHERE code = 'concepts.write';

-- 7. Movimientos registrados (E10)
SELECT t.id, t.transaction_type, t.amount, a.name AS cuenta, c.name AS concepto
FROM transactions t
JOIN accounts a ON a.id = t.account_id
JOIN concepts c ON c.id = t.concept_id
ORDER BY t.created_at DESC;
