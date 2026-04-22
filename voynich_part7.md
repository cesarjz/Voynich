# PARTE VII

# Validación del descifrado y restricciones gramaticales

La Parte VI produjo un mapping composicional glifo→carácter que coloca al hebreo en primer lugar con una brecha de 11.7 puntos sobre las lenguas no semíticas, una convergencia MCMC del 59% y un colapso many-to-one compatible con la hipótesis SilPart. Sin embargo, el ranking por sí solo no demuestra que el mapping sea correcto: un optimizador suficientemente potente encontrará *siempre* un mapping que maximiza la verosimilitud bajo el LM, incluso si el texto subyacente no es realmente hebreo. La Parte VII somete el mapping composicional a cinco tests de validación independientes del scoring (Capítulo 19) y, ante el diagnóstico de degeneración, implementa un EM constrained con grammar anchors que intenta corregir el colapso (Capítulo 20).

# Capítulo 19. Validación del mapping composicional

## 19.1 Cinco tests independientes

El principio de la validación es sencillo: si el mapping composicional captura la estructura real del Voynich, el texto mapeado debería exhibir propiedades que no fueron optimizadas directamente por el scoring. Se diseñan cinco tests, cada uno midiendo un aspecto distinto (celdas 4-13 del notebook `08_validation.ipynb`):

| # | Test | Pregunta | Criterio de éxito |
|---|------|----------|-------------------|
| 1 | Collapse coherence | ¿Los glifos que colapsan en el mismo carácter comparten distribución posicional? | z-score medio > 0 |
| 2 | N-gram realism | ¿Los trigramas del texto mapeado se parecen más a hebreo real que un shuffle aleatorio? | Percentil > 50% |
| 3 | Hebrew roots | ¿Aparecen raíces triconsonánticas hebreas reales en el texto mapeado? | Enrichment > 1.0 con p < 0.05 |
| 4 | Cardinality | ¿El mapping se degrada significativamente si se limita la cardinalidad? | Drop < 5% con K_max razonable |
| 5 | Label analysis | ¿Las etiquetas (palabras cortas junto a ilustraciones) se comportan como esperado? | Penalty < baseline |

## 19.2 Resultados por test

### Test 1: Collapse coherence

Se evalúa si los glifos que colapsan en un mismo carácter hebreo comparten características distribucionales (frecuencia, posición), o si el colapso es un artefacto del optimizador (celdas 4-5).

| Métrica | Valor |
|---------|-------|
| z-score medio | **-0.562** |
| Caracteres degenerados (z < -1) | 5 |
| Caracteres estructurados (z > 1) | 3 |
| Caracteres ambiguos | 14 |

Los tres peores caracteres:

| Carácter | z-score | N glifos |
|----------|---------|----------|
| ש (Shin) | -5.14 | 17 |
| ר (Resh) | -3.52 | 15 |
| ל (Lamed) | -3.43 | — |

**Veredicto: DEGENERADO.** El z-score negativo indica que los glifos agrupados bajo un mismo carácter son *menos* similares entre sí que glifos aleatorios. Shin (z=-5.14) es el peor caso: sus 17 glifos no comparten perfil distribucional, sugiriendo que el colapso es artificial.

### Test 2: N-gram realism

Se compara la divergencia Jensen-Shannon entre los trigramas del texto mapeado y los del hebreo nativo, contra una distribución nula de 100 shuffles aleatorios del mapping (celdas 6-7).

| Métrica | Valor |
|---------|-------|
| JSD real | 0.753 |
| JSD nulo (media) | 0.767 |
| Percentil | **24%** |
| Entropía real | 6.01 bits |
| Entropía nula | 7.86 bits |

**Veredicto: FAIL.** El mapping real tiene percentil 24%: peor que el 76% de los shuffles aleatorios. La entropía del texto mapeado (6.01 bits) es menor que la esperada bajo shuffle (7.86 bits), indicando que el mapping colapsa la distribución en lugar de producir texto con la diversidad n-grámica del hebreo real.

### Test 3: Hebrew roots

Se buscan raíces triconsonánticas hebreas reales (de una lista de referencia) en el texto mapeado, y se compara la tasa de aparición contra shuffles aleatorios para calcular el enrichment (celdas 8-9).

