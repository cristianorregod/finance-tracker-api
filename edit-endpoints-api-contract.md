# API Contract — Edit Endpoints

## Auth
Todos estos endpoints requieren JWT:

```http
Authorization: Bearer <token>
```

---

# 1) Edit Account

## Endpoint
```http
PATCH /accounts/{account_id}
```

## Descripción
Actualiza parcialmente una cuenta.

## Path params

| Campo | Tipo | Requerido | Descripción |
|---|---|---:|---|
| `account_id` | `number` | ✅ | ID de la cuenta |

## Body permitido

| Campo | Tipo | Requerido | Editable | Reglas |
|---|---|---:|---:|---|
| `name` | `string` | ❌ | ✅ | min 3, max 25 |
| `initial_balance` | `number` | ❌ | ✅* | solo si la cuenta no tiene transacciones |
| `account_type` | `string` | ❌ | ✅ | min 5, max 20 |
| `icon` | `string` | ❌ | ✅ | min 3, max 25 |

## Campos NO permitidos
No mandar:
- `current_balance`
- `last_transaction_date`

## Ejemplo request
```json
{
  "name": "Banco Sueldo",
  "icon": "bank"
}
```

## Ejemplo response 200
```json
{
  "message": "Account updated successfully",
  "account": {
    "id": 1,
    "name": "Banco Sueldo",
    "initial_balance": 2500,
    "current_balance": 2500,
    "account_type": "savings",
    "icon": "bank",
    "last_transaction_date": null,
    "created_at": "2026-06-08T10:00:00",
    "updated_at": "2026-06-08T12:00:00"
  }
}
```

## Errores esperables
### 400
```json
{
  "detail": "Initial balance cannot be edited once the account has transactions"
}
```

### 404
```json
{
  "detail": "Account not found"
}
```

---

# 2) Edit Budget

## Endpoint
```http
PATCH /budgets/{budget_id}
```

## Descripción
Actualiza parcialmente un presupuesto.

## Path params

| Campo | Tipo | Requerido | Descripción |
|---|---|---:|---|
| `budget_id` | `number` | ✅ | ID del presupuesto |

## Body permitido

| Campo | Tipo | Requerido | Editable | Reglas |
|---|---|---:|---:|---|
| `name` | `string` | ❌ | ✅ | min 3, max 25 |
| `description` | `string \| null` | ❌ | ✅ | opcional |
| `amount` | `number` | ❌ | ✅ | `>= 0`, no puede ser menor a lo ya gastado |
| `icon` | `string \| null` | ❌ | ✅ | opcional |

## Campos NO permitidos
No mandar:
- `remaining_amount`
- `spent_amount`
- `last_transaction_date`

## Regla importante
Si mandás `amount`, backend recalcula:

```txt
remaining_amount = amount - spent_amount
```

## Ejemplo request
```json
{
  "name": "Gastos del hogar",
  "amount": 1800
}
```

## Ejemplo response 200
```json
{
  "message": "Budget updated successfully",
  "budget": {
    "id": 2,
    "name": "Gastos del hogar",
    "description": "Servicios y compras",
    "amount": 1800,
    "remaining_amount": 950,
    "spent_amount": 850,
    "icon": "home",
    "last_transaction_date": "2026-06-07T18:20:00",
    "created_at": "2026-06-01T09:00:00",
    "updated_at": "2026-06-08T12:10:00"
  }
}
```

## Errores esperables
### 400
```json
{
  "detail": "Budget amount cannot be lower than the amount already spent"
}
```

### 404
```json
{
  "detail": "Budget not found"
}
```

---

# 3) Edit Transaction

## Endpoint
```http
PATCH /transactions/{transaction_id}
```

## Descripción
Actualiza parcialmente una transacción.

## Path params

| Campo | Tipo | Requerido | Descripción |
|---|---|---:|---|
| `transaction_id` | `number` | ✅ | ID de la transacción |

## Body permitido

