# AGENTS.md — "Sugar Trap" Market Gap Analysis

## Project
Helix CPG Partners consultancy project: find "Blue Ocean" opportunities in the snack aisle using Open Food Facts data. Identify under-served categories where demand for health (High Protein, High Fiber) isn't met by current offerings (High Sugar, High Fat).

## Data
- `openfoodfacts_500k.csv` — 500k-row subset of Open Food Facts. Key columns: `product_name`, `categories_tags` (comma-separated, e.g. `en:snacks, en:biscuits`), `sugars_100g`, `proteins_100g`, `fat_100g`, `fiber_100g`, `ingredients_text`, `nutriscore_grade`, `nova_group`, `countries_en`, `brands`.
- Use **relative paths** only (assume CSV is in same folder as notebook). Never commit the CSV to git.

## Deliverables (User Stories 1–4 + Bonus)
1. **Data Cleaning**: Drop rows missing `sugars_100g`/`proteins_100g`/`product_name`; filter biologically impossible values (e.g. sugar > 100g/100g).
2. **Category Wrangling**: Parse `categories_tags`, assign ≥5 high-level "Primary Category" buckets via keyword matching.
3. **Nutrient Matrix**: Scatter plot Sugar (X) vs Protein (Y), filterable by category; highlight the "Empty Quadrant" (High Protein + Low Sugar).
4. **Recommendation**: Key Insight text box: "Biggest opportunity is in [Category], targeting [X]g protein / <[Y]g sugar."
5. **Bonus – Hidden Gem**: Analyze `ingredients_text` for high-protein cluster; extract top 3 protein sources.
6. **Candidate's Choice**: Add one extra chart/metric with justification.

## Tooling & Style
- **Language**: Python 3 (Pandas, Matplotlib/Seaborn/Plotly). Notebook format (`.ipynb`), export to HTML/PDF.
- **Dashboard**: Must be publicly accessible (Streamlit Cloud, Tableau Public, Power BI Web, or Looker Studio).
- **Conventions**: PEP 8, descriptive variable names, inline markdown explanations in notebook cells. No hardcoded local paths.
