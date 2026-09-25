# Sistema Financiero — API GraphQL

Actividad #3: gestión de empresas (día 1) y administración de usuarios asociados a cada empresa (día 2).

**Stack:** Python 3.11+, FastAPI, Strawberry GraphQL, SQLAlchemy, bcrypt y JWT.

## Instalación

```bash
python -m venv venv
source venv/Scripts/activate     # Linux o Mac: source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

El editor GraphiQL queda disponible en <http://localhost:8000/graphql>.

Por defecto se usa SQLite, de modo que no hace falta levantar un servidor de base de datos. Para trabajar con PostgreSQL basta con cambiar `DATABASE_URL` en el archivo `.env`.

## Estructura

```
app/
├── main.py            FastAPI y montaje del router de GraphQL
├── config.py          variables de entorno
├── database.py        motor y sesiones de SQLAlchemy
├── models/            tablas companies, users y company_users
├── schemas/           tipos e inputs de GraphQL
├── graphql_api/       queries, mutations y contexto
├── services/          reglas de negocio
└── core/              hash de contraseñas, JWT, validadores y errores
```

Las reglas de negocio se concentran en `services/` en lugar de los resolvers, así pueden probarse sin levantar el servidor.

## Reglas de negocio

| ID | Regla |
| --- | --- |
| RN-01 | Cada empresa mantiene sus datos independientes de las demás |
| RN-02 | El correo electrónico es único en todo el sistema |
| RN-03 | Las contraseñas se almacenan como hash, nunca en texto plano |
| RN-04 | Cada empresa tiene un solo administrador principal |
| RN-05 | No se registran usuarios en empresas inexistentes o inactivas |
| RN-06 | La eliminación de una empresa es lógica, se conserva el registro |
| RN-07 | Un usuario no puede tener dos membresías en la misma empresa |
| RN-08 | Una cuenta inactiva no puede autenticarse |

## Operaciones

### Día 1: gestión de empresas

```graphql
# Crear empresa
mutation {
  createCompany(input: {
    name: "Alfa Financiera"
    legalName: "Alfa Financiera SA de CV"
    taxId: "AAA010101AAA"
    email: "contacto@alfa.com"
    phone: "9991234567"
  }) { id name isActive createdAt }
}

# Validación: nombre vacío
mutation { createCompany(input: { name: "  " }) { id } }

# Consultar empresas
query { companies(activeOnly: false) { id name taxId isActive } }
query { company(id: "PEGAR_ID") { name legalName taxId email phone isActive } }
query { company(id: "no-existe") { name } }

# Actualizar
mutation {
  updateCompany(input: { id: "PEGAR_ID", phone: "9997654321" }) {
    name legalName phone updatedAt
  }
}

# Eliminar (baja lógica)
mutation { deactivateCompany(id: "PEGAR_ID") { id name isActive } }
query { companies(activeOnly: true) { id name } }
```

### Día 2: usuarios y autenticación

```graphql
# Administrador principal
mutation {
  createCompanyAdmin(input: {
    companyId: "PEGAR_ID"
    name: "Ana López"
    email: "ana@alfa.com"
    password: "SuperSecreta1"
  }) { id isAdmin joinedAt user { id name email } company { name } }
}

# Usuario
mutation {
  createCompanyUser(input: {
    companyId: "PEGAR_ID"
    name: "Luis Pérez"
    email: "luis@alfa.com"
    password: "OtraClave99"
  }) { id isAdmin user { email } }
}

# Correo duplicado
mutation {
  createCompanyUser(input: {
    companyId: "PEGAR_ID", name: "Otro", email: "LUIS@alfa.com", password: "Clave12345"
  }) { id }
}

# Segundo administrador
mutation {
  createCompanyAdmin(input: {
    companyId: "PEGAR_ID", name: "Beto", email: "beto@alfa.com", password: "Clave12345"
  }) { id }
}

# Empresa inexistente
mutation {
  createCompanyUser(input: {
    companyId: "fantasma", name: "Nadie", email: "nadie@correo.com", password: "Clave12345"
  }) { id }
}

