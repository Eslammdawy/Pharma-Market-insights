# Worklog — IMS Leafs Interactive Performance Dashboard

## 1. Project Overview & Deliverables
The objective of this project is to build an executive-grade, interactive performance dashboard from the raw dataset `IMS_June_2026_-_Leafs.xlsx` (Sheet: `IMS Leafs`), covering pharmaceutical sales data for Egypt (June 2026).

**Deliverables:**
1. `IMS_Dashboard.html`: A self-contained, standalone single HTML file (CSS, JS, dataset embedded as compact JSON, and base64-encoded HPG logo). Works offline via local double-click without needing a web server.
2. `worklog.md`: Detailed documentation of data extraction, cleaning decisions, exact aggregation and market-share mathematical formulas, technical design choices, and validation steps.

---

## 2. Exploratory Data Analysis (EDA) & Data Cleaning Decisions

### 2.1 File Structure & Columns
Inspection of `IMS_June_2026_-_Leafs.xlsx` revealed:
- **Sheet Name**: `IMS Leafs`
- **Total Rows**: 44,023 rows (1 header row + 44,022 data rows)
- **Columns (13 total)**:
  1. `Corporation` (String)
  2. `ATC4` (String)
  3. `Product` (String)
  4. `Pack` (String)
  5. `Sector` (String: exactly two values — `PHARMACIES`, `STORES`)
  6. `Level` (Constant: `Sector` — ignored as per spec)
  7. `Period` (String: exactly two values — `YTD Jun 2026`, `Q2 2026`)
  8. `LC Value` (Numeric: Local Currency in EGP)
  9. `LC Value Market Share` (Decimal percentage: 0.0 to 1.0)
  10. `LC Value Growth % PY` (Decimal growth rate vs Prior Year)
  11. `Units` (Numeric: physical packs sold)
  12. `Units Market Share` (Decimal percentage: 0.0 to 1.0)
  13. `Units Growth % PY` (Decimal growth rate vs Prior Year)

### 2.2 Data Characteristics & Edge Cases
- **Corporation Naming**: Hefny Group is represented as `HEFNY GROUP*` (with an asterisk).
- **Hefny Group Scope**: 132 unique commercial products across numerous therapeutic classes.
- **Market Scope**: 1,215 unique corporations across 326 ATC4 therapeutic classes.
- **Zero / None Values**: 5,808 rows have `None` for `LC Value` and `Units` (inactive/dormant packs). In data extraction, these are treated as `0.0` so they do not produce `NaN` or distort aggregate sums.
- **Growth Rates**: Rows with active sales have defined growth figures. Rows where growth is `-1.0` (-100%) represent discontinued products or packs with no current-year sales.
- **Multi-ATC4 Product Mapping**: Notably, the HEFNY product `LORNICAM` appears under two distinct ATC4 classes (`M01A1 ANTIRHEUMATICS NON-S PLN` and `N02B0 NON-NARCOTIC ANALGESICS`). The lookup architecture was specially updated to map products to arrays of ATC4 categories, ensuring full competitive sets are retrieved.

---

## 3. Aggregation & Recomputation Logic

### 3.1 Pack-to-Product Level Aggregation
Raw data is grouped by `(Corporation, ATC4, Product, Sector, Period)`.
Collapsing packs produces 29,228 product-level records.

#### Formulas:
1. **Aggregated LC Value**:
   $$\text{LC Value}_{agg} = \sum_{i \in \text{packs}} \text{LC Value}_i$$

2. **Aggregated Units**:
   $$\text{Units}_{agg} = \sum_{i \in \text{packs}} \text{Units}_i$$

3. **Aggregated LC Value Growth % PY**:
   Raw percentage growth rates cannot be averaged. Each pack's prior-year sales figure is back-calculated:
   $$\text{Prior LC Value}_i = \frac{\text{LC Value}_i}{1 + \text{LC Value Growth % PY}_i}$$
   $$\text{Prior LC Value}_{agg} = \sum_{i \in \text{packs}} \text{Prior LC Value}_i$$
   $$\text{LC Value Growth % PY}_{agg} = \frac{\text{LC Value}_{agg} - \text{Prior LC Value}_{agg}}{\text{Prior LC Value}_{agg}}$$
   *(If $\text{Prior LC Value}_{agg} = 0$, growth is set to 0.0)*

4. **Aggregated Units Growth % PY**:
   $$\text{Prior Units}_i = \frac{\text{Units}_i}{1 + \text{Units Growth % PY}_i}$$
   $$\text{Prior Units}_{agg} = \sum_{i \in \text{packs}} \text{Prior Units}_i$$
   $$\text{Units Growth % PY}_{agg} = \frac{\text{Units}_{agg} - \text{Prior Units}_{agg}}{\text{Prior Units}_{agg}}$$

