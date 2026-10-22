# IMS Leafs Interactive Performance Dashboard

An executive-grade, standalone business intelligence dashboard built for **Hefny Pharma Group (HPG)** to monitor, benchmark, and analyze pharmaceutical market performance across Egypt for **June 2026 / Q2 2026**.

The project transforms raw pack-level IMS/IQVIA audit data into an interactive, zero-dependency, single-file HTML dashboard capable of running offline in any modern web browser.

---

## 📌 Executive Summary & Key Capabilities

- **Zero-Backend Architecture**: Distributed as a single self-contained file ([`IMS_Dashboard.html`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/IMS_Dashboard.html)). Embedded with full compressed dataset records, CSS styles, JavaScript logic, and base64-encoded corporate assets. Works offline via a simple double-click.
- **Accurate Aggregation Engine**: Reconstructs pack-level transactions into product-level benchmarks without mathematical distortion:
  - Back-calculates prior-year base volumes to prevent raw growth averaging errors.
  - Dynamically recalculates ATC4 therapeutic market shares live in-browser upon filtering.
- **Competitive Benchmarking**: Instant competitor discovery within the same ATC4 class when inspecting any HPG product.
- **Interactive Visualizations & Data Export**: Integrated Chart.js bar charts dynamically linked to table filtering and sorting, with one-click export to Excel (`.xlsx`).

---

## 🧭 Dashboard Modules (Navigation Tabs)

The dashboard provides three specialized analytical perspectives via the fixed navigation sidebar:

### 1. 🏢 HPG Products Performance (Default Tab)
- **Scope**: Search-as-you-type filter restricted exclusively to **`HEFNY GROUP*`** products (132 commercial products).
- **Peer Landscape**: Selecting an HPG product automatically detects its therapeutic classification (`ATC4`) and displays the **entire competitive market** across all competing corporations in that ATC4.
- **Key Insight**: Immediately benchmark Hefny product performance, rank, and market share against direct market peers.

### 2. 💊 ATC4 Performance
- **Scope**: Autocomplete search covering all **326 therapeutic classes** in the Egyptian pharmaceutical market.
- **Market Dynamics**: Displays all corporations and products competing within the selected ATC4 class, ranked by Local Currency Value (`LC Value`) or volume (`Units`).
- **Total Market Share**: Market shares automatically sum to **100.0%** across the active sector and period scope.

### 3. 🌐 Corporates Performance
- **Scope**: Search across all **1,215 pharmaceutical manufacturers and marketing corporations**.
- **Portfolio Breakdown**: Analyzes the complete commercial portfolio of the selected corporation, showing sales values, volume, growth rates, and category market shares.

---

## ⚙️ Interactive Controls & Filters

Every tab features real-time, zero-latency controls:
- **Sector Toggle**:
  - `PHARMACIES` (Community retail pharmacies)
  - `STORES` (Direct retail stores / supply chains)
  - `BOTH` (Consolidated market view combining Pharmacies and Stores)
- **Period Toggle**:
  - `YTD Jun 2026` (Year-to-Date cumulative performance)
  - `Q2 2026` (Second quarter quarterly performance)
- **Real-Time Search Bar**: Instant typeahead filter with highlighted matches and quick-clear controls.
- **Synchronized Visuals**: Interactive unit-volume bar chart displaying data labels outside bars, updating automatically whenever table data or filters change.
- **Excel Export**: Export the currently filtered and calculated view into a clean `.xlsx` file directly from the browser.

---

## 📐 Mathematical & Aggregation Methodology

Raw rows in `IMS_June_2026_-_Leafs.xlsx` are recorded at the individual **pack** level. Displaying pack rows directly would distort product comparisons. The pipeline uses the following mathematical logic:

### 1. Pack-to-Product Aggregation
For each unique `(Corporation, ATC4, Product, Sector, Period)` group:
$$\text{LC Value}_{agg} = \sum \text{LC Value}_{pack}$$
$$\text{Units}_{agg} = \sum \text{Units}_{pack}$$

