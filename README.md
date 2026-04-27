# 📊 SADE — Sistema de Análisis de Datos Económicos (Argentina)

> **Un Pipeline de Ingeniería de Datos (ETL) y CLI interactivo para la auditoría y análisis histórico de la macroeconomía argentina.**

SADE automatiza la extracción, limpieza, empalme y cruce de datos públicos (INDEC, BCRA, Ministerio de Economía) para generar *insights* financieros precisos. Transforma datos dispersos en reportes comparativos listos para consumir en dashboards (Power BI / Tableau) o analizar directamente en la terminal.

**Keywords / SEO:** `Data Engineering`, `ETL Pipeline`, `Python`, `Pandas`, `Macroeconomía Argentina`, `Dólar MEP`, `Dólar Blue`, `BCRA API`, `INDEC`, `Series Temporales`, `Data Analytics`.

---

## 💡 ¿Por qué existe SADE?

Los datos macroeconómicos de Argentina presentan desafíos técnicos severos para los analistas: cambios de base metodológica (apagones estadísticos), dispersión de fuentes, rezago temporal (*data lag*) y distorsiones por intervenciones estatales (cepos cambiarios). 

SADE resuelve esto mediante:
* **Series Splicing (Empalme):** Une series históricas descontinuadas con índices modernos automáticamente.
* **Waterfall Logic (Cascada Cambiaria):** Para análisis históricos, prioriza el Dólar MEP; si no existe, busca el Dólar Blue histórico; y como último recurso, el Oficial.
* **Alineación Base Cero:** Ajusta los mandatos presidenciales al "Mes 1" para permitir comparaciones justas entre distintas gestiones, independientemente del año en que ocurrieron.

---

## 🚀 Características Principales (Módulos Económicos)

SADE cuenta con una Interfaz de Línea de Comandos (CLI) interactiva que ofrece 6 motores de análisis:

1.  **📈 Tablero Ejecutivo de Coyuntura:** Snapshot en tiempo real del último mes vs. el anterior (Inflación, Reservas, Dólar MEP, Salarios, Riesgo País). Maneja asimetrías de tiempo informando la fecha exacta de cada variable.
2.  **🛒 Inflación Comparada:** Cálculo de inflación mensual y acumulada por mandato presidencial.
3.  **🏦 Reservas del BCRA:** Variación neta de reservas brutas en millones de dólares desde el día 1 de cada gestión.
4.  **💼 Poder Adquisitivo (Salario en USD):** Cruza el índice RIPTE (sueldos formales) con el Dólar Mercado (MEP/Blue) para obtener el salario real internacional.
5.  **💵 Dólar a Precios Constantes (TCRM):** Ajusta el valor histórico del dólar por la inflación acumulada hasta el día de hoy, permitiendo saber si el dólar actual está "caro" o "barato" frente a gestiones anteriores.
6.  **🏁 La Licuadora (Simulador de Ahorros):** Compara el rendimiento de $100.000 ARS a lo largo del tiempo bajo tres escenarios: Costo de Vida (Inflación), Tasa de Interés (Plazo Fijo BCRA) y Colchón (Dólar). Detecta escenarios de *Carry Trade* o *Tasa Real Negativa*.

---

## 🏗️ Arquitectura y Tech Stack

SADE está construido bajo una arquitectura ETL pura, modular y escalable.

| Capa | Tecnología | Propósito Técnico |
|---|---|---|
| **Extraction (E)** | `requests`, `APIs` | Consumo de endpoints REST (datos.gob.ar, argentinadatos) y lectura de parches estáticos locales. |
| **Transform (T)** | `pandas` | Limpieza, `merge` por granularidad `anio_mes`, cálculo de producto acumulado (`cumprod`), empalme de series (`combine_first`). |
| **Load (L)** | `CSV`, `OS` | Exportación estructurada de *Data Marts* limpios para herramientas de BI. |
| **Interfaz (UI)** | `questionary` | CLI interactivo, amigable y tipográfico para terminales. |
| **Data Viz** | `Power BI` | (En progreso) Dashboards de inteligencia de negocios. |

---

## ⚙️ Instalación y Uso Local

Requiere Python 3.8 o superior.

```bash
# 1. Clonar el repositorio
git clone [https://github.com/mathysaak/sade-economic-pipeline.git](https://github.com/mathysaak/sade-economic-pipeline.git)
cd sade-economic-pipeline

# 2. Crear y activar entorno virtual (Recomendado)
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el Panel de Control interactivo
python src/main.py