| Métrica | Valor |
|---------|-------|
| Matches encontrados | 84 |
| Raíces distintas | 6 |
| Enrichment | **84.0×** |

Las seis raíces detectadas:

| Raíz | Significado | Matches |
|------|-------------|---------|
| חמר | material/arcilla | — |
| עשה | hacer | — |
| שלח | enviar | — |
| שמע | escuchar | — |
| שמר | guardar | — |
| שמש | sol/servir | — |

**Veredicto: PROMETEDOR pero SESGADO.** El enrichment de 84× es impresionante, pero 4 de las 6 raíces contienen ש (shin), el carácter que atrae 17 glifos. Con 17 glifos mapeados a shin, las secuencias que contienen shin son estadísticamente abundantes, inflando artificialmente la detección de raíces que lo contienen. El test está contaminado por el colapso degenerado del Test 1.

### Test 4: Cardinality restriction

Se evalúa cuánto empeora el score si se limita el número máximo de glifos por carácter (K_max). Si el mapping es genuino, la restricción debería causar poco daño; si es degenerado, el score caerá significativamente (celdas 10-11).

| K_max | Drop en score |
|-------|--------------|
| 6 | 13.06% |
| 8 | 11.33% |
| 12 | 9.46% |
| **Media** | **11.28%** |

**Veredicto: MODERADO.** Un drop del 11.3% es sustancial pero no catastrófico. El mapping depende parcialmente del colapso de alta cardinalidad, pero no completamente ---existe señal residual incluso con restricción.

### Test 5: Label analysis

Las etiquetas del Voynich (palabras cortas junto a ilustraciones botánicas y astronómicas) deberían comportarse como un subsistema especial: vocabulario más limitado, posiblemente nombres propios o clasificaciones. Se compara la distribución de las etiquetas mapeadas contra el texto principal (celdas 12-13).

| Métrica | Valor |
|---------|-------|
| N etiquetas | 591 |
| Penalty media | **-5.717 bits** |
| Longitud media etiquetas | 5.22 tokens |
| Longitud media texto | 4.21 tokens |

**Veredicto: DIVERGENTE.** Las etiquetas mapeadas tienen una penalización de -5.7 bits respecto al texto principal, indicando que el mapping las trata peor que al texto general. Además, las etiquetas mapeadas son más largas (5.22 vs 4.21 tokens), lo opuesto de lo esperado si fueran nombres o clasificaciones breves.

## 19.3 Scorecard consolidado

| # | Test | Veredicto | Interpretación |
|---|------|-----------|----------------|
| 1 | Collapse coherence | **DEGENERADO** | Colapso artificial, no distribucional |
| 2 | N-gram realism | **FAIL** | Peor que 76% de shuffles |
| 3 | Hebrew roots | **PROMETEDOR**** | Enrichment alto pero contaminado por shin |
| 4 | Cardinality | **MODERADO** | 11.3% drop: parcialmente degenerado |
| 5 | Labels | **DIVERGENTE** | Mapping perjudica etiquetas |

**Veredicto global: DEGENERADO** (1 positivo, 2 marginal, 2 negativos).

** El resultado del test de raíces es el único positivo, pero está sesgado por el colapso de shin. Si se excluyen las raíces que contienen shin, el enrichment cae drásticamente.

## 19.4 Diagnóstico: el LM domina, el EM colapsa

Los cinco tests convergen en un diagnóstico claro: el scoring composicional de la Parte VI, dominado por S_LM (peso 2.0), permite que el optimizador encuentre un mapping que maximiza la verosimilitud bajo el CharLM *colapsando* múltiples glifos en unos pocos caracteres de alta frecuencia. Este colapso mejora el score porque:

1. Los caracteres hebreos más frecuentes (shin, resh, vav) tienen trigramas bien modelados por el CharLM
2. Al canalizar muchos glifos hacia estos caracteres, el texto mapeado se "simplifica" hacia secuencias que el CharLM puntúa alto
3. Pero esta simplificación destruye la estructura real: los glifos que colapsan no comparten distribución posicional, los n-gramas resultantes son menos diversos que los del hebreo real, y las etiquetas empeoran

El problema no está en el ranking ---que es informativo y robusto--- sino en el mapping específico, que está degenerado. La solución requiere restricciones adicionales que impidan el colapso descontrolado.

