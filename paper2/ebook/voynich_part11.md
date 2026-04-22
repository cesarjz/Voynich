
## 35.17 Matriz de selectividad, léxicos de registro y folios aislados (notebook `48_selectivity_and_registers.ipynb`)

### Matriz de selectividad
La matriz completa onset × coda (164 × 87) tiene 90% de ceros — confirmando que ~90% de combinaciones están prohibidas. El clustering jerárquico revela 8 bloques de onsets. Los tres onsets más productivos (K1, A1, D1.A1) forman un bloque "universal" compartiendo 40 codas. Par O-C más frecuente: [K1]+[K2.A2] (171 ocurrencias).

### Léxicos de registro
- **Vocabulario solo-A**: 2.711 tipos — %F=4.5%, %T2=74.6% (casi todo contenido técnico)
- **Vocabulario solo-B**: 4.958 tipos — %F=25.2%, %T2=59.1% (sustancialmente más funcional)
- **Compartido**: 1.156 tipos
- La sección Herbal tiene el mayor solapamiento inter-registro (Jaccard=0.113); Bio y Pharma tienen CERO solapamiento

### Folios aislados
16 folios forman comunidades singleton (sin vocabulario T2 compartido a Jaccard > 0.05). Los aislados son más técnicos (%F=25.5% vs 42.0%). Muchos son folios zodiacales — vocabulario astrológico tan especializado que no se solapa con otras secciones.

Notebook: `48_selectivity_and_registers.ipynb`
Resultados: `resultados/selectivity_registers_resultados.json`