### 3.2 Dynamic Cross-Sector Aggregation (`Sector = BOTH`)
When the user selects `BOTH` (Pharmacies + Stores), rows are combined across sectors for the same `(Corporation, ATC4, Product, Period)`.
- Summed values: $\text{LC Value}_{BOTH} = \text{LC Value}_{PHARMACIES} + \text{LC Value}_{STORES}$
- Combined growth is recalculated using the exact same prior-year sum formula above:
  $$\text{Prior}_{BOTH} = \frac{\text{Val}_{PHARM}}{1 + \text{Gr}_{PHARM}} + \frac{\text{Val}_{STORES}}{1 + \text{Gr}_{STORES}}$$
  $$\text{Growth}_{BOTH} = \frac{\text{Val}_{BOTH} - \text{Prior}_{BOTH}}{\text{Prior}_{BOTH}}$$

### 3.3 Dynamic Market Share Recomputation
Market share is recomputed live in the browser whenever Sector or Period toggles change.
The denominator represents the total volume of that product's ATC4 class across **all corporations and all products** in the active `(Sector, Period)` scope:

$$\text{ATC4 Total LC Value} = \sum_{k \in \text{all products in ATC4}} \text{LC Value}_k$$
$$\text{ATC4 Total Units} = \sum_{k \in \text{all products in ATC4}} \text{Units}_k$$

$$\text{LC Value Market Share} = \frac{\text{Product LC Value}}{\text{ATC4 Total LC Value}}$$
$$\text{Units Market Share} = \frac{\text{Product Units}}{\text{ATC4 Total Units}}$$

**Guarantees:**
- Within any selected ATC4 view (Tab 1 peer set or Tab 2 ATC4 selection), the market shares of all displayed products sum to exactly 100.0%.
- In Tab 3 (Corporates Portfolio) and Default Views (Top 20), each product displays its true market share in its therapeutic class.

---

## 4. UI & Visual Design Choices

Aligned with the user interview decisions:
1. **Corporate Color Palette**:
   - Primary Structure: Deep Navy (`#1a2332`, `#253347`) for sidebar and table headers.
   - Accents / Negative Growth: Controlled Crimson Red (`#c0392b`).
   - Positive Growth / Active Links: Corporate Blue (`#2471a3`, `#2e86c1`).
   - Warm Neutral Secondary: Tan/Brown (`#8b6914`, `#f5f0eb`, `#ded3c3`) for borders, cards, and page background.
2. **Fixed Sidebar**:
   - Top: Base64-encoded `HPG logo.jpg` (35.4 KB).
   - Navigation: 3 tabs with clear icons and active red border indicators.
   - Tab 1: **HPG Products Performance** (Default tab).
   - Tab 2: **ATC4 Performance**.
   - Tab 3: **Corporates Performance**.
3. **Filter Bar**:
   - Live autocomplete search input with instant matching, keyboard navigation (`ArrowUp`, `ArrowDown`, `Enter`, `Escape`), and `✕` clear button.
   - Sector toggles: `Both`, `Pharmacies`, `Stores`.
   - Period toggles: `YTD Jun 2026`, `Q2 2026`.
4. **KPI Summary Cards**:
   - Total LC Value (EGP, compact + full number).
   - Total Units (compact + full number).
   - Products Count (or HPG Market Share when an ATC4 is selected in Tab 1).
   - Weighted Average LC Growth vs PY.
5. **Data Table**:
   - Columns in exact specified order: `Corporation`, `Product`, `Pack`, `LC Value`, `LC Value Market Share`, `LC Value Growth % PY`, `Units`, `Units Market Share`, `Units Growth % PY`.
   - Sorting: Default sorted descending by LC Value. Clickable headers allow sorting by any column.
   - Number formatting: Thousands separators for values, 1 decimal place with `%` for shares, `+`/`−` with blue/red coloring for growth.
   - Expandable Pack Breakdown: Click `▶` or the pack badge to reveal individual pack rows with pack-level metrics and growth.
   - Row Highlighting: `HEFNY GROUP*` products feature a distinct subtle blue tint (`rgba(36,113,163,0.08)`) and blue indicator border to stand out against competitors.
6. **Synchronized Bar Chart**:
   - Built with Chart.js 4.4 and `chartjs-plugin-datalabels`.
   - X-axis: Product names (full name on tooltip).
   - Y-axis: Units.
   - Outside-end data labels with compact formatting (e.g. `2.3M`, `850K`).
   - Visual color coding: HPG products in corporate blue, competitor products in dark navy.
   - Automatically re-renders on toggle, filter, search, or sort changes.