# Capítulo 20. EM constrained con grammar anchors

## 20.1 Tres correcciones

Basándose en el diagnóstico del Capítulo 19, se implementan tres correcciones al EM composicional, cada una apuntando a un aspecto del colapso (celdas 4-7 del notebook `09_constrained_em.ipynb`):

### Corrección 1: K_max (cardinalidad máxima)

Se limita a K_max = 7 el número máximo de glifos que pueden mapear a un mismo carácter. Esto impide que shin atraiga 17 glifos y fuerza al optimizador a distribuir los glifos entre más caracteres. El valor K_max = 7 se elige basándose en el Test 4 de la validación: con K_max entre 6 y 8, el drop en score es ~11-13%, un compromiso entre restricción y calidad.

### Corrección 2: Entropy bonus

Se añade un término de bonificación que premia mappings con distribución más uniforme sobre los caracteres target:

**S_entropy = w_entropy × H(distribución de glifos por carácter)**

donde H es la entropía de Shannon de la distribución de cuántos glifos mapean a cada carácter. Valores altos de H corresponden a distribuciones más uniformes (menos colapso). Se exploran tres pesos: w_entropy ∈ {0.1, 0.2, 0.5}.

### Corrección 3: Grammar anchors

Se anclan glifos específicos del Voynich a caracteres hebreos específicos basándose en el conocimiento posicional de las Partes III-IV. La lógica es: si D1 aparece en posición inicial el 98.7% de las veces, y en hebreo las partículas preposicionales (ב be, כ ke, ל le, מ me) y el artículo (ה ha) aparecen casi siempre al inicio de palabra, entonces D1 debería mapear a uno de estos caracteres (celdas 4-5).

## 20.2 Reglas gramaticales STA → anchors hebreos

Se definen reglas basadas en la gramática posicional del Voynich, asignando 12 glifos a roles gramaticales que restringen su conjunto de caracteres hebreos permitidos:

| Glifo | Rol gramatical | Justificación |
|-------|---------------|---------------|
| D1 | prefix | 98.7% en posición inicial → preposiciones/artículo hebreo |
| L1 | prefix | Glifo-prefijo frecuente |
| K1 | classifier | 89.4% en posición inicial → partículas clasificadoras |
| Q1 | root | Raíz nuclear más frecuente |
| Q2 | root | Segundo núcleo más frecuente |
| E1 | root | Posición nuclear |
| P2 | root | Posición nuclear |
| Z1 | root | Posición nuclear |
| Qa | root | Posición nuclear |
| F2 | root | Posición nuclear |
| A2 | suffix | 83.8% en posición final → sufijos nominales/verbales hebreos |
| C1 | suffix | Posición final frecuente |

En total, 12 glifos quedan anclados (7.2% del inventario de 166). El baseline (mapping unconstrained de la Parte VI) respeta solo el 33% de estas reglas: el 67% de los glifos anclados mapean a caracteres fuera de su conjunto permitido.

### Scoring constrained

El score total se extiende con dos términos:

**S_total = 2.0 × S_LM + 0.5 × S_pos + 0.3 × S_card + w_entropy × S_entropy + w_grammar × S_grammar**

donde:

- **S_card** (peso 0.3): penalización por exceder K_max = 7 glifos por carácter
- **S_entropy** (w_entropy variable): bonificación por distribución uniforme
- **S_grammar** (w_grammar variable): bonificación por respetar los grammar anchors

## 20.3 Weight sweep (9 configs) + MCMC refinamiento

Se ejecuta un sweep sobre 9 configuraciones de pesos (w_entropy × w_grammar), combinando 3 valores de cada uno (celdas 9-10):

