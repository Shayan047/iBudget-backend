# Application Knowledge Base

## User Identity
The User entity is the central node of the ecosystem. Every financial record is strictly owned by a unique identity.
•	Table: users
•	Primary Key: id
•	Business Logic: Acts as the root for all data. Relationships like incomes, budgets, and expenses are configured with cascade="all, delete". This ensures that a user's entire financial history is strictly tied to their account lifecycle.

## Income Management (Revenue Tracking)
This feature manages the inflow of a user’s incomes.
•	Table: incomes
•	Foreign Key: user_id (References users.id)
•	Business Logic: Every income record tracks a specific amount and date. The relationship with the taxes table (via income_id) handles taxation tracking.

## Category Management (Expense Classification)
Organizes expenses by letting users select a category.
•	Table: categories
•	Foreign Key: created_by_user_id (Optional, references users.id)
•	Business Logic: Supports both Global and Custom categories. If created_by_user_id is null, it is a system default. If populated, it is user-specific.

### Expense Management (Expenditure Tracking)
The core of the application records individual spending events, divided into personal and shared expenses.

•	Tables: expenses and shared_expense_users
•	Expense Table Foreign Keys: user_id, category_id (References categories.id)
•	SharedExpenseUser Table Foreign Keys: expense_id (References expenses.id), user_id (References users.id)

Business Logic Guardrails:

1.	Personal vs. Shared: If is_shared in the expenses table is false, it is a personal expense and has no entries in shared_expense_users.
2.	Shared Totals: If is_shared is true, the amount in the expenses table represents the total bill.
3.	Ownership: user_id in the expenses table is always the Owner (the person who paid the bill).
4.	Participant Mapping: All users involved (including the creator) must have a row in shared_expense_users.
5.	Role Logic: In the shared_expense_users table, the is_creator boolean identifies if the user is the owner (true) or a participant (false).
6.	Status Enum: The status column in shared_expense_users uses the SharedExpenseStatus enum with lowercase values:
    •	paid
    •	pending
7.	Creator Status: The status for the creator (is_creator = true) is always paid.
8.	Receivables/Payables: * To find money owed to the user: Look for rows where the user is the creator but participants have a pending status.
9.  find money the user owes: Look for rows in shared_expense_users where user_id is the user, is_creator is false, and status is pending.