---

## 5. Technical Pipeline & File Manifest

| File | Purpose |
|---|---|
| `IMS June 2026 - Leafs.xlsx` | Raw Excel source data (44,022 rows). |
| `HPG logo.jpg` | Corporate logo image (base64 embedded in output). |
| `AI_Agent_Prompt_IMS_Dashboard.md` | Original requirements specification. |
| `extract_data.py` | Python extraction script using `openpyxl`, computing pre-aggregations, growth back-calculations, lookups, and injecting into the HTML template. |
| `dashboard_template.html` | Dashboard layout, CSS styling, and interactive JavaScript application logic. |
| `IMS_Dashboard.html` | Standalone, self-contained interactive dashboard (11.6 MB). |
| `worklog.md` | Comprehensive technical log, mathematical formulations, and verification records. |

---

## 6. Acceptance Criteria Verification

- [x] **Standalone HTML File**: `IMS_Dashboard.html` is 11.6 MB, opens directly in web browser via double-click without a web server.
- [x] **Worklog**: `worklog.md` documents all data cleaning decisions, aggregation logic, mathematical formulas, and UI specifications.
- [x] **Sidebar & Tabs**: Left fixed navy sidebar with HPG logo, 3 tabs; Tab 1 loads by default.
- [x] **Tab 1 Filter**: Search restricted to `HEFNY GROUP*` products (132 products); selecting one reveals its full ATC4 competitive peer set. Multi-ATC4 products (e.g. `LORNICAM`) properly handled.
- [x] **Tab 2 Filter**: Search across all 326 ATC4 categories; selecting one displays all competing products.
- [x] **Tab 3 Filter**: Search across all 1,215 corporations; selecting one displays its product portfolio.
- [x] **Default Landing States**: Shows Top 20 products by LC Value before search selection.
- [x] **Data Table Specifications**: Columns in exact order, default descending sort by LC Value, expandable pack rows, numbers formatted with separators, percentages with 1 decimal, growth with signs and color coding.
- [x] **Live Recomputation**: Sector and Period toggles trigger instant market share and growth recalculation.
- [x] **Synced Bar Chart**: Chart.js vertical bar chart with outside-end data labels, synced with table data.
- [x] **Corporate Palette**: Deep navy, controlled red, corporate blue, and warm tan/brown.

---

## 7. UI Enhancements & Table Expansion (Update)

1. **Sidebar Compaction & Layout Optimization**:
   - Sidebar width reduced from `245px` to `180px` (`--sidebar-w: 180px;`).
   - Logo, typography, and navigation spacing scaled down proportionally (`64px` logo width, `12.5px` nav links) to maintain a clean layout without text wrapping.
   - Main content padding optimized from `24px 32px 40px` to `20px 20px 36px`, granting **89px of additional horizontal space** for the table and charts.
   - Table cell padding tightened to `9px 10px` (headers) and `7px 10px` (body cells), saving another ~44px across columns.

2. **Rank Column**:
   - Added a dedicated `Rank` column as the very first column in the data table (`<th class="no-sort rank-th">Rank</th>`).
   - Dynamically calculates each row's rank (`1` to `N`) according to the active sort column and direction (LC Value, Units, Growth, Market Share, Corporation, or Product).
   - Rendered using elegant tabular number badges (`.rank-badge`) with top-3 visual highlights (`top-1`, `top-2`, `top-3`) adhering to the brand palette, and branded blue styling for `HEFNY GROUP*` rows.
   - All pack drill-down sub-rows aligned with the new 11-column table schema.
   - Deterministic tie-breaking by LC Value descending implemented to ensure stable, reproducible ranking when primary sort keys are tied.