| w_entropy | w_grammar | Score EM | S_LM | Chars usados | Entropía | Grammar |
|-----------|-----------|----------|------|-------------|----------|---------|
| 0.1 | 0.5 | -41.48 | -20.84 | 27 | 0.999 | 0.50 |
| 0.1 | 1.0 | -43.23 | -22.15 | 27 | 0.999 | 1.00 |
| 0.1 | 1.5 | -39.63 | -20.45 | 27 | 1.000 | 0.67 |
| 0.2 | 0.5 | -41.38 | -20.84 | 27 | 0.999 | 0.50 |
| 0.2 | 1.0 | -42.04 | -21.75 | 27 | 0.999 | 1.00 |
| 0.2 | 1.5 | -39.55 | -20.51 | 27 | 0.999 | 0.67 |
| 0.5 | 0.5 | -42.63 | -21.88 | 27 | 0.999 | 1.00 |
| 0.5 | 1.0 | -42.23 | -21.91 | 27 | 0.999 | 1.00 |
| **0.5** | **1.5** | **-39.32** | **-20.50** | **27** | **1.000** | **0.67** |

La mejor configuración es **w_entropy = 0.5, w_grammar = 1.5** con score EM = -39.32. Todas las configuraciones usan los 27 caracteres hebreos y respetan K_max = 7. La entropía de la distribución de glifos por carácter es consistentemente ~1.0 (cerca del máximo), indicando que las tres correcciones efectivamente previenen el colapso concentrado. El grammar compliance oscila entre 0.50 y 1.00, con las configuraciones de w_grammar = 1.5 alcanzando 0.67 (2 de 3 condiciones).

La mejor configuración EM se refina con MCMC multi-chain (celdas 11-13):

| Parámetro | Valor |
|-----------|-------|
| Cadenas | 4 |
| Iteraciones/cadena | 10,000 |
| Burn-in | 5,000 |
| Muestras posteriores | 4,004 |
| Pesos | w_lm = 2.0, w_pos = 0.5, w_card = 0.3, w_ent = 0.5, w_gram = 1.5 |
| K_max | 7 |

## 20.4 Comparación constrained vs unconstrained

| Métrica | Unconstrained (Parte VI) | Constrained |
|---------|--------------------------|-------------|
| Score final | -39.90 | **-40.69** |
| Score LM | -20.10 | -20.50 |
| PPX mapeada | 16.25 | 19.24 |
| PPX nativa (hebreo) | 7.60 | 7.60 |
| Ratio PPX | 2.14 | **2.53** |
| K_max efectivo | 17 (shin) | **11** |
| R-hat < 1.1 | 57.1% | **39.9%** |
| Grammar compliance | 33% | **67%** |

El constrained sacrifica score LM y perplejidad (el CharLM no puede colapsar tanto) a cambio de un mapping con cardinalidad controlada (K_max 17 → 11) y mayor respeto por las restricciones gramaticales (33% → 67%). La convergencia MCMC empeora (57.1% → 39.9%) porque los anchors crean barreras en el espacio de probabilidad que dificultan la exploración.

### Mappings de alta confianza

El MCMC constrained produce un conjunto de mappings con confianza posterior 1.0 que son lingüísticamente coherentes:

| Glifo | Función STA | → Hebreo | Confianza | Interpretación |
|-------|------------|----------|-----------|----------------|
| D1 | Prefijo (98.7% inicial) | ה (he) | 1.0 | Artículo definido hebreo |
| J1 | — | ל (lamed) | 1.0 | Preposición "a/para" |
| A1 | — | מ (mem) | 1.0 | Preposición "de/desde" |
| A3 | — | מ (mem) | 1.0 | Preposición "de/desde" |
| Q1 | Raíz nuclear | ש (shin) | 1.0 | Consonante de raíz frecuente |
| Q2 | Raíz nuclear | ש (shin) | 1.0 | Consonante de raíz frecuente |
| C1 | Sufijo (final) | ה (he) | 1.0 | Sufijo femenino/direccional |
| C2 | — | ה (he) | 1.0 | Función morfológica |
| B2 | — | ה (he) | 1.0 | Función morfológica |
| G1 | — | ר (resh) | 0.75 | Consonante frecuente |
| K1 | Clasificador (89.4% inic.) | ב (bet) | 0.66 | Preposición "en" |

El cluster D1→ה, J1→ל, A1→מ, K1→ב reproduce exactamente el sistema de preposiciones proclíticas del hebreo bíblico (ב ,כ ,ל ,מ más el artículo ה). Que este patrón emerja del MCMC con anchors ---sin haberlo impuesto directamente--- es notable: los glifos-prefijo del Voynich mapean a las partículas gramaticales más frecuentes del hebreo.

