---
name: freee-analysis
description: "Use when: freee accounting, financial analysis, trial balance, journal entries, PL statement, expense breakdown, revenue analysis, tax preparation, monthly closing, profit and loss, balance sheet, accounts payable, accounts receivable. Instructs Claude to fetch freee data via MCP and produce analysis or visualization."
version: 1.0.0
---

# `/freee-analysis` — Accounting Data Analysis via freee MCP

> "Without data, you're just another person with an opinion." Accounting data holds your business health. This skill connects freee's live financial records to actionable insights by orchestrating MCP tool calls and synthesizing the results into structured analysis.

---

## When to Use This Skill

Invoke `/freee-analysis` when you need:

| Trigger | Example | Subcommand |
|---------|---------|------------|
| Financial analysis | Monthly P&L, revenue vs. prior period | `trial-balance` |
| Monthly closing review | Verify debit/credit balance at month-end | `monthly-close` |
| Expense audit | Break down expenses by category or vendor | `expenses YYYY-MM` |
| Revenue tracking | Compare monthly revenue trends | `revenue YYYY-MM` |
| Tax prep data | Aggregate deductible expense categories | `expenses YYYY` |
| Journal entry analysis | Inspect specific transactions or corrections | `journals YYYY-MM` |

**Key signals in user messages**: "freee", "accounting", "trial balance", "P&L", "profit and loss", "monthly close", "expense breakdown", "revenue", "仕訳", "試算表", "損益計算書", "経費"

---

## Usage

```
/freee-analysis trial-balance             Fetch and verify trial balance (current period)
/freee-analysis trial-balance 2026-02     Trial balance for a specific month
/freee-analysis expenses 2026-03          Expense breakdown for March 2026
/freee-analysis revenue 2026-Q1           Revenue summary for Q1 2026
/freee-analysis monthly-close             Full monthly closing checklist (trial balance + P&L)
/freee-analysis journals 2026-03          Inspect journal entries for March 2026
```

---

## Behavior

This is an instruction skill. Claude executes these steps when the skill is invoked:

### Step 1: Identify Required Data

Determine what data is needed based on the subcommand:
- `trial-balance`: account balances for the target period
- `expenses`: deal/transaction records filtered by expense accounts
- `revenue`: deal/transaction records filtered by revenue accounts
- `monthly-close`: trial balance + profit/loss report + unbalanced entry check
- `journals`: raw journal entries for the target period

### Step 2: Fetch Company Context

Before any data query, establish the company context:

1. Call `mcp__freee-mcp__freee_get_companies` to list available companies
2. If the user has specified a company, match by name or ID
3. If only one company exists, use it automatically
4. Store `company_id` — every subsequent API call requires it

### Step 3: Call Appropriate MCP Tools

Issue tool calls based on the data needed. Use the tool categories below as a guide. For unknown or exploratory analysis, use MCP tool discovery to find additional tools beyond this list.

### Step 4: Analyze the Fetched Data

Process the API results:
- Compute period-over-period deltas (e.g., revenue this month vs. last month)
- Group transactions by account code or category
- Detect anomalies: unusual expense spikes, zero-balance accounts that should have balances, unmatched debit/credit
- Check debit/credit balance for trial balance verification

### Step 5: Present Results

Output a structured markdown report:
- Summary table with key metrics
- Period comparison (if applicable)
- Anomaly flags (if any)
- Raw data table (collapsed or abbreviated for large datasets)

---

## Available MCP Tools

The following tool categories are available via the `freee-mcp` server. Tool names use the `mcp__freee-mcp__freee_*` prefix. This list is representative — use MCP tool discovery for the complete set.

### Account Tools
- `freee_get_companies` — List companies and their IDs (always call first)
- `freee_get_accounts` — Chart of accounts for a company
- `freee_get_account_items` — Detailed account item definitions

