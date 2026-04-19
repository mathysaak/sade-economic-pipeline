# sade-economic-pipeline
# SADE — Sistema de Análisis de Datos Económicos

> Automated pipeline to extract, validate, and store Argentine macroeconomic 
> indicators from public sources (INDEC, BCRA, and others).

## Why this project exists

Argentina's macroeconomic data is scattered across multiple government sources,
published in inconsistent formats, and frequently revised without clear versioning.
SADE automates the extraction and applies validation rules to detect anomalies
before the data reaches storage — making it usable for analysis.

## Architecture
[Government APIs / Web Sources]
↓
[Extractor layer — Python + Playwright]
↓
[Validation / QA rules — Pandas]
↓
[Storage — SQL / Excel]
↓
[Visualization — Tableau / Power BI] ← in progress

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Extraction | Python + Playwright | API calls + fallback scraping |
| Validation | Pandas | Anomaly detection, format checks |
| Storage | SQLite / Excel | Structured output |
| Visualization | Power BI (WIP) | Economic dashboards |

## Current status

- [x] Extractor for [source name, e.g. INDEC CPI data]
- [x] Basic validation rules (null checks, range anomalies)
- [ ] Additional indicators (BCRA reserves, exchange rates)
- [ ] Automated scheduling
- [ ] Power BI dashboard

## Running locally

```bash
git clone https://github.com/mathysaak/sade-economic-pipeline
cd sade-economic-pipeline
pip install -r requirements.txt
python src/extractors/[script_name].py
```

## Data sources

- INDEC (Instituto Nacional de Estadística y Censos)
- BCRA (Banco Central de la República Argentina)

---

*Personal project — built to practice data engineering and explore Argentine
macroeconomic trends. Not affiliated with any government entity.*