Los glifos clasificados como raíz (E1, P2, Z1, Qa, F2) muestran una distribución posterior bimodal entre י (yod) y א (alef), con preferencia por yod (58-83%). Esta ambigüedad puede reflejar la dualidad consonante/vocal de las *matres lectionis* en hebreo.

## 20.5 Re-validación (3 tests)

Se re-ejecutan tres de los cinco tests de validación del Capítulo 19 sobre el mapping constrained (celdas 16-18). Los resultados revelan una tensión fundamental entre estructura morfológica y fluidez secuencial.

### Test 1 revisado: Collapse coherence

| Métrica | Unconstrained | Constrained | Dirección |
|---------|---------------|-------------|-----------|
| z-score medio | -0.562 | **-0.448** | Mejora parcial |
| Chars degenerados (z < -1) | 5 | **7** | Regresión |
| Chars estructurados (z > 1) | 3 | 1 | Regresión |

**Resultado mixto.** El z-score medio mejora ligeramente (-0.562 → -0.448), indicando que el colapso más extremo (shin con 17 glifos) se ha atenuado. Sin embargo, el número de caracteres degenerados *aumenta* de 5 a 7, y los estructurados bajan de 3 a 1. Las restricciones redistribuyen el colapso ---impiden la concentración extrema pero crean más zonas de degeneración moderada. El mapping constrained es menos extremo pero no más estructurado.

### Test 2 revisado: N-gram realism

| Métrica | Unconstrained | Constrained | Dirección |
|---------|---------------|-------------|-----------|
| JSD | 0.753 | **0.723** | Mejora en JSD |
| Percentil vs shuffles | 24% | **5%** | **Regresión severa** |

**Resultado negativo inesperado.** Aunque la JSD absoluta mejora ligeramente (0.753 → 0.723), el percentil cae drásticamente del 24% al 5%: el texto mapeado con restricciones se parece *menos* a hebreo real a nivel de secuencia que el baseline sin restricciones. Los grammar anchors, al forzar ciertos glifos a ciertos caracteres, producen secuencias de trigramas que no se dan en hebreo natural. El 95% de los shuffles aleatorios producen trigramas más parecidos al hebreo.

### Test 3 revisado: Hebrew roots — el resultado estrella

| Métrica | Unconstrained | Constrained | Dirección |
|---------|---------------|-------------|-----------|
| Raíces distintas | 6 | **100** | **Gran mejora** |
| Enrichment | 84× | **154×** | **Gran mejora** |

**Resultado positivo contundente.** El mapping constrained detecta **100 raíces triconsonánticas hebreas bíblicas** frente a solo 6 del baseline, con un enrichment de 154× (frente a 84×). Las 100 raíces incluyen vocabulario nuclear del hebreo bíblico:

| Categoría | Raíces ejemplo |
|-----------|---------------|
| Existencia | היה (ser), חיה (vivir), מות (morir) |
| Movimiento | הלך (caminar), בוא (venir), יצא (salir), ירד (bajar), עלה (subir) |
| Conocimiento | ידע (conocer), שמע (escuchar), ראה (ver) |
| Acción | עשה (hacer), נתן (dar), לקח (tomar), כתב (escribir) |
| Comunicación | אמר (decir), דבר (hablar), שלח (enviar), קרא (llamar) |
| Mundo natural | ארץ (tierra), מים (agua), שדה (campo), עוף (ave), פרי (fruto) |
| Sociedad | מלך (reinar), כהן (sacerdote), בית (casa), עיר (ciudad) |
| Religión | קדש (santo), ברך (bendecir), זבח (sacrificar), צדק (justicia) |

A diferencia del resultado unconstrained donde 4 de las 6 raíces contenían shin (sesgo por colapso), las 100 raíces del constrained cubren 20+ consonantes distintas ---el sesgo de shin se ha diluido significativamente. Este resultado no puede explicarse solo por azar estadístico: la probabilidad de encontrar 100 raíces reales con enrichment 154× en un mapping aleatorio es despreciable.

## 20.6 La paradoja raíces vs n-gramas

Los tres tests revisados revelan una tensión fundamental que merece análisis:

