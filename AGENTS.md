# CSV Comparison Tool — Grok Build Project Guide

## Project Overview
A Streamlit web app that performs VLOOKUP-style CSV comparison between two datasets with 10 match methods (exact, fuzzy, domain prefix, etc.). Deployed via Docker on Hostinger.

## Stack
- **Frontend**: Streamlit (app.py)
- **Python**: 3.11, managed via pyproject.toml
- **Data**: pandas, numpy, plotly
- **AI**: xAI Grok API (OpenAI-compatible, base URL https://api.x.ai/v1)
- **Container**: Red Hat UBI9 + Python 3.11, docker-compose

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit UI, all pages and rendering logic |
| `utils/comparison_engine.py` | VLOOKUP comparison logic and 10 match methods |
| `utils/data_processor.py` | CSV loading, encoding detection, delimiter sniffing |
| `Dockerfile` | Production image; installs Grok Build CLI + Python deps |
| `docker-compose.yml` | App service (port 8501) + `grok-build` dev service |
| `pyproject.toml` | Python dependencies |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `XAI_API_KEY` | Yes (for AI features) | xAI SuperGrok Heavy API key |

## Development Conventions
- No comments unless the WHY is non-obvious
- No unused imports or dead code
- Streamlit session state keys: `df1`, `df2`, `comparison_results`, `current_page`
- All UI colours defined in the `COLORS` dict at the top of `app.py`
- Match result DataFrames always have `_match_status`, `_match_type_used`, `_has_duplicates` columns

## Running Locally
```bash
# App
docker compose up csv-comparison-tool

# Grok Build headless task
XAI_API_KEY=your_key docker compose run --rm grok-build -p "your task"
```

## Testing
No automated test suite yet. Validate by uploading sample CSVs through the UI and checking match counts.
