
## **35.17 Selectivity Matrix, Register Lexicons, and Isolated Folios (notebook `48_selectivity_and_registers.ipynb`)**

### Selectivity matrix
The full onset × coda co-occurrence matrix (164 × 87) has 90% zero entries — confirming ~90% of combinations are forbidden. Hierarchical clustering reveals 8 onset blocks. The three most productive onsets (K1, A1, D1.A1) form a "universal" block sharing 40 codas — the code's workhorses. Top O-C pair: [K1]+[K2.A2] (171 occurrences).

### Register lexicons
- **A-only vocabulary**: 2,711 types — %F=4.5%, %T2=74.6% (almost entirely technical content)
- **B-only vocabulary**: 4,958 types — %F=25.2%, %T2=59.1% (substantially more functional)
- **Shared**: 1,156 types
- Herbal section has highest inter-register overlap (Jaccard=0.113); Bio and Pharma have ZERO overlap — completely disjoint vocabularies per register

### Isolated folios
16 folios form singleton communities (no shared T2 vocabulary at Jaccard > 0.05):
f27v, f31r, f41r, f48r, f65r, f67v1, f67v2, f68r1-3, f71v, f72r3, f72v1-2, etc.
- Isolates are more technical: %F=25.5% vs non-isolates 42.0%
- Many are zodiac folios — astrological vocabulary is so specialised it doesn't overlap with other sections
- f116v (anomalous, nearly blank) is among the isolates

Notebook: `48_selectivity_and_registers.ipynb`
Results: `resultados/selectivity_registers_resultados.json`