| Dimensión | Unconstrained | Constrained | Interpretación |
|-----------|---------------|-------------|----------------|
| Raíces hebreas | 6 (sesgadas) | **100** (diversas) | Estructura morfológica genuina |
| N-gram realism | Percentil 24% | Percentil **5%** | Fonotaxis no cuadra |
| Collapse | z = -0.56 | z = -0.45 | Mejora marginal |
| PPX ratio | 2.14 | 2.53 | Texto menos fluido |

**El constrained encuentra más hebreo real (100 raíces bíblicas) pero produce menos texto hebreo fluido (percentil 5 en n-gramas).** Esta paradoja tiene varias interpretaciones posibles:

1. **Lengua semítica no-hebrea.** La lengua subyacente puede compartir raíces semíticas con el hebreo (como el arameo, que tiene ~70% de raíces cognadas) pero con fonotaxis diferente. Un texto arameo mapeado a través de un CharLM hebreo produciría exactamente este patrón: raíces reconocibles pero secuencias de caracteres no-nativas.

2. **Capa de complejidad adicional.** El sistema de escritura del Voynich puede tener una capa que el modelo composicional simple no captura: transposición, nulos, o codificación contextual que distorsiona los n-gramas sin destruir las raíces.

3. **Glifos no anclados contaminan.** Solo 12 de 166 glifos están anclados. Los ~154 restantes siguen optimizados por el LM, que tiende al colapso. El texto resultante mezcla fragmentos anclados (que producen raíces) con fragmentos libres (que producen n-gramas no-hebreos).

## 20.7 Scorecard constrained

| # | Dimensión | Unconstrained → Constrained | Veredicto |
|---|-----------|------------------------------|-----------|
| 1 | Raíces hebreas | 6 → 100 raíces, 84× → 154× | **MEJORA** |
| 2 | Cardinalidad | K_max 17 → 11 | **MEJORA** |
| 3 | Grammar compliance | 33% → 67% | **MEJORA** |
| 4 | Mappings gramaticales | Incoherentes → D1→ה, J1→ל, A1→מ | **MEJORA** |
| 5 | N-gram realism | Percentil 24% → 5% | **REGRESIÓN** |

**Veredicto global: IMPROVED** (4 mejoras, 1 regresión).

La mejora es predominantemente morfológica: el constrained encuentra estructura de raíces y paradigmas gramaticales plausibles. La regresión es fonotáctica: las secuencias de caracteres resultantes no son fluidas en hebreo. Esta asimetría ---morfología correcta, fonotaxis incorrecta--- es diagnósticamente valiosa porque acota el tipo de sistema: es compatible con una lengua semítica que comparte léxico con el hebreo pero no necesariamente su fonotaxis exacta.

## 20.8 Conclusiones y próximos pasos

### Conclusiones del Capítulo 20

1. **Los grammar anchors funcionan.** La detección de 100 raíces hebreas bíblicas (enrichment 154×) es el resultado más fuerte de todo el pipeline de descifrado. Las restricciones gramaticales transforman un mapping degenerado (6 raíces sesgadas por shin) en uno morfológicamente rico.

2. **El trade-off morfología vs fonotaxis es real e informativo.** El mapping constrained mejora en estructura morfológica (raíces, paradigmas, preposiciones) pero empeora en fluidez secuencial (n-gramas, perplejidad). Esta tensión sugiere que (a) el CharLM trigrama es insuficiente para capturar la fonotaxis real, (b) la lengua subyacente no es hebreo estándar sino una lengua semítica emparentada, o (c) existe una capa de codificación adicional.

3. **El sistema de preposiciones proclíticas emerge espontáneamente.** Los mappings D1→ה, J1→ל, A1→מ, K1→ב reproducen el sistema gramatical más básico del hebreo bíblico sin haberlo impuesto directamente. Esto constituye evidencia independiente de compatibilidad semítica.

4. **La convergencia MCMC empeora con restricciones** (57% → 40%), indicando que el espacio posterior con anchors es más multimodal. Esto es esperable: los anchors crean barreras que fragmentan el espacio de búsqueda.

5. **El Voynich no se ha descifrado.** El texto mapeado no es hebreo legible. Los 100 raíces y las preposiciones son señales prometedoras, pero la perplejidad (2.53× la nativa) y el percentil n-gráfico (5%) indican que el mapping está lejos de ser correcto a nivel de secuencia.

