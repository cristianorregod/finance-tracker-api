-- SQLite/Turso migration. Run once against an existing database before deploying
-- the application. create_all does not alter existing tables.

CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    budget_id INTEGER REFERENCES budgets(id),
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR NOT NULL,
    description VARCHAR,
    amount FLOAT NOT NULL,
    day_of_month INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    recurrence VARCHAR NOT NULL DEFAULT 'monthly',
    status VARCHAR NOT NULL DEFAULT 'active',
    last_confirmed_date DATE,
    next_occurrence_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_recurring_expenses_account_id ON recurring_expenses(account_id);
CREATE INDEX IF NOT EXISTS ix_recurring_expenses_budget_id ON recurring_expenses(budget_id);
CREATE INDEX IF NOT EXISTS ix_recurring_expenses_category_id ON recurring_expenses(category_id);
CREATE INDEX IF NOT EXISTS ix_recurring_expenses_status ON recurring_expenses(status);
CREATE INDEX IF NOT EXISTS ix_recurring_expenses_next_occurrence_date ON recurring_expenses(next_occurrence_date);

-- These ALTER statements are intentionally explicit and should be run only once
-- because SQLite versions used by Turso do not universally support ADD COLUMN IF NOT EXISTS.
ALTER TABLE transactions ADD COLUMN recurring_expense_id INTEGER REFERENCES recurring_expenses(id);
ALTER TABLE transactions ADD COLUMN occurrence_period VARCHAR;

CREATE INDEX IF NOT EXISTS ix_transactions_recurring_expense_id ON transactions(recurring_expense_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_transactions_recurring_period
    ON transactions(recurring_expense_id, occurrence_period);