# Autenticación correcta e incorrecta
mutation {
  login(input: { email: "ana@alfa.com", password: "SuperSecreta1" }) {
    token tokenType user { id name email }
  }
}
mutation { login(input: { email: "ana@alfa.com", password: "equivocada" }) { token } }

# Usuarios de la empresa
query { companyUsers(companyId: "PEGAR_ID") { id isAdmin isActive user { name email } } }
```

La prueba de correo duplicado usa mayúsculas distintas de forma intencional: el correo se normaliza antes de compararse, de manera que `LUIS@alfa.com` y `luis@alfa.com` se reconocen como el mismo.

## Códigos de error

`VALIDATION_ERROR`, `COMPANY_NOT_FOUND`, `EMAIL_ALREADY_EXISTS`, `ADMIN_ALREADY_EXISTS`, `MEMBERSHIP_ALREADY_EXISTS`, `INVALID_CREDENTIALS`, `ACCOUNT_DISABLED` y `FORBIDDEN`.

Cada error viaja en `extensions.code` para que el cliente reaccione al código y no al texto del mensaje.

## Actividad 4 — Día 1: cuentas, conceptos y conceptos por cuenta

Todas las operaciones necesitan el id de una empresa activa. Si la base está vacía, primero hay que crear la empresa y copiar su id.

```graphql
# Cuentas (mínimo 3)
mutation { createAccount(input: { companyId: "ID_EMPRESA", accountType: DEBIT, name: "Cuenta Principal BBVA", bankName: "BBVA", accountNumber: "0123456789", clabe: "012180001234567890" }) { id name accountType isActive } }
mutation { createAccount(input: { companyId: "ID_EMPRESA", accountType: CASH, name: "Caja Chica", shortDescription: "Efectivo de oficina" }) { id name accountType } }
mutation { createAccount(input: { companyId: "ID_EMPRESA", accountType: CREDIT, name: "Tarjeta Corporativa", bankName: "Santander", cardLastDigits: "4417" }) { id name accountType } }

# Conceptos de ingreso (mínimo 5)
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Ventas" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Servicios" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Intereses" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Rendimientos" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Otros ingresos" }) { id name conceptType } }

# Conceptos de egreso (mínimo 5)
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: EXPENSE, name: "Nómina" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: EXPENSE, name: "Renta" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: EXPENSE, name: "Servicios públicos" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: EXPENSE, name: "Proveedores" }) { id name conceptType } }
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: EXPENSE, name: "Impuestos" }) { id name conceptType } }

# Consultas
query { accounts(companyId: "ID_EMPRESA") { id name accountType bankName isActive } }
query { accounts(companyId: "ID_EMPRESA", accountType: DEBIT) { id name } }
query { concepts(companyId: "ID_EMPRESA", conceptType: INCOME) { id name } }
query { concepts(companyId: "ID_EMPRESA", conceptType: EXPENSE) { id name } }

