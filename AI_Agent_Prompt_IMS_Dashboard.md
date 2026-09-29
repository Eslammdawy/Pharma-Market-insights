# Prompt: Build IMS Leafs Interactive Performance Dashboard

## Context
You are given the source file `IMS_June_2026_-_Leafs.xlsx`, sheet `IMS Leafs`, with these columns:

`Corporation | ATC4 | Product | Pack | Sector | Level | Period | LC Value Ranked | LC Value | LC Value Market Share | LC Value Growth % PY | Units | Units Market Share | Units Growth % PY`

Notes on the raw data:
- `Sector` has exactly two values: `PHARMACIES`, `STORES`.
- `Period` has exactly two values: `YTD Jun 2026`, `Q2 2026`.
- `Level` is constant (`Sector`) — ignore it.
- Rows are at **pack** level. The same (Corporation, Product, Sector, Period) combination can appear multiple times (once per `Pack`), so it must be aggregated up to product level before use — do not display raw pack rows directly.

## Deliverables
1. **A single standalone `.html` file** — fully self-contained (all CSS/JS inline or via CDN `<script>` tags; no local file dependencies other than the embedded dataset). Must open and work by double-clicking it, no server required.
2. **A `worklog.md` file** documenting every step you take: data extraction/cleaning decisions, aggregation logic implemented, design choices, and any assumptions made. Update it as you go, not just at the end.

## Data Processing (critical — do this before building the UI)

### 1. Extract and embed the data
Convert the Excel sheet to a compact JSON array (or array-of-arrays to save size) and embed it in the HTML (e.g. inside a `<script type="application/json" id="data">` block). Do not require the user to keep the Excel file next to the HTML.

### 2. Aggregate pack-level rows to product level
Group rows by **(Corporation, ATC4, Product, Sector, Period)** and collapse packs using this logic:

- **LC Value (aggregated)** = SUM of `LC Value` across the group.
- **Units (aggregated)** = SUM of `Units` across the group.
- **LC Value Growth % PY (aggregated)** — do NOT average the raw percentages. Back out each row's prior-year value, sum, then recompute:
  - `prior_i = LC Value_i / (1 + LC Value Growth % PY_i)`
  - `prior_agg = SUM(prior_i)`
  - `LC Value Growth % PY (agg) = (LC Value_agg − prior_agg) / prior_agg`
- **Units Growth % PY (aggregated)** — same method, using `Units` and `Units Growth % PY`.
- **LC Value Market Share / Units Market Share (aggregated)** — recompute, do not average the raw shares. Within the currently selected **Sector + Period** scope (see toggles below), the denominator is the total (LC Value or Units) summed across **all corporations and all products belonging to the same ATC4** as the row in question:
  - `Market Share = Group's aggregated metric / SUM(same metric across all corporations/products in that ATC4, for the same Sector+Period filter)`
  - This means shares in a filtered table should sum to 100% within that ATC4/Sector/Period view. Recalculate live whenever the Sector or Period toggle changes — do not reuse the raw per-row Excel market share values as-is.

Document the exact formulas you implement in `worklog.md`.

## Visual Design
- Professional, clean dashboard aesthetic. Primary palette built around **red, blue, and brown** (e.g. deep navy/blue for structure and headers, a controlled red as accent/alert or highlight color, brown/tan as a warm neutral for secondary elements and backgrounds) — avoid a garish or childish mix; keep contrast and whitespace corporate-grade.
- Consistent typography, spacing, and hover/active states across all 3 tabs.
- Left-hand fixed **sidebar** with 3 navigation tabs (icons + labels):
  1. **HPG Products Performance** (default/first tab shown on load)
  2. **ATC4 Performance**
  3. **Corporates Performance**

## Shared Behavior Across All 3 Tabs
Each tab follows the same layout pattern:

1. **Filter bar** at the top with a **live search-as-you-type box** (autocomplete/dropdown of matching results as the user types).
2. **Toggles** for **Sector** (PHARMACIES / STORES / both) and **Period** (YTD Jun 2026 / Q2 2026) placed above the table. Changing either toggle re-runs the aggregation (see Market Share formula above) and refreshes the table and chart immediately.
3. **Data table**, columns in this exact order:
   `Corporation | Product | Pack | LC Value | LC Value Market Share | LC Value Growth % PY | Units | Units Market Share | Units Growth % PY`
   - Sorted **descending by LC Value**.
   - Format currency/number columns with thousands separators, percentages with 1 decimal and a `%` sign, and growth values with a `+`/`−` sign and color coding (e.g. red for negative, blue/green for positive — stay within the palette).
4. **Bar chart** below the table that **stays in sync with the table** (same filtered/sorted rows):
   - X-axis: Product names (from the visible table rows).
   - Y-axis / value: `Units`.
   - Data labels positioned **outside the end** of each bar.
   - Chart re-renders whenever the filter, toggles, or selected item change.

## Tab-Specific Filter Logic

### Tab 1 — HPG Products Performance (default tab)
- The search bar only lists/searches **Products belonging to Corporation = `HEFNY GROUP*`** (i.e. restrict the autocomplete list to that corporation's products only).
- When the user selects a product from this filtered list:
  - Identify that product's `ATC4`.
  - The table then shows **all products within that same ATC4** (across **all corporations**, not just HEFNY GROUP*), aggregated per the rules above, one row per (Corporation, Product).
  - Sort descending by LC Value.
  - Chart below reflects the same rows (Products on X-axis, Units as value).

### Tab 2 — ATC4 Performance
- The search bar searches/lists **ATC4 categories** (all of them, not restricted to a corporation).
- When the user selects an ATC4:
  - The table shows all (Corporation, Product) combinations within that ATC4, aggregated per the rules above, sorted descending by LC Value.
  - Same toggles (Sector, Period) and same chart behavior as Tab 1.

### Tab 3 — Corporates Performance
- The search bar searches/lists **Corporations** (all of them).
- When the user selects a corporation:
  - The table shows that corporation's products (aggregated per the rules above), sorted descending by LC Value.
  - Same toggles (Sector, Period) and same chart behavior as Tab 1.

## Technical Requirements
- Pure HTML/CSS/JS (vanilla, or a lightweight charting library loaded via CDN, e.g. Chart.js) — keep it a single file.
- Handle the full dataset (~44k raw rows / ~28.7k unique pack-level combinations) client-side without noticeable lag — pre-aggregate where reasonable to keep interactions responsive.
- Empty/no-selection state: before the user picks anything from the filter, show a sensible default (e.g. a prompt message, or the top N products/ATC4s/corporations by LC Value) rather than a blank screen.
- Responsive layout (usable on a standard laptop screen at minimum).

## Acceptance Checklist (verify before final delivery)
- [ ] Single `.html` file opens standalone with no external file dependencies besides CDN scripts.
- [ ] `worklog.md` documents each step, including the exact aggregation/market-share formulas used.
- [ ] Sidebar with 3 correctly labeled tabs; Tab 1 loads by default.
- [ ] Tab 1 search restricted to HEFNY GROUP* products only; selecting one shows the full ATC4 peer set.
- [ ] Tab 2 search across all ATC4s; Tab 3 search across all corporations.
- [ ] Table columns, sort order, and formatting match spec exactly on all 3 tabs.
- [ ] Sector/Period toggles recompute aggregation and market share correctly, and update both table and chart.
- [ ] Bar chart stays synced to table on all 3 tabs, Units on Y-axis, data labels outside bar ends.
- [ ] Color palette is professional and consistently built around red/blue/brown.
