### Component: AI Chatbot Engine with Human-in-the-Loop (HIL) Guardrails

### 1. System Architecture Role

The Chatbot serves as a conversational natural language interface to the existing Warehouse Database (DB). It must handle two distinct pathways: 

1. **Read Operations (NL-to-SQL):** Direct answering of data queries.
2. **Write Operations (Mutations):** Intercepted by a mandatory confirmation gate before database execution.

### 2. Functional Requirements

### 2.1 Natural Language Processing & Querying (Read-Only)

* **REQ-CB-001: Semantic Schema Mapping** 

  * The NLP engine must map user conversational phrasing to the existing database schema (e.g., mapping *"How long has item X been here?"* to a calculation on arrival_time).
* **REQ-CB-002: Read-Only Query Generation** 

  * The system must translate natural language into optimized SQL read statements or API data calls.
  * The system must explicitly enforce read-only database connections for general inquiries to prevent unintended modifications.
* **REQ-CB-003: Response Formatting** 

  * The chatbot must return data in unstructured natural text, structured Markdown tables (for lists of products), or simple key-value blocks depending on data size.

### 2.2 Intent Detection & Mutation Safety

* **REQ-CB-004: Write-Intent Interception** 

  * The NLP model must classify incoming user intents.
  * If the intent involves an INSERT, UPDATE, or DELETE equivalent phrase (e.g., *"Change vendor price"*, *"Mark product 102 as picked up"*), the system must instantly halt automatic backend execution.
* **REQ-CB-005: Query Sanitization & Injection Blocking** 

  * The system must sanitize input to block SQL Injection patterns or prompt injection attempts designed to bypass the database authorization layer.

### 2.3 Human-in-the-Loop (HIL) Workflows

* **REQ-CB-006: Staging Payload Generation** 

  * Upon detecting an update intent, the backend must construct a temporary JSON change-payload containing: Target Table, Primary Key/ID, Field to Change, Old Value, and Proposed New Value.
* **REQ-CB-007: Visual Confirmation UI Card** 

  * Instead of standard text, the chatbot UI must render a locked **Confirmation Card Component**.
  * The card must clearly present the **Old Data vs. New Data** side-by-side.
  * The card must feature two functional UI inputs: an **[Approve & Save]** button and a **[Cancel]** button.
* **REQ-CB-008: Explicit Transaction Execution** 

  * The database update operation must only execute *after* a physical user click event is registered on the **[Approve & Save]** button.
  * If the user clicks **[Cancel]**, the staging payload is destroyed, and the chat replies: *"Update cancelled. No changes were made."*

### 2.4 Audit & Security Compliance

* **REQ-CB-009: User Session Authentication** 

  * Every user talking to the chatbot must be authenticated via an active login session.
* **REQ-CB-010: Write-Access RBAC (Role-Based Access Control)** 

  * If an unprivileged user attempts an update intent, the system must immediately reject it without generating an HIL payload (e.g., *"Error: You do not have permissions to modify this database."*).
* **REQ-CB-011: HIL Ledger Audit Logging** 

  * Every approved data mutation must write a ledger entry containing: timestamp, user_id, query_text, sql_executed, and a reference to the explicit user approval event.

### 3. Core Interface User Experience (UX) States

State 

User Input Example 

Chatbot Backend Action 

Expected UI Output 

****Data Inquiry****
*"What is the brokerage fee for vendor ABC today?"*Generates SELECT query against current ledger tables.Plain text reply with the precise calculated currency value.
****Modification Request****
*"Update item size for SKU-990 to Large."*Identifies write intent, queries old value, creates payload.Displays a comparison modal card with active **[Approve]** / **[Cancel]** buttons.
****Action: Cancel****
*Clicks [Cancel] button*Purges temporary update payload.Modifies the confirmation card to a disabled state showing *"Action Aborted"*.
****Action: Approve****
*Clicks [Approve] button*Verifies authorization, executes SQL UPDATE, writes audit log.Card updates to a green checkmark state showing *"Database successfully updated"*.
