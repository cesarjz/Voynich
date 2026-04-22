
## 35.16 Análisis de metadatos STA1 (notebook `47_sta_metadata_analysis.ipynb`)

Re-ejecutando el análisis two-tier con los metadatos oficiales del STA1 ($I tipo de ilustración, $L lenguaje Currier, $H mano del escriba) en vez de asignaciones aproximadas por número de folio:

1. **Two-tier por tipo de ilustración**: Astronómica tiene el menor %F (27.6%) y mayor %O-C (20.4%); Biológica el mayor %F (61.9%). La utilización es estable (4.4–6.1%) en los 8 tipos — la restricción de selectividad es global del código.

2. **Los "lenguajes" Currier son dos registros**: Lenguaje A (%F=41.8) es más técnico; B (%F=52.8) es 11pp más funcional. Ambos mantienen ~6% utilización y ~1.8 ratio O/C. No son dos lenguas sino dos registros: A para descripciones, B para instrucciones.

3. **Manos de escriba = comunidades de vocabulario**: Comunidad × mano (χ²=82,857) correlaciona más que × tipo de ilustración (χ²=79,123) o × lenguaje (χ²=44,776). Cada escriba usó un subconjunto de vocabulario distinto — responsable de diferentes dominios.

4. **Unicidad de identificadores**: 98–100% en los 8 tipos de ilustración.

Notebook: `47_sta_metadata_analysis.ipynb`
Resultados: `resultados/sta_metadata_resultados.json`