### 2. Prior-Year Growth Rate Recomputation
Averaging growth percentages is mathematically invalid across varying volume weights. Prior-year sales figures are back-calculated per pack, summed, and recalculated:
$$\text{Prior Value}_i = \frac{\text{Value}_i}{1 + \text{Growth \% PY}_i}$$
$$\text{Prior Value}_{agg} = \sum \text{Prior Value}_i$$
$$\text{Aggregated Growth \% PY} = \frac{\text{Value}_{agg} - \text{Prior Value}_{agg}}{\text{Prior Value}_{agg}}$$

### 3. Live Dynamic Market Share Calculation
When switching sectors or periods, market shares are recalculated dynamically against the total volume of all products in that ATC4 class:
$$\text{ATC4 Total Value} = \sum_{k \in \text{ATC4}} \text{Value}_k$$
$$\text{Market Share} = \frac{\text{Product Value}}{\text{ATC4 Total Value}} \times 100\%$$

---

## 📁 Repository Structure

```text
├── AI_Agent_Prompt_IMS_Dashboard.md   # Original project specification and requirements
├── extract_data.py                    # Python ETL pipeline & HTML generation script
├── dashboard_template.html            # Web template containing styles, UI structure, and JS logic
├── HPG logo.jpg                       # Corporate logo asset (encoded as base64 in HTML)
├── IMS June 2026 - Leafs.xlsx         # Raw source data (44,023 rows, sheet: "IMS Leafs")
├── IMS_Dashboard.html                 # Standalone production dashboard (~12 MB single-file HTML)
├── worklog.md                         # Detailed engineering log, data decisions, and formulas
└── README.md                          # Project documentation (this file)
```

---

## 🚀 Quick Start Guide

### Option 1: View the Dashboard (No Installation Required)
Simply open [`IMS_Dashboard.html`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/IMS_Dashboard.html) in any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).
- No web server, Node.js, or Python environment is needed.
- Network access is only required on initial load to fetch lightweight chart libraries via CDN (`chart.js`, `chartjs-plugin-datalabels`, `xlsx`).

### Option 2: Regenerate Dashboard from Source Data
To re-process the raw Excel sheet and rebuild `IMS_Dashboard.html`:

1. **Prerequisites**: Ensure Python 3.8+ is installed with `openpyxl`:
   ```powershell
   python -m pip install openpyxl
   ```

2. **Run ETL Script**:
   ```powershell
   python extract_data.py
   ```

3. **Output**:
   The script reads [`IMS June 2026 - Leafs.xlsx`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/IMS%20June%202026%20-%20Leafs.xlsx), computes aggregations, serializes compact JSON representations, embeds [`HPG logo.jpg`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/HPG%20logo.jpg), and outputs the updated [`IMS_Dashboard.html`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/IMS_Dashboard.html).

---

## 🛠️ Technology Stack

| Layer | Component | Description |
|---|---|---|
| **ETL & Data Processing** | Python 3 (`openpyxl`) | Parses raw Excel workbook, aggregates pack records, and generates JSON data payloads |
| **User Interface** | HTML5 / Modern CSS3 | Custom corporate color palette (Navy `#1a2332`, Red `#c0392b`, Blue `#2471a3`, Tan `#f5f0eb`) |
| **Client Engine** | Vanilla JavaScript (ES6+) | In-memory indexing, dynamic aggregation, live filtering, and state management |
| **Charting** | Chart.js 4.4.7 + DataLabels Plugin | Responsive bar charts with value labels rendered on top of bars |
| **Spreadsheet Export** | SheetJS (xlsx 0.18.5) | Client-side Excel workbook generation |

---

## 📖 Additional Documentation
For complete technical notes, data cleaning edge cases, and step-by-step engineering records, refer to [`worklog.md`](file:///d:/HPG/Project%20AI/Marketing/IMS/IMS%20June%20AG/worklog.md).