# Asignar conceptos a una cuenta (mínimo 10 relaciones en total)
mutation { assignConceptToAccount(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO" }) { id isActive account { name } concept { name conceptType } } }

# Conceptos asociados a una cuenta
query { accountConcepts(accountId: "ID_CUENTA") { id isActive concept { id name conceptType } } }

# Desactivar la relación
mutation { removeConceptFromAccount(accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO") }
```

### Casos que deben fallar

```graphql
# DUPLICATE_ACCOUNT: nombre de cuenta repetido en la misma empresa
mutation { createAccount(input: { companyId: "ID_EMPRESA", accountType: CASH, name: "Caja Chica" }) { id } }

# DUPLICATE_CONCEPT: nombre de concepto repetido en la misma empresa
mutation { createConcept(input: { companyId: "ID_EMPRESA", conceptType: INCOME, name: "Ventas" }) { id } }

# RELATION_ALREADY_EXISTS: el concepto ya está asignado a esa cuenta
mutation { assignConceptToAccount(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO" }) { id } }

# COMPANY_MISMATCH: cuenta y concepto de empresas distintas
mutation { assignConceptToAccount(input: { accountId: "ID_CUENTA_OTRA_EMPRESA", conceptId: "ID_CONCEPTO" }) { id } }

# RELATION_NOT_FOUND: quitar una relación que no existe
mutation { removeConceptFromAccount(accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_NO_ASIGNADO") }
```

## Actividad 4 — Día 2: movimientos financieros

`createTransaction` exige usuario autenticado. Primero hay que obtener el token y colocarlo en el panel de Headers de GraphiQL:

```graphql
mutation { login(input: { email: "ana@alfa.com", password: "SuperSecreta1" }) { token } }
```

```json
{ "Authorization": "Bearer PEGAR_EL_TOKEN" }
```

```graphql
# Ingreso
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_INCOME", transactionType: INCOME, amount: "12500.50", shortDescription: "Venta de septiembre" }) { id amount transactionType transactionDate capturedAt account { name } concept { name conceptType } capturedByUser { name email } } }

# Egreso
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_EXPENSE", transactionType: EXPENSE, amount: "8400.00", shortDescription: "Pago de nómina" }) { id amount transactionType capturedByUser { name email } } }

# Consultas
query { transactions(limit: 50) { id transactionType amount transactionDate account { name } concept { name } capturedByUser { email } } }
query { transactions(accountId: "ID_CUENTA", limit: 20) { id transactionType amount } }
query { transactions(transactionType: EXPENSE, limit: 20) { id amount concept { name } } }
query { transactions(limit: 5, offset: 5) { id amount } }

# Eliminar
mutation { deleteTransaction(id: "ID_MOVIMIENTO") { id isActive } }
```

### Casos que deben fallar

```graphql
# INVALID_AMOUNT
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_INCOME", transactionType: INCOME, amount: "0" }) { id } }

# ACCOUNT_NOT_FOUND
mutation { createTransaction(input: { accountId: "fantasma", conceptId: "ID_CONCEPTO_INCOME", transactionType: INCOME, amount: "100" }) { id } }

# CONCEPT_NOT_FOUND
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "fantasma", transactionType: INCOME, amount: "100" }) { id } }

# CONCEPT_NOT_ALLOWED: el concepto no está asignado a esa cuenta
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_NO_ASIGNADO", transactionType: EXPENSE, amount: "100" }) { id } }

# UNAUTHENTICATED: la misma mutation sin el encabezado Authorization
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_INCOME", transactionType: INCOME, amount: "100" }) { id } }

# TRANSACTION_TYPE_MISMATCH: concepto de ingreso registrado como egreso
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_INCOME", transactionType: EXPENSE, amount: "100" }) { id } }

# COMPANY_MISMATCH: token de un usuario de otra empresa
mutation { createTransaction(input: { accountId: "ID_CUENTA", conceptId: "ID_CONCEPTO_INCOME", transactionType: INCOME, amount: "100" }) { id } }
```

## Códigos de error de la actividad 4

`DUPLICATE_ACCOUNT`, `DUPLICATE_CONCEPT`, `RELATION_ALREADY_EXISTS`, `RELATION_NOT_FOUND`, `ACCOUNT_NOT_FOUND`, `CONCEPT_NOT_FOUND`, `CONCEPT_NOT_ALLOWED`, `COMPANY_MISMATCH`, `INVALID_AMOUNT`, `TRANSACTION_TYPE_MISMATCH`, `TRANSACTION_NOT_FOUND` y `UNAUTHENTICATED`.

## Regla financiera

Todos los montos se almacenan como positivos y el tipo de movimiento determina su efecto: `INCOME` suma y `EXPENSE` resta. El balance de una cuenta es la suma de sus ingresos menos la suma de sus egresos.

## Pendiente

Las mutations `createCompany` y `createCompanyAdmin` se exponen sin autenticación, ya que el administrador de plataforma todavía no existe como registro en el sistema. En una versión posterior quedarían protegidas por un rol de superusuario.
