
## **35.16 STA1 Metadata Analysis (notebook `47_sta_metadata_analysis.ipynb`)**

Re-running the two-tier analysis with official STA1 metadata ($I illustration type, $L Currier language, $H writing hand) instead of approximate section assignments yields three findings:

1. **Two-tier by illustration type**: Astronomical has lowest %F (27.6%) and highest %O-C (20.4%); Biological has highest %F (61.9%). Utilisation is stable (4.4–6.1%) across all 8 types — the selectivity constraint is code-wide.

2. **Currier "languages" are two registers**: Language A (%F=41.8) is content-heavy; Language B (%F=52.8) is 11pp more functional. Both maintain ~6% utilisation and ~1.8 O/C ratio. Not two languages but two registers: A for descriptions, B for instructions.

3. **Writing hands = vocabulary communities**: Community × hand (χ²=82,857) correlates more strongly than community × illustration type (χ²=79,123) or × language (χ²=44,776). Community 0 = Hand 1/Lang A; Community 2 = Hands 2+3/Lang B. Each scribe used a distinct vocabulary subset — responsible for different domains.

4. **Identifier uniqueness**: 98–100% across all 8 illustration types.

Notebook: `47_sta_metadata_analysis.ipynb`
Results: `resultados/sta_metadata_resultados.json`
