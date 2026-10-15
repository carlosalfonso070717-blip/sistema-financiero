# Parte 1. Investigación breve y preparación

## 1. ¿Qué diferencia hay entre autenticación, autorización y configuración de permisos? ¿Por qué actorCompanyUserId no comprueba identidad?

**Respuesta:**

La autenticación comprueba quién eres, la autorización define qué puedes hacer y los permisos indican a qué información puedes acceder. Por ejemplo, un administrador puede ver todos los ingresos, pero otro usuario solo los suyos. actorCompanyUserId no comprueba la identidad porque alguien podría cambiar ese dato por el de otra persona.

## 2. ¿Cómo ayudan las variables, alias y fragmentos a preparar pruebas repetibles? Incluye una operación propia que los utilice.

**Respuesta:**

Las variables permiten cambiar los datos sin modificar la consulta, los alias ayudan a distinguir resultados y los fragmentos permiten reutilizar campos. Esto facilita repetir pruebas con diferentes datos.

Ejemplo:

```graphql
query {
  ingresos: ingreso(id: "123") {
    id
    monto
    estado
  }
}
```

Aquí uso un alias llamado ingresos para identificar el resultado de la consulta.

## 3. ¿Qué valida un enum o un input de GraphQL y qué reglas deben seguir validándose en Python? Explica también por qué [ID!]! acepta [].

**Respuesta:**

Un enum permite elegir entre valores definidos, mientras que un input establece qué datos se pueden enviar. En Python todavía debemos comprobar reglas como que el monto sea positivo y que el usuario tenga permiso. [ID!]! acepta [] porque la lista puede estar vacía, aunque no permite que la lista ni sus elementos sean nulos.

## 4. ¿Qué diferencia hay entre atomicidad e idempotencia? ¿Por qué enviar varias mutaciones en una petición no garantiza un rollback conjunto?

**Respuesta:**

La atomicidad significa que todos los cambios se realizan o ninguno. La idempotencia significa que repetir una operación no debe causar cambios duplicados. En GraphQL, enviar varias mutaciones no garantiza que todos los cambios se deshagan si ocurre un error. Para lograrlo, el backend debe usar una transacción en la base de datos.

## Fuentes consultadas

- GraphQL: https://www.ibm.com/mx-es/think/topics/graphql  15/10/2026
- Strawberry: https://strawberry.rocks/docs/guides/permissions  15/10/2026
- Python: https://www.paradigmadigital.com/dev/implementacion-graphql-python/  15/10/2026