### Journal and Transaction Tools
- `freee_get_journals` — Raw journal entries for a date range
- `freee_create_journal` — Create a new journal entry (use with caution)
- `freee_get_deals` — Deals (income/expense transactions) with filter support
- `freee_get_expense_applications` — Expense reimbursement applications

### Report Tools
- `freee_get_trial_balance` — Trial balance report (debit/credit balances by account)
- `freee_get_profit_loss` — Profit and loss statement for a period
- `freee_get_balance_sheet` — Balance sheet at a point in time

### Partner and Tax Tools
- `freee_get_partners` — Vendor/customer master data
- `freee_get_taxes` — Tax category definitions

---

## Analysis Patterns

### Monthly P&L Comparison

1. Call `freee_get_profit_loss` for the current month and the prior month
2. Build a comparison table: account → this month → prior month → delta → delta%
3. Flag any line item with delta% > 20% as "notable change"
4. Summarize: total revenue, total expenses, operating profit, net income

### Expense Category Breakdown

1. Call `freee_get_deals` with `type=expense` and the target date range
2. Group transactions by `account_item_id` (expense account)
3. Sort by total amount descending
4. Present as a ranked table: account name → transaction count → total amount → % of total expenses
5. Optionally break down the top 3 accounts by individual transactions

### Trial Balance Verification

1. Call `freee_get_trial_balance` for the target period
2. Sum all debit balances and all credit balances
3. Verify they are equal — any discrepancy indicates an unbalanced entry
4. Flag accounts with unexpectedly zero balance (e.g., revenue accounts at zero mid-month)
5. Present a summary: total debit, total credit, balance status (OK / UNBALANCED)

### Revenue Trend (Multi-Period)

1. Call `freee_get_profit_loss` for each month in the target range (e.g., last 6 months)
2. Extract revenue line from each period
3. Build a time-series table and compute month-over-month growth rates
4. Identify trend direction: growing, stable, or declining

---

## Gotchas

### Company ID Requirement

Every freee API call requires a `company_id` parameter. Attempting to call account or report tools without first retrieving the company list will result in an error. Always call `freee_get_companies` first — even if the company ID seems obvious from context. The actual numeric ID may differ from what the user expects. Store the ID in working memory and pass it to every subsequent call.

### Fiscal Year Boundaries

freee fiscal years may not align with the calendar year. A company might have a March fiscal year-end, meaning "FY2025" runs from April 2025 to March 2026. Always check the company's fiscal year settings before constructing date-range queries. Using calendar-year date ranges on a non-calendar fiscal year produces incomplete or misleading report data. Confirm the fiscal period when the user asks for "annual" or "yearly" data.

### Rate Limiting

The freee API enforces rate limits. Fetching multiple months of detailed transaction data in rapid succession can trigger 429 responses. When running multi-period analysis (e.g., 12-month trend), introduce natural pauses between requests and handle 429 by retrying after the indicated wait time. Avoid fetching all journal entries for an entire year in a single request — prefer month-by-month queries.

### Data Freshness

freee data reflects the state after the last sync or manual entry. Recent transactions (particularly bank feed imports) may not appear until the next sync cycle completes. When analyzing "current month" data, advise the user that the analysis reflects data as of the last sync and that uncommitted entries may not be included. For closing-critical analysis, confirm that all entries have been posted before running the report.

### Read vs. Write Operations

This skill is primarily a read/analysis skill. The `freee_create_journal` tool modifies accounting records and cannot be undone without an explicit correcting entry. Before calling any write tools, confirm the user's intent explicitly. A mistaken journal entry in a closed period is an accounting compliance issue. When in doubt, present the intended entry for user review before executing it.

---

## Related Skills

| Skill | Path | When to Chain |
|-------|------|---------------|
| tps-kaizen | `skills/tps-kaizen/SKILL.md` | If the MCP calls fail repeatedly — use ANDON to diagnose the connection or authentication issue before retrying |
| qc-audit | `skills/qc-audit/SKILL.md` | After generating a financial report — use qc-audit to verify the report satisfies the completeness criteria defined in the analysis request |