| Campo | Tipo | Requerido | Editable | Reglas |
|---|---|---:|---:|---|
| `from_account_id` | `number \| null` | ❌ | ✅ | requerido para `EXPENSE` y tipos no `INCOME` |
| `to_account_id` | `number \| null` | ❌ | ✅ | requerido para `INCOME` |
| `budget_id` | `number \| null` | ❌ | ✅ | opcional |
| `category_id` | `number \| null` | ❌ | ✅ | opcional |
| `type` | `string` | ❌ | ✅ | hoy soporta `INCOME`, `EXPENSE`, `SAVINGS` |
| `description` | `string \| null` | ❌ | ✅ | opcional |
| `title` | `string` | ❌ | ✅ | min 15, max 25 |
| `amount` | `number` | ❌ | ✅ | debe ser `> 0` |
| `icon` | `string \| null` | ❌ | ✅ | opcional |
| `transaction_date` | `string (YYYY-MM-DD)` | ❌ | ✅ | fecha válida |

## Reglas funcionales importantes

### Si cambian estos campos:
- `type`
- `amount`
- `from_account_id`
- `to_account_id`
- `budget_id`

el backend **reconcilia balances y presupuesto**.

### Si cambian solo estos:
- `description`
- `title`
- `icon`
- `category_id`
- `transaction_date`

el backend **NO toca balances**.

## Validaciones importantes

### INCOME
Debe tener:
- `to_account_id`

### EXPENSE / SAVINGS
Debe tener:
- `from_account_id`

### Regla general
`from_account_id` y `to_account_id` no pueden ser iguales.

## Ejemplo request — cambio solo metadata
```json
{
  "title": "Compra super semanal",
  "description": "Compras del sábado",
  "category_id": 3
}
```

## Ejemplo request — cambio financiero
```json
{
  "amount": 240.75,
  "budget_id": 4
}
```

## Ejemplo request — convertir a ingreso
```json
{
  "type": "INCOME",
  "to_account_id": 1,
  "from_account_id": null,
  "budget_id": null,
  "amount": 950
}
```

## Ejemplo response 200
```json
{
  "message": "Transaction updated successfully",
  "transaction": {
    "id": 15,
    "from_account": {
      "id": 1,
      "name": "Banco Principal"
    },
    "to_account": null,
    "budget": {
      "id": 4,
      "name": "Comida"
    },
    "category": {
      "id": 3,
      "name": "Supermercado"
    },
    "type": "EXPENSE",
    "description": "Compras del sábado",
    "title": "Compra super semanal",
    "amount": 240.75,
    "transaction_date": "2026-06-08",
    "icon": "cart",
    "created_at": "2026-06-08T11:00:00",
    "updated_at": "2026-06-08T12:20:00"
  }
}
```

## Errores esperables

### 400
```json
{
  "detail": "Transaction amount must be greater than 0"
}
```

```json
{
  "detail": "INCOME transactions require a destination account"
}
```

```json
{
  "detail": "This transaction type requires a source account"
}
```

```json
{
  "detail": "Source and destination accounts must be different"
}
```

```json
{
  "detail": "Account balance cannot be negative"
}
```

```json
{
  "detail": "Budget remaining amount cannot be negative"
}
```

### 404
```json
{
  "detail": "Transaction not found"
}
```

---

# Recomendación de uso desde frontend

## Regla de oro
Mandá **solo los campos modificados**.

## Bien
```json
{
  "icon": "wallet"
}
```

## Evitá esto si no hace falta
Mandar el objeto completo entero para un PATCH.

---

# Tipado sugerido para frontend (TypeScript)

## Account
```ts
export interface UpdateAccountPayload {
  name?: string;
  initial_balance?: number;
  account_type?: string;
  icon?: string;
}
```

## Budget
```ts
export interface UpdateBudgetPayload {
  name?: string;
  description?: string | null;
  amount?: number;
  icon?: string | null;
}
```

## Transaction
```ts
export interface UpdateTransactionPayload {
  from_account_id?: number | null;
  to_account_id?: number | null;
  budget_id?: number | null;
  category_id?: number | null;
  type?: "INCOME" | "EXPENSE" | "SAVINGS";
  description?: string | null;
  title?: string;
  amount?: number;
  icon?: string | null;
  transaction_date?: string;
}
```

---

# Checklist para el frontend

## Antes de mandar PATCH de account
- no mandar `current_balance`
- no mandar `last_transaction_date`

## Antes de mandar PATCH de budget
- no mandar `remaining_amount`
- no mandar `spent_amount`

## Antes de mandar PATCH de transaction
- si `type = INCOME`, mandar `to_account_id`
- si `type != INCOME`, mandar `from_account_id`
- no mandar cuentas iguales
- si solo cambia metadata, mandar solo metadata