3. **Export to Excel Feature**:
   - Positioned directly above the data table in `.table-header-bar` inside `.table-tools`, right alongside the HPG legend and live product count.
   - **Executive Styling**: Built with corporate Excel emerald green (`#107c41`, hover `#0b6a37`) and an embedded vector spreadsheet SVG icon, maintaining complete visual hierarchy with the dashboard palette.
   - **Export Button Group & Dropdown**:
     - **Primary Button (`Export to Excel`)**: Single-click export of data **exactly as shown in the table** (active tab, sector, period, search selection, sort order, and any currently expanded pack breakdown rows).
     - **Dropdown Menu Options**:
       - *Export Current View*: Exports only what is currently rendered on screen (including any open pack rows).
       - *Export with All Pack Details*: Automatically exports all displayed products with their complete pack breakdowns.
       - *Export Products Only*: Exports product summary rows without pack breakdown.
     - **Companion Toolbar Button (`▾ Expand All` / `▴ Collapse All`)**: Allows the user to toggle expansion of all product packs on the page simultaneously with one click.
   - **Exported Column Schema**:
     1. `Rank` (integer)
     2. `Corporation` (text)
     3. `Product` (text)
     4. `Pack` (summary pack count or indented pack description `↳ [Pack Name]`)
     5. `LC Value` (formatted numeric `#,##0`)
     6. `LC Value Market Share` (formatted percentage `0.0%`, or `—` for pack rows)
     7. `LC Value Growth % PY` (formatted signed growth `+0.0%;-0.0%;0.0%`)
     8. `Units` (formatted numeric `#,##0`)
     9. `Units Market Share` (formatted percentage `0.0%`, or `—` for pack rows)
     10. `Units Growth % PY` (formatted signed growth `+0.0%;-0.0%;0.0%`)
   - **Data Fidelity & Number Formatting**:
     - Numeric values (`v`, `u`, `vg`, `ug`, `lcMs`, `unMs`) are exported as genuine numeric values formatted with Excel number format codes (`z: '#,##0'`, `z: '0.0%'`, `z: '+0.0%;-0.0%;0.0%'`). This guarantees that values visually mirror the dashboard display while allowing users to execute `=SUM()`, `=AVERAGE()`, and pivot operations inside Microsoft Excel.
     - Auto-adjusted column widths (`!cols`) and automatic header AutoFilter (`!autofilter`) applied.
   - **Dual Engine / Offline Resilience**:
     - Primary: SheetJS (`xlsx.full.min.js` v0.18.5) generates native binary `.xlsx` workbooks.
     - Fallback: Pure JavaScript Excel XML SpreadsheetML (`.xls`) generator using standard browser `Blob` download, ensuring the feature functions 100% offline even without internet connectivity.
   - **Contextual File Naming**:
     - Dynamically names the exported file based on the active tab, selected entity, period, and sector (e.g. `IMS_HPG_Products_YTD_Jun_2026_BOTH.xlsx`, `IMS_ROTAPYRETIC_ATC4_YTD_Jun_2026_BOTH.xlsx`), with Windows filename sanitization.

---

## 8. Top-N Selector, Scorecard Reactivity, Frozen Columns & Show More Removal

1. **Top-N Selector (Top 20 / 50 / All)**:
   - Added on top of the data table inside `.table-header-bar` toolbar (`.topn-group`), active across all table views (Tabs 1–3: HPG Products, ATC4 Performance, Corporates).
   - Options provided: `Top 20`, `Top 50`, `All`.
   - **Default State**: Configured to `All` as the default (`state.tableTopN = 'all'`).
   - Clean executive pill toggle design matching the brand's navy and warm tan aesthetic.

2. **Removal of "Show 50" & "Show 100" Toggles**:
   - Completely removed `#showMoreBar` under the data table, along with its supporting CSS (`.show-more-bar*`, `.active-limit`) and JavaScript methods (`setViewLimit`, `updateShowMoreBar`).
   - The former `viewLimit` logic is replaced by the unified top-level Top-N selector.

3. **Scorecard (KPI) & Chart Reactivity**:
   - The top KPI cards (`Total LC Value`, `Total Units`, `Products` / `HPG Market Share`, `Avg LC Growth`) are computed from the active view dataset returned by `getTableData()`.
   - When switching between `Top 20`, `Top 50`, and `All`, the KPI values immediately update to reflect the aggregate LC value, units sold, weighted growth rate, and product count of the selected subset.
   - Card 3 subtitle dynamically reflects the active view mode (e.g., `Top 20 in view`, `Top 50 in view`, `All products in view`).
   - Table count and dynamic headers adapt automatically to the active Top-N selection.

4. **Frozen First 3 Columns (Sticky Header & Left Columns)**:
   - Sticky positioned the first 3 columns across every table in all tabs:
     1. Column 1: `Rank` (`left: 0px`, `width: 46px`)
     2. Column 2: `Expand / Drill-down button` (`left: 46px`, `width: 28px`)
     3. Column 3: `Corporation` (`left: 74px`)
   - Configured `.data-table` with `border-collapse: separate; border-spacing: 0;` ensuring sticky coordinates render accurately across all modern browsers.
   - Configured `z-index: 20` for sticky `thead` header cells and `z-index: 5` for sticky `tbody` cells, with sticky header at `z-index: 10`.
   - Applied explicit backgrounds (`var(--white)`, `#faf7f2`, `var(--hpg-bg)`) to prevent scrolling content from bleeding through frozen columns.
   - Applied a subtle drop shadow (`box-shadow: 3px 0 6px -2px rgba(0,0,0,0.12)`) along the right boundary of the 3rd column (`Corporation`) for clear visual separation during horizontal scroll.