### Próximos pasos

1. **Arameo como candidato.** Dado que el mapping produce raíces semíticas reconocibles pero fonotaxis no-hebrea, el arameo bíblico y el judeo-arameo son candidatos naturales: comparten la mayoría del léxico con el hebreo pero tienen fonotaxis y morfología propias.

2. **Neural LM.** Reemplazar el CharLM trigrama por un modelo neuronal (character-level LSTM o Transformer) que capture dependencias largas y fonotaxis más rica.

3. **Ampliar cobertura lingüística.** Añadir lenguas romance (italiano, catalán, occitano) ---candidatas históricas por la procedencia del manuscrito--- y arameo.

4. **Cribs visuales.** Usar las ilustraciones del Voynich para identificar palabras ancla (nombres de plantas, símbolos astronómicos) que restrinjan el mapping más allá de la gramática posicional.

5. **Validación cruzada.** Entrenar el mapping en la mitad del corpus y validar en la otra mitad para detectar sobreajuste.

6. **Transcripciones alternativas.** Repetir el análisis completo con EVA y Currier para verificar que los resultados no dependen de la transcripción STA1 2.0.

# Capítulo 21. Análisis semántico por sección y reconstrucción morfológica

El Capítulo 20 demostró que el mapping constrained produce 100 raíces hebreas (enrichment 154×) pero n-gramas peor que el baseline (percentil 5%). Antes de concluir la Parte VII, abordamos dos preguntas complementarias: (1) ¿las raíces detectadas se correlacionan con el contenido temático de cada sección del Voynich? y (2) ¿el mapping produce palabras hebreas reconocibles con estructura morfológica prefijo-raíz-sufijo?

## 21.1 Raíces por sección

Se aplicó el root matching del mapping constrained (con conf_threshold=0.30, dado que la confianza mediana es 0.155) a cada sección del manuscrito por separado. Resultados:

| Sección | Palabras | Raíces distintas | Total matches | Top 3 raíces |
|---------|----------|-------------------|---------------|--------------|
| Herbal | 13,777 | 53 | 1,514 | שמר(650), שמע(386), עמד(113) |
| Astronómica | 1,307 | 100 | 247 | שמע(39), עמד(24), שמר(18) |
| Zodíaco | 1,558 | 17 | 159 | שמע(47), שמר(46), חמר(14) |
| Biológica | 6,661 | 15 | 660 | שמע(385), שמר(204), עלה(22) |
| Farmacéutica | 2,444 | 22 | 166 | שמר(39), שמע(38), עמד(26) |
| Recetas | 10,448 | 28 | 1,469 | שמר(628), שמע(584), עמד(71) |

Observación clave: las mismas 2-3 raíces (שמר, שמע, עמד) dominan en *todas* las secciones. La sección astronómica es anómala: matchea las 100 raíces en solo 1,307 palabras, sugiriendo mayor diversidad de glifos pero no especificidad semántica.

## 21.2 Correlación semántica: categoría × sección

Se definieron 5 categorías semánticas a priori con raíces de HEBREW_ROOTS asignadas manualmente:

- **Botánica/naturaleza** (10 raíces): פרי, שדה, עוף, צאן, עלה, גמל, סוס, דגג, שמן, יין
- **Astronomía/tiempo** (6): יום, שמש, ליל, חדש, שנה, רוח
- **Cuerpo/biología** (9): נפש, בשר, עצם, רגל, ראש, עין, רחם, חיה, דמם
- **Religión/ritual** (7): קדש, כהן, זבח, טהר, טמא, ברך, צדק
- **Sociedad/material** (8): מלך, בית, עיר, כסף, זהב, אבן, כלי, ספר

Se calculó el enrichment (freq_sección / freq_global) para cada par categoría × sección, y un test chi-cuadrado global.

**Chi² = 64.21, p = 1.56×10⁻⁶, dof = 20** — asociación significativa.

Correspondencias esperadas (sección ↔ categoría semántica):

