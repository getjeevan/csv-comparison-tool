# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run locally:**
```bash
streamlit run app.py
```
The local dev server (configured in `.streamlit/config.toml`) runs on port **5000**.

**Install dependencies:**
```bash
pip install -e .
```

**Run with Docker:**
```bash
docker compose up --build
```
Docker maps to port **8501**.

There are no tests or linting configurations in this project.

## Architecture

This is a single-page Streamlit application for VLOOKUP-style CSV comparison. The entry point is `app.py`, which contains all UI rendering logic and delegates data work to two utility classes.

### Data flow

1. User uploads two CSV files via sidebar → `DataProcessor.load_csv()` parses each into a DataFrame stored in `st.session_state` (`df1`, `df2`).
2. User configures key columns, return columns, and match methods, then clicks "Run Comparison" → `ComparisonEngine.vlookup_comparison()` executes.
3. Results are stored in `st.session_state.comparison_results` and rendered with row-level color highlighting and Plotly charts.
4. Users can download the filtered result set as CSV or Excel (with a stats summary sheet).

### `utils/data_processor.py` — `DataProcessor`

`load_csv()` auto-detects encoding and delimiter by trying every combination of `['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']` × `[',', ';', '\t', '|']`, skipping combinations that produce a single-column result (which indicates a wrong delimiter). The cleaned DataFrame strips whitespace from all string columns and converts `'nan'` strings back to `NaN`.

### `utils/comparison_engine.py` — `ComparisonEngine`

`vlookup_comparison()` is the core method. It:

1. For each selected match method, creates a standardized `_lookup_key_{i}` column on both DataFrames via `_standardize_lookup_key()`.
2. Builds a `lookup_dict` per match method (key → {col: value, `_duplicate_count`}) from df2 using `_create_lookup_dict()`. Duplicates are tracked; only the first occurrence is stored.
3. Iterates every row in df1 through `_perform_lookup()`, trying each match method in order and stopping at the first hit.

**Two categories of match methods** — distinguished by how they find matches:
- **Preprocessing-based** (use dict lookup after key transformation): Exact Match, Case Insensitive, Domain Prefix Match, Remove Special Chars, Numbers Only.
- **Iteration-based** (loop over all lookup dict keys for each row): Prefix Match, Suffix Match, Contains Match, Word Order Insensitive, Fuzzy Match. These are O(n × m) and can be slow on large datasets.

**Fuzzy Match** uses `difflib.SequenceMatcher` with an 80% similarity threshold.

### Result schema

The output DataFrame produced by `vlookup_comparison()` has these sentinel columns prepended:
- `_match_status` — `'Matched'` or `'Unmatched'`
- `_match_type_used` — which method produced the match
- `_has_duplicates` — whether the matched lookup key had duplicates

Columns pulled from df2 are suffixed with `_from_lookup`.

### Session state keys

`app.py` uses four `st.session_state` keys: `df1`, `df2`, `comparison_results`, `current_page` (`"Compare"` or `"How To"`).