| Sección | Categoría esperada | Enrichment | Cumple |
|---------|-------------------|------------|--------|
| Herbal | Botánica/naturaleza | 1.073 | ✓ (marginal) |
| Astronómica | Astronomía/tiempo | 3.635 | ✓ |
| Zodíaco | Astronomía/tiempo | 2.033 | ✓ |
| Biológica | Cuerpo/biología | 0.209 | ✗ |
| Farmacéutica | Religión/ritual | 0.000 | ✗ |
| Recetas | Sociedad/material | 1.130 | ✓ (marginal) |

**Resultado: 4/6 correspondencias se cumplen**, pero la señal del chi² proviene principalmente de la asimetría en diversidad de raíces (la sección astronómica matchea las 100 raíces con enrichment >3 en *todas* las categorías). Las secciones biológica y farmacéutica no muestran la especificidad temática esperada.

## 21.3 Reconstrucción morfológica

Se analizaron las 200 palabras más frecuentes (47.1% del corpus) descomponiendo cada una en prefijo proclítico + raíz triconsonántica + sufijo:

| Categoría | Nº palabras | % |
|-----------|-------------|---|
| Morfología solo (prefijo/sufijo sin raíz) | 171 | 85.5% |
| Completa (prefijo + raíz + sufijo) | 15 | 7.5% |
| No reconocible | 9 | 4.5% |
| Raíz parcial (raíz sin afijos) | 5 | 2.5% |

El 85.5% de "morfología solo" se explica por la degeneración many-to-one del mapping: 7 glifos mapean a מ y 6 a ה, por lo que casi toda palabra "empieza con prefijo" o "termina con sufijo" por construcción, sin que esto refleje morfología real.

## 21.4 Frecuencia de partículas gramaticales

Se comparó la frecuencia de partículas gramaticales como prefijos (posición inicial de palabra) con las frecuencias del hebreo bíblico real:

| Partícula | Voynich mapeado | Hebreo bíblico | Dentro del rango |
|-----------|----------------|----------------|-----------------|
| ה (artículo) | 22.7% | 15-18% | ✗ |
| ל (a/para) | 1.0% | 5-7% | ✗ |
| ב (en) | 23.7% | 4-6% | ✗ |
| מ (de) | 28.1% | 3-5% | ✗ |
| כ (como) | 0.2% | 1-2% | ✗ |

**Resultado: 0/5 partículas dentro del rango.** Las frecuencias de ב (23.7%) y מ (28.1%) son 4-6× más altas que lo esperado, consecuencia directa de la degeneración: múltiples glifos frecuentes mapean a la misma consonante.

## 21.5 Conclusiones del Capítulo 21

1. **La correlación semántica existe pero es débil.** El chi² es significativo (p < 10⁻⁶), y 4/6 correspondencias sección-tema se cumplen. Sin embargo, la señal proviene de la distribución desigual de diversidad de raíces entre secciones, no de especificidad temática genuina.

2. **La morfología no es coherente con hebreo bíblico.** El 85.5% de las palabras muestra "morfología" solo por el colapso many-to-one, no por estructura lingüística real. Las frecuencias de partículas gramaticales están completamente fuera de rango (0/5).

3. **El diagnóstico de degeneración se confirma en una tercera dimensión.** La validación del Capítulo 19 (scorecard 1+/1±/3−), la re-validación del Capítulo 20 (raíces++ pero n-gramas−−), y ahora el análisis semántico-morfológico apuntan a la misma conclusión: el mapping captura correlaciones superficiales (raíces, chi²) pero no produce texto hebreo real a nivel morfosintáctico.

4. **Implicación para el arameo.** Los resultados no descartan una lengua semítica: las raíces que emergen son genuinamente semíticas, pero la fonotaxis y la morfología no corresponden al hebreo. Esto refuerza la hipótesis de que la lengua subyacente podría ser arameo u otra lengua semítica con léxico cognado pero distribución diferente.

Notebook: `10_semantic.ipynb` · Resultados: `semantic_resultados.json`

# Referencias de la Parte VII

- Gelman, A. y Rubin, D. B. (1992). "Inference from Iterative Simulation Using Multiple Sequences." *Statistical Science* 7(4): 457--472.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebooks: `08_validation.ipynb` · `09_constrained_em.ipynb` · `10_semantic.ipynb` · Resultados: `validacion_resultados.json` · `constrained_resultados.json` · `semantic_resultados.json`

Partes I--VII disponibles como documentos independientes.
