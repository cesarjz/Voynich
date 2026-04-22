# PARTE X — Modelos Alternativos y Tests Diagnósticos (Capítulos 28–35)

## 28.1 Motivación: de la homofonía posicional al descifrado

El Capítulo 26 descartó la polifonía posicional (1 glifo → N caracteres según posición) pero confirmó la premisa SilPart: 73% de glifos son position-locked. La lectura correcta de SilPart es la **homofonía posicional** (N glifos → 1 carácter, con selección por posición), análoga a las variantes posicionales del árabe cursivo donde las formas inicial, medial y final de una letra son glifos distintos que codifican el mismo fonema.

**Hipótesis:** Si identificamos glifos que son variantes posicionales del mismo carácter subyacente (alógrafos) y los colapsamos, reduciremos el vocabulario efectivo de ~166 a ~30--50 tipos. El descifrado neural con 1 tabla plana sobre el vocabulario reducido debería mejorar el root matching porque los patrones consonánticos serán más coherentes.

## 28.2 Estrategia de clustering

### Feature vectors por glifo

Para cada glifo con frecuencia ≥ 10, se construyen tres vectores de características:

1. **Perfil de transiciones** (2 × N_glifos dims): fila de M_prob (qué glifos le siguen) concatenada con columna de M_prob (qué glifos le preceden). Captura el contexto secuencial del glifo.

2. **Distribución intra-silábica** (3D): [onset%, nucleus%, coda%]. Captura la posición del glifo dentro de la sílaba.

3. **Distribución posicional en palabra** (3D): [initial%, middle%, final%].

### Criterio de fusión

Dos glifos son candidatos a alógrafos si cumplen tres condiciones:

- **Alta similaridad contextual:** coseno sobre perfiles de transición > 0.6 (aparecen en los mismos contextos secuenciales)
- **Posiciones complementarias:** dominan en posiciones intra-silábicas distintas (uno onset-heavy, otro coda-heavy)
- **Mismo rol C/V:** no fusionar consonante con vocal

### Clustering jerárquico

- Distancia = 1 - coseno sobre perfiles de transición
- Linkage: average (robusto a outliers)
- Sweep de thresholds para cortar el dendrograma
- Selección del threshold que produce ~30--50 tipos efectivos
- Post-filtro: separar clusters con roles C/V mixtos

## 28.3 Resultado del clustering

| Parámetro | Valor |
|-----------|-------|
| Glifos con freq ≥ 10 | ~100 / 166 |
| Threshold óptimo | 0.30 |
| Vocabulario original | 166 |
| Vocabulario reducido | **145** |
| Reducción | 21 glifos (**12.7%**) |
| Clusters multi-glifo | **4** |
| Pares candidatos (sim > 0.6, mismo rol) | 200 |
| Pares complementarios | 65 (32%) |

La reducción es **mínima** (12.7%), muy lejos del target de 30--50 tipos. Solo se forman 4 clusters con más de un miembro:

| Cluster | Representante | Miembros | Posiciones | Rol |
|---------|---------------|----------|------------|-----|
| U2 | U2 | E2, M1, N1, T1, T2, Tb, U2, U3, U4, U5, V1, V2, W1, W2 (14) | 13 onset + 1 nucleus | C |
| F1 | F1 | B4, Cd, F1, F3, G3, H1, X1 (7) | nucleus, onset, coda (mixto) | C |
| D1 | D1 | D1, Da (2) | onset, onset | C |
| Ba | Ba | B5, Ba (2) | onset, onset | C |

### Diagnóstico de los clusters

**Cluster U2 (14 miembros):** Es un mega-cluster de glifos de baja frecuencia (T1, T2, U3, U4, U5, V1, V2, W1, W2) que comparten perfiles de transición por ser infrecuentes y ruidosos, no por ser alógrafos genuinos. Casi todos son onset. No hay complementariedad posicional.

**Cluster F1 (7 miembros):** Mezcla posiciones (nucleus, onset, coda) pero no de forma complementaria --- es un agrupamiento por similaridad contextual genérica.

**Clusters D1 y Ba (2 miembros cada uno):** Ambos agrupan glifos de la misma posición (onset+onset). Son variantes dentro del pool de onset, no pares onset/coda complementarios.

**Ningún cluster muestra la complementariedad posicional esperada** bajo la hipótesis alográfica.

## 28.4 EM multi-seed sobre vocabulario reducido

20 runs (10 seeds × 2 temperaturas: T=2.0, T=3.0) sobre el corpus reescrito con 145 glifos:

| Métrica | Neural v2 (166 gl.) | Allograph (145 gl.) | Δ |
|---------|---------------------|---------------------|---|
| Score medio | -36.34 ± 0.23 | -36.55 ± 0.45 | -0.21 |
| Roots medio | 1.5 ± 1.1 | 1.6 ± 1.2 | +0.1 |
| Roots max | 3 | 4 | +1 |
| K_eff | 25 (todos) | 25--27 | = |
| Grammar = 1.00 | 30/30 | 18/20 | = |

Mejor candidato: T=3.0, seed 0: score=-36.43, K_eff=27, grammar=1.00, roots=4 {חכם, לחם, עבד, שלח}.

Las raíces חכם y לחם comparten las consonantes ח y ל --- el mismo patrón de co-ocurrencia consonántica diagnosticado como artefactual en el Capítulo 25.

## 28.5 MCMC multi-chain

| Métrica MCMC | Neural v2 | Allograph | Δ |
|--------------|-----------|-----------|---|
| Best score | -36.20 | -36.43 | -0.23 |
| K_eff | 25 | 25 | = |
| R-hat < 1.1 | **71.1%** | **54.5%** | -16.6 pp |
| Accept rates | 27--29% | 26--29% | = |

La convergencia empeora significativamente (54.5% vs 71.1%). Con 145 glifos en lugar de 166, el espacio de búsqueda es menor pero la pérdida de distinciones informativas hace que las cadenas MCMC encuentren cuencas de atracción más ambiguas.

## 28.6 Validación: scorecard 4 PASS / 0 MARGINAL / 2 FAIL

| Test | Neural v2 | Allograph | Δ |
|------|-----------|-----------|---|
| 1. Collapse z-score | PASS (-0.94) | PASS (-0.75) | +0.19 |
| 2. N-gram percentile | PASS (68%) | PASS (23%) | **-45 pp** |
| 3. Root matching | FAIL (3 raíces) | FAIL (4 raíces) | +1 |
| 4. Cardinality ratio | PASS (0.93) | PASS (0.93) | = |
| 5. Grammar anchors | PASS (100%) | PASS (100%) | = |
| 6. Coherencia reducción | — | **FAIL** (-45 pp) | nuevo |

**Veredicto: 4 PASS / 0 MARGINAL / 2 FAIL** — peor que neural v2 (4+/0±/1−).

### El n-gram cae drásticamente

68% → 23% (-45 puntos). La reducción destruye información secuencial: al colapsar 14 glifos distintos en U2, se pierden distinciones de transición que el LSTM explotaba para lograr n-gramas realistas. El test 6 (coherencia de la reducción) confirma el FAIL: el delta de -45 puntos percentiles está muy por debajo del umbral de ±5 pp.

### Las raíces no mejoran significativamente

4 raíces vs 3 del neural v2. Las raíces encontradas (חכם, לחם, עבד, שלח) incluyen dos pares que comparten consonantes (חכם/לחם comparten ח,ל) --- el patrón artefactual del Capítulo 25.

## 28.7 Por qué fracasa la hipótesis alográfica

La hipótesis predecía que glifos de posiciones complementarias (onset vs coda) compartirían contextos de transición similares, porque "rodean" las mismas secuencias de caracteres subyacentes. Los datos muestran lo contrario:

| Predicción | Resultado |
|------------|-----------|
| Clusters onset+coda complementarios | **No:** 0 clusters con complementariedad genuina |
| Reducción a 30--50 tipos | **No:** solo 145 tipos (12.7% reducción) |
| N-gram mejora o se mantiene | **No:** cae 45 puntos (-68% → 23%) |
| Roots mejora significativamente | **No:** 4 vs 3 (no significativo) |
| R-hat mejora (menos parámetros) | **No:** empeora (54.5% vs 71.1%) |

La similaridad contextual en el Voynich se organiza **por posición**: glifos de onset se parecen entre sí, glifos de coda se parecen entre sí. Pero glifos de onset y coda **no** se parecen entre sí, aunque la hipótesis alográfica lo predecía. Esto es compatible con un sistema donde cada posición tiene un pool cerrado de glifos con distribuciones de transición internas propias, pero donde los pools de distintas posiciones operan con lógicas distintas.

## 28.8 Tabla comparativa: 9 modelos

| Métrica | Composic. | Constr. | Homof. | Neural v1 | Lexical | Neural v2 | Syl-Heb | Syl-Ara | **Allograph** |
|---------|-----------|---------|--------|-----------|---------|-----------|---------|---------|---------------|
| Vocab | 166 | 166 | 166 | 166 | 166 | 166 | 166 | 166 | **145** |
| N-gram %ile | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% | 23% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | 5 | 4 |
| Collapse z | -0.56 | -0.45 | -0.79 | -0.72 | -0.91 | -0.94 | **-0.20** | -0.35 | -0.75 |
| R-hat < 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** | 90% | 54% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** | 4+/2±/0− | 4+/2±/0− | 4+/0±/2− |

## 28.9 Conclusiones del Capítulo 28

1. **La hipótesis alográfica se descarta como vía de mejora del descifrado.** El clustering basado en contexto + complementariedad posicional produce una reducción mínima (12.7%), sin clusters genuinamente complementarios. El escenario pesimista del plan se ha cumplido.

2. **La similaridad contextual opera dentro de posiciones, no entre ellas.** Los glifos de onset se parecen entre sí, los de coda se parecen entre sí, pero un glifo de onset y uno de coda del supuesto "mismo carácter" no comparten contexto. Esto descarta el modelo de variantes posicionales tipo árabe cursivo.

3. **La reducción destruye información.** Colapsar glifos distintos en un representante pierde distinciones de transición que el LSTM explotaba. El n-gram cae de 68% a 23% (-45 pp), y la convergencia MCMC empeora de 71% a 54%.

4. **El límite de ~3--5 raíces persiste.** Ni la reducción de vocabulario ni el colapso de alógrafos superan la barrera estructural. Con 9 modelos testados, este límite se confirma como una propiedad del espacio de soluciones del Voynich, no de ningún modelo específico.

5. **La estructura posicional del Voynich es más profunda que la alografía.** Los pools posicionales (onset, nucleus, coda) no son variantes de un mismo alfabeto --- son subsistemas con distribuciones de transición propias. La posición no solo selecciona qué glifo se usa (como predice SilPart), sino que define contextos de transición distintos, lo que sugiere que la estructura posicional es un componente integral del mecanismo de codificación, no una capa superficial de variación gráfica.

Notebook: `17_allograph.ipynb` · Resultados: `allograph_resultados.json`

# Capítulo 29. Cifrado homofónico silábico: glifo → sílaba hebrea

## 29.1 Motivación: ¿son los glifos unidades silábicas?

Los nueve modelos anteriores comparten un supuesto: cada glifo Voynich codifica un único **carácter** hebreo. El Capítulo 29 prueba una hipótesis fundamentalmente distinta: cada glifo codifica una **sílaba hebrea completa** (2--3 caracteres), y múltiples glifos pueden representar la misma sílaba (cifrado homofónico).

Tres observaciones motivan esta hipótesis:

1. **Tamaño del inventario.** 166 glifos es excesivo para un alfabeto (~27 caracteres hebreos) pero razonable para un silabario con variantes homofónicas. Silabarios históricos operan en rangos de 50--200 signos (cuneiforme ~600, lineal B ~87, katakana ~48).

2. **MI no amplifica.** La información mutua glifo→sílaba es 0.92× (Capítulo 5), consistente con que los glifos ya son unidades silábicas: si el glifo codificara un solo carácter, la MI debería amplificarse al agrupar caracteres en sílabas.

3. **Posición y homofonía.** El 73% de glifos está position-locked (Capítulo 26). La posición podría determinar qué variante homofónica se usa para la misma sílaba, explicando la distribución posicional sin asumir polivalencia.

## 29.2 Inventario silábico hebreo

Se construye un inventario de sílabas hebreas a partir del corpus Torah usando el mismo método de Transition Probability (TP) del bayesiano (Capítulo 5):

1. Calcular probabilidades de transición de bigramas dentro de palabras hebreas
2. Segmentar en percentil P20 (mínimos locales de TP): threshold = 0.033
3. Filtrar sílabas con frecuencia ≥ 5

| Métrica | Valor |
|---------|-------|
| Sílabas distintas | 1,811 |
| Longitud media | 3.3 chars |
| Distribución longitud | 1: 27, 2: 199, 3: 662, 4: 600, 5: 254, 6: 62, 7: 7 |
| Posición | free: 1,062, coda: 431, onset: 272, nuclear: 46 |
| Roles C/V | C: 1,219 (67%), V: 592 (33%) |

El inventario es considerablemente mayor que los 27 caracteres hebreos. La ratio glifos/sílabas = 166/1811 = 0.09, lo que implica una capacidad homofónica teórica de ~11 glifos por sílaba si se distribuyeran uniformemente.

## 29.3 Diseño: SyllableGlyphMappingState

La clase `SyllableGlyphMappingState` adapta el framework de neural_v2 con una diferencia clave: `apply_word` concatena los caracteres de las sílabas asignadas, produciendo secuencias de longitud variable.

```
Glifo G1 → sílaba (ב,ר)  = "bar"
Glifo G2 → sílaba (א)    = "a"
Glifo G3 → sílaba (כ,ל)  = "kl"
Palabra [G1, G2, G3] → "barakl" (6 chars de 3 glifos)
```

El LSTM de neural_v2 se reutiliza sin modificaciones: puntúa la secuencia concatenada de caracteres, independientemente de cómo se generó. Esto permite comparación directa.

Las funciones de scoring se adaptan:
- **Positional:** match C/V del glifo con C/V de la sílaba (basado en primer carácter)
- **Grammar anchors:** verifica que el primer carácter de la sílaba asignada pertenezca al anchor set del glifo
- **Cardinality:** cuenta sílabas distintas usadas (no chars), K_max = |inventario|/2
- **Root matching:** busca raíces 3-consonánticas en la secuencia concatenada de chars

## 29.4 EM multi-seed

Se ejecutan 10 seeds con parámetros ajustados para las secuencias más largas:

| Parámetro | Valor | vs neural_v2 |
|-----------|-------|-------------|
| Seeds | 10 (5 freq + 5 random) | 20 |
| SAMPLE_EM | 1,500 | 3,000 |
| PROPOSALS/iter | 100 | 200 |
| EM_ITERS | 1,500 | 2,000 |
| T | 3.0 | 3.0 |

Resultados (celda 9):

| Seed | Score | K_eff | Grammar | Roots | Iter | Tiempo |
|------|-------|-------|---------|-------|------|--------|
| 0 | -163,894 | 166 | 1.000 | 1 | 1,236 | 203s |
| 1 | -163,904 | 166 | 0.667 | 1 | 736 | 132s |
| 2 | -163,896 | 166 | 0.667 | 2 | 757 | 125s |
| 3 | -163,901 | 166 | 0.500 | 2 | 898 | 156s |
| 4 | -163,897 | 166 | 0.667 | **5** | 1,500 | 252s |
| 5 | -163,890 | 166 | 0.500 | 2 | 923 | 150s |
| 6 | -163,894 | 166 | 1.000 | 1 | 1,351 | 229s |
| 7 | -163,893 | 166 | 0.500 | 2 | 1,500 | 250s |
| 8 | -163,894 | 166 | 0.500 | 2 | 1,500 | 244s |
| 9 | -163,893 | 166 | 0.500 | 2 | 724 | 121s |

**Observación crítica: K_eff = 166 en las 10 seeds.** El optimizador asigna una sílaba distinta a cada glifo, sin colapso homofónico alguno. Esto ocurre a pesar de tener 1,811 sílabas disponibles.

Los scores (~-163,900) son órdenes de magnitud peores que neural_v2 (~-36), lo cual es esperado: las secuencias decodificadas son ~2.5× más largas, acumulando más penalización del LM.

Mejor candidato: seed 4 (5 roots: בשר, דבר, שמן, שמע, שמש).

## 29.5 MCMC y posterior

4 cadenas, 20K iteraciones, burn-in 5K, thin 10:

| Métrica | Valor |
|---------|-------|
| Best score | -163,886 |
| K_eff | 166 |
| Accept rates | 74%, 75%, 74%, 75% |
| R-hat < 1.1 | 82.0% |

Las tasas de aceptación son altas (~75%) porque con 1,811 candidatos por propuesta, muchos cambios producen sílabas de score similar. La convergencia R-hat (82%) es buena, indicando que las cadenas exploran el mismo atractivo local.

## 29.6 Validación: 6 tests

Se añade un test específico del modelo silábico (test 6: ratio de longitud de palabras).

| Test | Valor | Veredicto |
|------|-------|-----------|
| 1. Collapse z-score | 0.00 | **PASS** |
| 2. N-gram percentile | 22.0% | **PASS** |
| 3. Root matching | 1 raíz | **FAIL** |
| 4. Cardinality ratio | 0.092 | **FAIL** |
| 5. Grammar anchors | 83% | **PASS** |
| 6. Word length ratio | z = 1.11 | **MARGINAL** |

**Scorecard: 3 PASS / 1 MARGINAL / 2 FAIL**

### Análisis de cada test

**Test 1 (PASS):** El z-score de colapso es exactamente 0.0 porque no hay colapso: cada glifo tiene su propia sílaba, así que no hay grupos de glifos para evaluar coherencia interna.

**Test 2 (PASS, pero espurio):** El n-gram del 22% parece aceptable, pero es un artefacto. Inspección de las sílabas asignadas revela que el optimizador selecciona preferentemente sílabas de 1--2 caracteres, evitando las de 3--7 chars. Esto produce secuencias de longitud media 5.16 chars (en vez de los ~8--12 esperados si las sílabas fueran genuinas), y el LSTM puede puntuar estas secuencias "pseudo-char" con score razonable. En esencia, el modelo reimplementa un cifrado char-level disfrazado.

**Test 3 (FAIL):** Solo 1 raíz validada post-MCMC, peor que todos los modelos char-level competitivos (3--5 raíces).

**Test 4 (FAIL):** Cardinality ratio = 9.2%. Se usan 166 de 1,811 sílabas posibles, confirmando que el inventario silábico es innecesariamente grande para este mapping.

**Test 5 (PASS):** Grammar anchors al 83%, indicando que el primer carácter de las sílabas asignadas respeta los roles gramaticales. Pero esto es trivial: las sílabas cortas seleccionadas se comportan como caracteres individuales.

**Test 6 (MARGINAL):** Las palabras decodificadas tienen media 5.16 chars vs 3.81 de la Torah (z = 1.11, dentro de ±2σ pero fuera de ±1σ). Si los glifos fueran genuinamente silábicos, las palabras de 4 glifos producirían ~8--12 chars, muy por encima de la media Torah. El optimizador mitiga esto eligiendo sílabas cortas, pero el exceso residual (1.35 chars) delata la tensión entre hipótesis silábica y realismo.

## 29.7 El resultado clave: fan-out = 0

El dato más revelador del experimento es el fan-out homofónico:

| Métrica | Valor |
|---------|-------|
| Fan-out medio | 1.0 glifos/sílaba |
| Fan-out máximo | 1 |
| Sílabas con múltiples glifos | 0 |
| Sílabas únicas usadas | 166 |

El optimizador, con libertad total para asignar múltiples glifos a la misma sílaba, elige **nunca** hacerlo. Cada glifo recibe su propia sílaba distinta. Esto refuta la hipótesis homofónica desde la raíz: si el manuscrito usara variantes homofónicas para las mismas sílabas, el mapping óptimo debería colapsar glifos similares a la misma sílaba, reduciendo K_eff muy por debajo de 166.

La ausencia total de homofonía, combinada con la preferencia por sílabas cortas, indica que el framework silábico no aporta nada que el char-level no proporcione mejor: el LSTM penaliza las secuencias largas y el optimizador responde eligiendo "sílabas" que son efectivamente caracteres individuales.

## 29.8 Tabla comparativa: 10 modelos

| Métrica | Composic. | Constr. | Homof. | Neural v1 | Lexical | Neural v2 | Syl-Heb | Syl-Ara | Allograph | **Syl-Homo** |
|---------|-----------|---------|--------|-----------|---------|-----------|---------|---------|-----------|-------------|
| Vocab/K_eff | ~10 | — | — | 26 | 1.0 | 25 | 27 | 27 | 25 | **166 syls** |
| N-gram %ile | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% | 23% | 22% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | 5 | 4 | 1 |
| R-hat < 1.1 | 59% | 40% | 68% | 70% | 67% | 71% | **92%** | 90% | 55% | 82% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** | 4+/2±/0− | 4+/2±/0− | 4+/0±/2− | 3+/1±/2− |

## 29.9 Conclusiones del Capítulo 29

1. **La hipótesis silábica homofónica se descarta.** El optimizador no produce homofonía (fan-out = 0) ni colapso silábico (K_eff = 166), y el scorecard (3+/1±/2−) es inferior a todos los modelos char-level competitivos.

2. **166 glifos no forman un silabario.** Son demasiados para un silabario eficiente (que colapsaría a ~80--100 sílabas distintas) y cubren solo el 9% del inventario silábico hebreo. El tamaño del inventario de glifos es compatible con un alfabeto con variantes posicionales (como ya sugiere SilPart), no con un silabario.

3. **El LSTM fuerza la parsimonia.** Ante la opción de usar sílabas largas (genuinamente silábicas) o cortas (pseudo-caracteres), el LSTM penaliza las secuencias largas y el optimizador converge hacia sílabas de 1--2 chars. Esto confirma que el modelo char-level es la representación más parsimoniosa para el Voynich.

4. **Con 10 modelos testados, el límite de ~3--5 raíces y el techo del n-gram siguen intactos.** Neural v2 (68% n-gram, 3 raíces) permanece como el mejor resultado global. Ningún cambio de hipótesis (char-level, syllabic, allographic, homophonic) altera estos límites, confirmando que son propiedades del espacio de soluciones del Voynich, no de los modelos de descifrado.

Notebook: `18_syllabic_homophonic.ipynb` · Resultados: `syllabic_homophonic_resultados.json`

# Capítulo 30. Registros hebreos alternativos: Torah vs Mishnah vs Zohar

## 30.1 Motivación: el registro equivocado

Los Capítulos 23--29 usan hebreo bíblico (Torah) como corpus target exclusivo. Sin embargo, si el autor del Voynich fuera un médico o cabalista judío del norte de Italia (siglo XV) — perfil históricamente plausible —, su escritura seguiría un registro distinto del bíblico:

- **Hebreo mishnaico (halájico):** lengua de la literatura rabínica, con vocabulario técnico-legal ausente en la Torah (contratos, pureza ritual, litigios). Corpus: Mishnah ed. Vilna 1913, 186,577 palabras en 63 tratados.
- **Arameo zohárico (cabalístico):** lengua del Zohar, el texto central de la Cábala, con vocabulario esotérico y estructura sintáctica distinta del arameo bíblico. Corpus: Sulam ed. Jerusalem 1945, 768,375 palabras.

El techo de 68% n-gram y 3--5 raíces (neural v2) podría ser artefacto de entrenar el LM contra el registro equivocado. Este capítulo testea los 3 registros con el mismo pipeline neural v2 (LSTM + EM multi-seed + MCMC).

## 30.2 Diseño experimental

Se descargan los 3 corpora desde Sefaria-Export (GitHub), se subsamplean a N=37,087 palabras (tamaño del corpus Voynich) con semilla fija, y se entrenan 3 LSTMs idénticos (2 capas, embed=32, hidden=192, dropout=0.2, 30 epochs). Hiperparámetros del descifrado: 10 seeds EM, T=3.0, 1500 iteraciones, 100 propuestas/iter, seguido de MCMC (4 cadenas, 20K iteraciones, burn-in 5K).

Nota: estos hiperparámetros son reducidos respecto a neural v2 (20 seeds, 2000 iter, 200 propuestas, 3000 sample) para hacer factible el triple de experimentos. La comparación interna entre registros es justa (todos con idénticas condiciones), pero los valores absolutos no son directamente comparables con neural v2.

Notebook: `19_registers.ipynb`

## 30.3 Estadísticas de corpora y LMs

| Corpus | Full size | Muestra | Vocab | Mean WL | Val loss LM |
|--------|-----------|---------|-------|---------|-------------|
| Torah | 80,051 | 37,087 | 27 | 3.81 | 2.003 |
| Mishnah | 186,577 | 37,087 | 27 | 4.10 | 2.106 |
| Zohar | 768,375 | 37,087 | 27 | 4.21 | 2.119 |

Los 3 corpora comparten las mismas 27 letras hebreas. Mishnah y Zohar tienen palabras más largas en promedio (4.10 y 4.21 vs 3.81), reflejando mayor uso de formas analíticas y compuestos. El val loss de Torah es ligeramente menor (2.003 vs 2.11--2.12), posiblemente porque la Torah es más formulaica y predecible que los textos rabínicos/zoháricos.

## 30.4 Resultados del EM multi-seed

| Registro | Score (mean±std) | Roots (mean) | Roots max | Best seed |
|----------|-----------------|-------------|-----------|-----------|
| Torah | -36.91 ± 0.29 | 2.0 | 4 | seed 8 |
| Mishnah | -36.80 ± 0.33 | 1.0 | 3 | seed 3 |
| Zohar | -36.00 ± 0.27 | 0.3 | 1 | seed 3 |

Zohar obtiene el mejor score bruto (-36.00), pero el menor número de raíces (0.3 de media; 7 de 10 seeds encuentran 0 raíces). Esto refleja que el LM de Zohar es más permisivo (mayor entropía del arameo) pero produce mappings sin contenido léxico reconocible. Torah domina en raíces (2.0 de media, max 4).

## 30.5 Validación: scorecards comparativos

| Test | Torah | Mishnah | Zohar |
|------|-------|---------|-------|
| 1. Collapse z-score | -1.75 (FAIL) | -1.47 (MARGINAL) | -1.38 (MARGINAL) |
| 2. N-gram percentile | 1% (FAIL) | 6% (MARGINAL) | 0% (FAIL) |
| 3. Root matching | 4 (FAIL) | 3 (FAIL) | 1 (FAIL) |
| 4. Cardinality ratio | 0.93 (PASS) | 1.00 (PASS) | 0.96 (PASS) |
| 5. Grammar anchors | 87% (PASS) | 96% (PASS) | 94% (PASS) |
| **Scorecard** | **2+/0±/3−** | **2+/2±/1−** | **2+/1±/2−** |

Los 3 registros producen scorecards muy similares. Mishnah es marginalmente el mejor (2+/2±/1− vs 2+/0±/3− de Torah), con n-gram 6% (MARGINAL vs FAIL) y collapse z-score ligeramente mejor (-1.47 vs -1.75). Sin embargo, el rango absoluto 0--6% n-gram está muy por debajo del 68% de neural v2 con pipeline completo.

Bootstrap CI del n-gram percentile: Torah 1.0% [0, 4], Mishnah 8.1% [2, 16], Zohar 0.0% [0, 0]. La diferencia Mishnah-Torah (~7 pp) es marginalmente significativa, pero irrelevante en términos absolutos.

## 30.6 Cross-scoring: transferibilidad de mappings

Se evalúa cada mapping optimizado para un registro con el LM de los otros dos registros:

| Mapping \ LM | Torah | Mishnah | Zohar |
|--------------|-------|---------|-------|
| Torah | **-36.56** | -38.53 | -39.18 |
| Mishnah | -39.27 | **-36.54** | -39.02 |
| Zohar | -39.50 | -39.29 | **-35.83** |

La diagonal siempre gana con ~3 puntos de ventaja. Los mappings son **completamente específicos** a su propio LM y no son transferibles. Esto indica que el optimizador se adapta a las idiosincrasias estadísticas de cada modelo de lenguaje, no a estructura lingüística real subyacente. Un mapping que «funciona» para Torah es inútil para Mishnah y viceversa.

## 30.7 Conclusiones del experimento de registros

1. **La hipótesis del registro alternativo se descarta.** Los 3 registros (bíblico, mishnaico, zohárico) producen resultados igualmente pobres con el mismo pipeline. Mishnah muestra una ventaja marginal en n-gram (6% vs 1%) que desaparece en términos absolutos. Ningún registro rompe el techo de ~3--5 raíces.

2. **El cross-scoring revela que los mappings son artefactos del LM.** La caída de ~3 puntos fuera de la diagonal confirma que cada mapping se especializa en las frecuencias de caracteres de su propio corpus, sin capturar estructura lingüística transferible.

3. **El Zohar es el peor candidato.** A pesar de obtener el mejor score bruto (su LM es más permisivo), produce el menor número de raíces (0.3 media) y el peor n-gram (0%). El arameo zohárico no es un target viable.

4. **Confirmación de la categoría «semítico noroccidental».** Este resultado refuerza la conclusión del Capítulo 27 (arameo Targum): dentro de la familia semítica noroccidental, el registro específico no importa. El límite es estructural del Voynich, no del corpus target.

5. **Caveat metodológico.** El pipeline reducido (10 seeds, 1500 iter, 100 propuestas) no reproduce el baseline de 68% de Torah neural v2 (obtiene solo 1%). La comparación relativa es justa, pero no podemos excluir al 100% que un pipeline completo con Mishnah produzca resultados cualitativamente distintos. Sin embargo, la diferencia relativa tan pequeña (6 pp) hace esto altamente improbable.

Notebook: `19_registers.ipynb` · Resultados: `registers_resultados.json`

# Capítulo 31. Sílaba-a-sílaba (Modelo 12)

## 31.1 Motivación: la paradoja de la longitud de palabra

Si la unidad de mapping correcta es el glifo individual (como asume Neural v2), un glifo = un carácter hebreo. Pero las palabras Voynich tienen una media de 4.24 glifos, y el 7% tienen ≥7 glifos. Esto implicaría palabras hebreas de 7+ caracteres, lo cual es anómalo: la media hebrea es 3.81 caracteres. Si en cambio la unidad es la **sílaba Voynich** (media 2.58 glifos), una palabra de 10 glifos tendría ~4 sílabas, y mapeando cada sílaba a una sílaba hebrea se producirían ~4 sílabas hebreas (~4 caracteres). Esto resuelve la paradoja de longitud.

## 31.2 Diseño

La segmentación TP-P20 produce 2,923 tipos de sílabas Voynich (792 con frecuencia ≥5) y 3,829 tipos de sílabas hebreas (1,168 funcionales), dando un ratio |Σ|/|A| = 0.68 — el más favorable de todos los modelos. Cada sílaba Voynich mapea a una sílaba hebrea; las sílabas decodificadas se concatenan a secuencias de caracteres y se evalúan con el LSTM.

Pipeline: 20 seeds (10 × 2 temperaturas T=2.0, T=3.0), 1,500 iteraciones EM con 200 propuestas/iteración, patience 80. MCMC: 4 cadenas, 15,000 iteraciones, burn-in 3,000, thin 5.

## 31.3 Resultados

| Métrica | Valor | Veredicto |
|---------|-------|-----------|
| Collapse z | +0.12 | PASS |
| N-gram percentil | **0.1%** | **FAIL** |
| Raíces | 25† | MARGINAL |
| K_eff / cardinalidad | 217/1,168 (18.6%) | FAIL |
| Longitud de palabra | z = 0.85 | PASS |
| R-hat < 1.1 | 4.0% | — |
| Accept rate | 96.5% | — |
| **Scorecard** | **2+/1±/2−** | |

†Las 25 raíces son espurias: las palabras decodificadas promedian solo 2.42 caracteres, con lo que las raíces de 3 consonantes se encuentran trivialmente.

## 31.4 Diagnóstico

El n-gram 0.1% (peor que el azar) y el acceptance rate de 96.5% revelan un **paisaje de energía plano**: el optimizador acepta prácticamente cualquier propuesta, lo que significa que el espacio de soluciones (792 → 1,168) es demasiado grande para que la señal del LM guíe la búsqueda. El K_eff = 217/1,168 confirma que solo el 18.6% del inventario hebreo se utiliza, y la convergencia (R-hat 4%) es la peor de todos los modelos.

El ratio |Σ|/|A| = 0.68, superficialmente favorable, es engañoso: con 792 tipos de entrada, el número total de mappings posibles es 1,168^792 ≈ 10^2,433 — un espacio combinatorio astronómicamente mayor que los 27^166 ≈ 10^237 del mapping glifo-a-carácter.

## 31.5 Conclusión

Ni el mapping glifo-a-carácter ni el mapping sílaba-a-sílaba producen texto hebreo legible. El modelo sílaba-a-sílaba es significativamente peor que todos los modelos char-level. **Hipótesis descartada.**

Notebook: `20_syllable_to_syllable.ipynb` · Resultados: `syl2syl_resultados.json`

# Capítulo 32. Nucleus-Only (Modelo 13)

## 32.1 Motivación: glifos estructurales vs. glifos de contenido

El Capítulo 26 estableció que el 73% de los glifos están position-locked, y la paradoja SilPart (§34.3 del balance) indica que la posición afecta la selección de glifo, no su significado. Llevando esta idea al extremo: ¿qué ocurre si los glifos de onset y coda no son variantes del mismo alfabeto, sino **marcadores estructurales** que no codifican contenido fonético? En este caso, solo los glifos de nucleus serían portadores de información.

Esta hipótesis resuelve la paradoja de longitud de palabra: una palabra de 10 glifos con ~4 glifos de nucleus → 4 caracteres hebreos (razonable). Además, reduce el |Σ|/|A| efectivo de 6.1 a un rango potencialmente resoluble.

## 32.2 Diseño

La clasificación posicional TP-P20 identifica:

| Posición | Tipos | Rol |
|----------|------:|-----|
| Onset (dominant) | 42 | NULL (estructural) |
| Coda (dominant) | 5 | NULL (estructural) |
| Nucleus (dominant) | 28 | Contenido |
| Mixtos (content vocab) | 120 | Contenido |
| **Total structural** | **47** | — |

Todos los glifos clasificados como onset o coda puros se tratan como NULL. Los 120 glifos restantes (incluyendo 28 puramente nucleares y 92 con presencia parcial en nucleus) mapean a los 27 caracteres hebreos. |Σ|/|A| = 120/27 = 4.44.

La extracción de contenido funciona así: para cada sílaba de 3+ glifos, se elimina el primer glifo (onset) y el último (coda), conservando los glifos intermedios (nucleus). Las sílabas de 1 glifo se conservan íntegras. Las sílabas de 2 glifos (onset+coda, sin nucleus) no contribuyen contenido; si una palabra completa queda vacía, se usa la palabra original como fallback (11.8% de palabras).

Pipeline: 20 seeds (10 × 2T), 1,500 iteraciones EM, 4 cadenas MCMC. LSTM idéntico a modelos anteriores.

## 32.3 Resultados

| Métrica | Valor | Veredicto |
|---------|-------|-----------|
| Collapse z | −0.41 | PASS |
| N-gram percentil | **100%** | **PASS** (récord absoluto) |
| Raíces | 2 (אכל, הלך) | FAIL |
| K_eff / cardinalidad | 27/27 (100%) | PASS |
| Longitud de palabra | z = 1.31 (decodificada 2.22 vs. hebrea 3.81) | PASS |
| R-hat < 1.1 | **95.8%** | (mejor convergencia de los 13 modelos) |
| **Scorecard** | **4+/0±/1−** | |

Scores: EM best −24.35, MCMC best −24.42 (mucho mejor que los ~−36 de modelos char-level). Val loss LSTM: 2.009.

## 32.4 Análisis crítico

El n-gram 100% es el mejor resultado de todos los modelos, pero **es un artefacto de la longitud**. La media de contenido nuclear es 2.22 glifos/palabra, lo que produce palabras hebreas de ~2 caracteres. Con solo 2 caracteres, prácticamente cualquier bigrama consonántico aparece en el corpus de referencia. La prueba n-gram no discrimina a esta longitud.

El R-hat 95.8% (mejor convergencia) confirma que el espacio de soluciones es mucho más manejable con 120→27 que con 166→27, y las 4 cadenas MCMC convergen en mappings consistentes. Sin embargo, las 2 raíces (אכל "comer", הלך "caminar") son el mínimo de todos los modelos — confirmando que el techo de raíces no se rompe ni siquiera con las mejores condiciones estadísticas.

## 32.5 Conclusión

El Modelo 13 demuestra que reducir el vocabulario de entrada mejora todas las métricas estadísticas (convergencia, cardinalidad, n-gram), pero las palabras decodificadas son demasiado cortas para producir texto legible. La hipótesis de que onset/coda son puramente estructurales es **excesivamente agresiva**: elimina demasiada información. El resultado motiva directamente el Modelo 14 (§33).

Notebook: `21_nucleus_only.ipynb` · Resultados: `nucleus_resultados.json`

# Capítulo 33. Partial NULL (Modelo 14)

## 33.1 Motivación: threshold parametrizado

Los Modelos 7 (neural v2, full mapping) y 13 (nucleus-only) representan dos extremos de un espectro:

| Modelo | Glifos/palabra | Chars decodificados | N-gram | Problema |
|--------|:--------------:|:-------------------:|-------:|----------|
| Neural v2 | 4.24 | ~4.24 | 68% | |Σ|/|A| = 6.1 |
| Nucleus-only | 2.22 | ~2.22 | 100%* | Bigramas triviales |
| **Sweet spot** | — | **~3.5–4.0** | ? | — |

No todos los glifos de onset/coda son igual de "estructurales". Algunos aparecen en su posición dominante el 100% del tiempo (puramente estructurales), otros solo el 60-70% (parcialmente informativos). Definimos un **umbral de position-locking θ**: un glifo se trata como NULL si su fracción en la posición dominante (onset o coda) es ≥ θ.

- θ → 0.5 (agresivo): se eliminan más glifos → palabras cortas (≈nucleus-only)
- θ → 1.0 (conservador): se eliminan pocos glifos → palabras largas (≈full mapping)

## 33.2 Diseño del barrido

Se evalúan 7 valores de θ ∈ {0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00}. Para cada θ:

1. Clasificar glifos: NULL si (posición dominante ∈ {onset, coda}) AND (fracción dominante ≥ θ)
2. Extraer palabras de contenido (eliminar glifos NULL, fallback a palabra completa si queda vacía)
3. Ejecutar 10 seeds × T=2.0, EM 1,500 iter, 200 propuestas/iter
4. Seleccionar el mejor θ entre aquellos con longitud media decodificada ≥ 3.0
5. Ejecutar MCMC (4 cadenas, 15K iter) sobre el θ seleccionado
6. Scorecard de 5 tests

## 33.3 Resultados del barrido

| θ | NULL glyphs | Content vocab | Mean len | |Σ|/|A| | Best score | K_eff |
|---|------------|--------------|----------|--------|-----------|-------|
| 0.50 | 47 | 157 | 2.69 | 5.81 | -26.78 | 27 |
| 0.60 | 43 | 158 | 2.76 | 5.85 | -27.00 | 27 |
| **0.70** | **38** | **155** | **3.06** | **5.74** | **-28.22** | **27** |
| 0.80 | 24 | 146 | 3.83 | 5.41 | -31.06 | 27 |
| 0.90 | 15 | 152 | 3.93 | 5.63 | -31.70 | 27 |
| 0.95 | 9 | 158 | 4.09 | 5.85 | -31.85 | 27 |
| 1.00 | 7 | 159 | 4.24 | 5.89 | -33.42 | 27 |

Se selecciona **θ=0.70** (longitud media ≥ 3.0): compromiso entre eliminar glifos estructurales (38 NULL) y mantener contenido suficiente.

## 33.4 Scorecard del mejor θ (θ=0.70)

| Test | Valor | Veredicto |
|------|-------|-----------|
| Collapse z-score | -0.15 | PASS |
| N-gram percentile | 100.0% | PASS |
| Root matching | 1 (חיה) | FAIL |
| Cardinality ratio | 1.00 | PASS |
| Word length z | 0.62 | PASS |

R-hat < 1.1: **94.8%**. Scorecard: **4+/0±/1−**.

## 33.5 Conclusión

Partial NULL confirma el patrón de nucleus-only (Capítulo 32): eliminar glifos posicionales mejora métricas estadísticas (100% n-gram, 94.8% R-hat) pero no rompe la barrera de raíces (1 root). El θ parametrizado revela un trade-off continuo, pero **ningún punto produce más de 1 raíz**. El score mejora con θ más agresivo, pero refleja la trivialidad de palabras cortas, no descifrado genuino.

Notebook: `22_partial_null.ipynb` · Resultados: `partial_null_resultados.json`

# Capítulo 34. Robustez transcripcional y Neural v2 sobre EVA

## 34.1 Motivación

Todos los resultados del proyecto reposan sobre la transcripción STA1 2.0 (Stolfi), que asigna 166 tipos de glifos usando códigos de 2 caracteres. La transcripción alternativa más utilizada, EVA (Zandbergen-Landini), colapsa variantes alográficas en ~34 tipos con códigos de 1 carácter (más multi-char como `ch`, `sh`, `cth`, `ckh`). Dos preguntas clave:

1. **¿Son los hallazgos estadísticos robustos bajo EVA?**
2. **¿El ratio |Σ|/|A| favorable de EVA (1.26 vs 6.15) permite mejores resultados de descifrado?**

## 34.2 Fingerprint comparado (notebook `23_transcription_robustness.ipynb`)

Se replica el fingerprint estadístico completo sobre ambas transcripciones:

| Métrica | STA1 2.0 | EVA | Criterio | ¿Ambos pasan? |
|---------|----------|-----|----------|---------------|
| Words | 37,087 | 34,725 | — | — |
| Types | 166 | 34 | — | — |
| **Bounce** | **0.813** | 0.309 | > 0.8 | **NO** |
| MI_pos | 0.658 | 0.670 | > 0.5 | SÍ |
| MI_big | 1.681 | 1.839 | — | — |
| Spectral gap | 0.541 | 0.527 | — | — |
| Inter-folio r | 0.9996 | 0.9995 | > 0.99 | SÍ |

**Resultado:** MI_pos, spectral gap e inter-folio son robustos bajo ambas transcripciones. El bounce (curva en U) se atenúa severamente en EVA (0.309 vs 0.813). El mecanismo es el siguiente: los 166 tipos de glifos de STA1 codifican información posicional directamente en la identidad del glifo — las variantes de onset y coda del "mismo" glifo son tipos distintos, por lo que H₁ (entropía de unigramas) ya captura la estructura posicional. EVA fusiona estas variantes en 34 tipos, borrando la señal posicional de los unigramas y forzando al modelo a depender del contexto de bigramas para recuperarla parcialmente. Esto produce dos efectos observables: (1) el mínimo de entropía se desplaza un paso más tarde (de H₂ en STA1 a H₃ en EVA), porque se necesita un carácter de contexto adicional para desambiguar posiciones que STA1 codifica directamente; y (2) el rebote subsiguiente es más débil (0.309 vs 0.813), porque el contexto por sí solo no puede reconstruir completamente la información posicional perdida en la fusión many-to-one de glifos.

Bootstrap (200 resamples): los IC 95% de bounce no se solapan (STA1 [0.779, 0.825] vs EVA [0.313, 0.335]); los de MI_pos sí se solapan (STA1 [0.653, 0.664] vs EVA [0.663, 0.676]), confirmando que MI_pos es genuinamente robusto entre transcripciones.

## 34.3 Neural v2 sobre EVA (notebook `24_neural_v2_eva.ipynb`)

Pipeline Neural v2 adaptado para EVA:
- **Sin restricciones C/V** (EVA no tiene información de posición silábica)
- **Sin grammar anchors** (los anchors requieren clasificación posicional de STA1)
- **Scoring simplificado:** w_lm=2.0, w_card=0.5, w_ent=0.3 (sin w_pos, sin w_gram)
- 20 seeds EM, 4 cadenas MCMC, 5 tests de validación

### Resultados

| Métrica | EVA Neural v2 | STA1 Neural v2 |
|---------|---------------|----------------|
| |Σ|/|A| | **1.26** | 6.15 |
| Val loss (LM) | 2.013 | 2.004 |
| Score media EM | -38.09 ± 0.82 | -36.34 ± 0.23 |
| Roots media EM | 1.2 ± 1.0 | 1.5 ± 1.1 |
| MCMC best score | -36.15 | -36.34 |
| **N-gram %ile** | **0.0%** | **68%** |
| **Roots** | **0** | **3** |
| R-hat < 1.1 | 66.7% | 71% |
| Cardinality | 0.74 | 0.96 |
| Collapse z | -1.97 (FAIL) | -0.41 (PASS) |
| **Scorecard** | **2+/0±/3−** | **4+/0±/1−** |

### Diagnóstico

El mapping EVA es **masivamente degenerado**: 8 glifos EVA → ה (he), 4 → י (yod), 3 → ם (mem final). La posterior muestra incertidumbre extrema para glifos poco frecuentes (cfh, cph, ckh tienen distribuciones casi uniformes sobre 20+ caracteres). El ratio |Σ|/|A|=1.26 — teóricamente en el rango resoluble — no ayuda porque:

1. **EVA destruye información posicional.** Los 166 tipos de STA1 codifican estructura posicional real (73% position-locked). EVA colapsa variantes que tienen roles posicionales distintos en un mismo token, eliminando señal discriminativa.
2. **El LM sin restricciones colapsa a alta frecuencia.** Sin C/V constraints ni grammar anchors, el optimizador es libre de mapear todos los glifos frecuentes a los pocos caracteres hebreos más comunes.
3. **El problema no es el ratio |Σ|/|A|.** El Zodiac 340 (ratio ~1.3) fue resuelto porque es un cifrado de sustitución genuino. El Voynich no lo es — reducir el ratio no elimina la barrera fundamental.

## 34.4 Conclusión

La comparación STA1/EVA confirma que:
- Los hallazgos robustos (MI_pos, spectral gap, estabilidad) reflejan propiedades genuinas del manuscrito
- El bounce es específico de STA1 (inventario fino)
- **El límite del descifrado es inherente a la codificación del manuscrito**, no al sistema de transcripción ni al ratio de tamaños de alfabeto

Notebooks: `23_transcription_robustness.ipynb`, `24_neural_v2_eva.ipynb` · Resultados: `transcription_robustness_resultados.json`, `neural_v2_eva_resultados.json`

# Capítulo 35. Sustitución morfológica (Modelo 15)

## 35.1 Motivación

Los 14 modelos anteriores tratan cada glifo como una entrada en una tabla de sustitución indexada por posición silábica o sin condición alguna. Sin embargo, si el autor del Voynich era un cabalista judío del siglo XV, conocería íntimamente la morfología hebrea: prefijos gramaticales (ו,ה,ב,כ,ל,מ,ש), raíces consonánticas (22 letras) y sufijos (ה,ת,ם,ן,ך). La hipótesis: **3 tablas de sustitución indexadas por rol morfológico** (P=prefijo, R=raíz, S=sufijo), no por posición del glifo en la palabra.

Esto explicaría:
- **Position-locking** (MI_pos=0.658): los roles morfológicos correlacionan con la posición (prefijos→inicio, raíces→centro, sufijos→final)
- **166 tipos distintos**: ~27 chars × 3 roles × variación ≈ 160
- **Por qué la tabla única (68%) supera a 3 tablas posicionales (14%)**: la posición es un proxy imperfecto del rol morfológico

## 35.2 Diseño

Cada glifo mapea a un par **(carácter hebreo, rol morfológico)**. El scoring combina:
- **w_lm=2.0**: log-probabilidad del LSTM (igual que neural v2)
- **w_morph=3.0**: consistencia morfológica — para cada palabra decodificada, se segmenta en prefijo/raíz/sufijo y se comprueba si los roles asignados coinciden
- **w_card=0.5, w_ent=0.3, w_role=0.5**: cardinalidad, entropía, distribución de roles

Propuestas mixtas: 70% cambian el carácter dentro del set válido del rol actual, 30% reasignan el glifo a un rol diferente.

Inicialización: onset→P, nuclear→R, coda→S (proxy posicional).

20 seeds EM paralelas (15 CPUs), 4 cadenas MCMC paralelas.

## 35.3 Resultados

### Multi-seed EM (20 seeds)

| Métrica | Valor |
|---------|-------|
| Score medio | -102.27 ± 3.26 |
| Roots medio | 1.1 ± 1.1 (max 3) |
| Morph consistency medio | 0.472 ± 0.089 |
| Mejor candidato | Seed 5: score -99.16, K=25, roots 3, morph 0.540 |
| Role distribution (mejor) | P=38, R=49, S=79 |

### MCMC (4 cadenas, 20K iter)

| Métrica | Valor |
|---------|-------|
| Best score | -96.43 |
| K_eff | 25 |
| R-hat < 1.1 | **84.3%** |
| Accept rates | 0.8-1.1% |
| Morph consistency | 0.538 |

### Tablas emergentes

| Tabla | Glyphs | Chars únicos |
|-------|--------|-------------|
| P (prefijo) | 40 | 7 |
| R (raíz) | 52 | 25 |
| S (sufijo) | 74 | 5 |

La distribución P/R/S (40/52/74) está sesgada hacia S — el optimizador asigna demasiados glifos al rol de sufijo, contrario a la distribución esperada del hebreo bíblico (~20%P/60%R/20%S).

### Scorecard (6 tests)

| Test | Valor | Veredicto |
|------|-------|-----------|
| Collapse z-score | 0.00 | PASS |
| N-gram percentile | 16.0% | PASS (borderline) |
| Root matching | 0 roots | FAIL |
| Cardinality ratio | 0.93 (25/27) | PASS |
| Morph consistency | 48.1% (69 %ile) | MARGINAL |
| Word length z | 0.23 | PASS |

**Scorecard: 4+/1±/1−**

### Comparación con Neural v2

| Métrica | Morfológico | Neural v2 |
|---------|------------|-----------|
| N-gram %ile | 16% | **68%** |
| Roots | 0 | **3** |
| R-hat < 1.1 | 84.3% | 71% |
| Cardinality | 0.93 | 0.96 |
| Scorecard | 4+/1±/1− | **4+/0±/1−** |

## 35.4 Diagnóstico

1. **Morph consistency 48% (MARGINAL)**: el optimizador alinea parcialmente los roles asignados con la segmentación morfológica hebrea, pero no alcanza el 80%. La correspondencia posición→rol es real pero insuficiente para el descifrado.

2. **Role stability 58.4%**: solo ~58% de los glifos mantienen el mismo rol en >80% del posterior MCMC. Las tablas no están bien definidas — el sistema oscila entre asignaciones alternativas.

3. **N-gram 16%** (borderline PASS): comparable al syllabic positional (14%) pero muy inferior al neural v2 (68%). Añadir la dimensión morfológica no compensa la pérdida de coherencia de tabla única.

4. **0 roots en validación**: el techo de raíces persiste incluso con segmentación morfológica explícita.

5. **Accept rates ~1%**: el espacio de búsqueda (166 glifos × 3 roles × chars por rol) es enorme, y la función de scoring con w_morph crea un paisaje rugoso.

## 35.6 Réplica con Zohar/Arameo (Modelo 16)

Se replica el experimento morfológico sustituyendo el corpus Torah (hebreo) por Zohar (arameo), con adaptaciones morfológicas: prefijos arameos (ד,ב,כ,ל,מ,ו — 6 chars, sin ה/ש del hebreo) y sufijos arameos (א,ה,ת,ן,ך,י — 6 chars, con א como artículo definido pospuesto).

| Métrica | Modelo 15 (Torah) | Modelo 16 (Zohar) |
|---------|:-:|:-:|
| Scorecard | 4+/1±/1− | 3+/0±/3− |
| N-gram | 16% | 0.0% |
| Roots (validación) | 0 | 1 (הלך) |
| Morph consistency | 48.1% (P69) | 42.0% (P45) |
| val_loss LM | 2.004 | 2.111 |
| Score medio EM | -102.27±3.26 | -103.33±2.50 |

**Resultado:** El Zohar/arameo es peor que Torah/hebreo en todas las métricas. El n-gram cae de 16% a 0%, la consistencia morfológica baja del percentil 69 al 45. El LM del Zohar es más permisivo (val_loss 2.111 vs 2.004) pero produce mappings sin estructura léxica. **Modelo 16 DESCARTADO** — confirma que la barrera es estructural, no dependiente del corpus target.

## 35.7 Conclusión

**Hipótesis de sustitución morfológica DESCARTADA.** El modelo añade complejidad (3 tablas + roles) sin superar la tabla única de neural v2. El n-gram 16% es 4× peor que el 68% de referencia, y los 0 roots en validación confirman la barrera estructural. La correspondencia parcial (48% morph consistency) sugiere que la estructura posicional del Voynich tiene una componente morfológica real, pero esta no es explotable para el descifrado dentro del paradigma de sustitución. La réplica con Zohar/arameo (Modelo 16) confirma el patrón: el cambio de corpus target empeora todas las métricas (n-gram 0%, consistencia P45), reforzando que el límite es propiedad del espacio de soluciones y no del corpus elegido.

Notebook: `25_morphological.ipynb`, `26_morphological_zohar.ipynb` · Resultados: `morphological_resultados.json`, `morphological_zohar_resultados.json`

## 35.8 Experimentos cross-lingüísticos: Hebreo Tibbónido, Judeo-Árabe y Ge'ez (Modelos 17–19)

Se testaron tres lenguas target adicionales con el pipeline Neural v2 (20 seeds × 2 temperaturas, 4 cadenas MCMC), cada una abordando una hipótesis específica sobre por qué persiste el techo estructural.

### 35.8.1 Modelo 17: Hebreo Tibbónido (Moreh Nevuchim) — notebook `33_tibbonid_hebrew.ipynb`

**Hipótesis:** El autor del Voynich escribió en el hebreo filosófico de la escuela de Ibn Tibbon, no en hebreo bíblico.

**Corpus:** Moreh Nevuchim completo (Guía de los Perplejos), edición Makbili 2024 vía Sefaria; 157.042 palabras, 27 caracteres. Longitud media 4.21 (vs. Voynich 4.24).

| Métrica | Torah (Mod. 7) | Tibbónido (Mod. 17) |
|---------|----------------|---------------------|
| Val loss | 2.004 | 2.107 |
| N-gram % | **68%** | 13% (MARGINAL) |
| Roots | 3 | 3 |
| R-hat < 1.1 | 71.1% | 54.2% |
| Scorecard | **4+/0±/1−** | 3+/1±/1− |

**Resultado:** El LM tibbónido es menos predictivo que el bíblico. El n-gram cae de 68% a 13%. El techo de roots (3) no cambia. **Modelo 17 DESCARTADO.**

### 35.8.2 Modelo 18: Judeo-Árabe (proxy coránico) — notebook `34_judeo_arabic.ipynb`

**Hipótesis:** El Voynich codifica judeo-árabe (árabe escrito en caracteres hebreos).

**Corpus:** Árabe coránico (Uthmani, 77.875 palabras) transliterado a caracteres hebreos siguiendo la convención judeo-árabe estándar (28 consonantes árabes → 22 letras hebreas). |Σ|/|A| ≈ 7.5.

| Métrica | Torah (Mod. 7) | Judeo-Árabe (Mod. 18) |
|---------|----------------|----------------------|
| Val loss | 2.004 | **1.975** (¡mejor LM!) |
| N-gram % | **68%** | 12% (MARGINAL) |
| Roots | 3 | 1 |
| Grammar | PASS (100%) | **FAIL (0%)** |
| Scorecard | **4+/0±/1−** | 2+/1±/2− |

**Resultado:** Paradójicamente, el LM judeo-árabe tiene la mejor val\_loss de todos los modelos (1.975), pero produce el segundo peor mapping. **Modelo 18 DESCARTADO.**

### 35.8.3 Modelo 19: Ge'ez Clásico (Etíope) — notebook `35_geez.ipynb`

**Hipótesis:** Este es el test teóricamente más significativo. El Ge'ez se escribe en un abugida donde cada carácter codifica un par consonante+vocal. Con 188 caracteres silábicos, da |Σ|/|A| ≈ 0.88 — casi 1:1 con los 166 glifos del Voynich. Es el primer modelo que elimina el problema de LM dominance.

**Conexión histórica:** Monjes etíopes asistieron al Concilio de Florencia (1441) y mantenían comunidad permanente en Santo Stefano dei Mori (Vaticano) desde el siglo XIV.

**Corpus:** TraCES Corpus de Etíope Clásico, Universidad de Hamburgo; 62.671 palabras, 188 caracteres silábicos. Sin distinción C/V; sin grammar anchors.

| Métrica | Torah (Mod. 7) | Ge'ez (Mod. 19) |
|---------|----------------|------------------|
| Chars target | 27 | 188 |
| |Σ|/|A| | 6.1 | **0.88** |
| N-gram % | **68%** | **0%** (peor de los 19) |
| Collapse z | −0.94 (PASS) | **−3.50 (FAIL)** |
| Cardinalidad | 92.6% | **63.3%** |
| R-hat < 1.1 | 71.1% | **80.5%** (mejor de todos) |
| Scorecard | **4+/0±/1−** | **1+/0±/3−** |

**Resultado:** A pesar del ratio casi óptimo, el Ge'ez produce el peor descifrado de los 19 modelos. Las cadenas MCMC convergen bien (80.5% R-hat) pero convergen hacia un mapping degenerado. **Modelo 19 DESCARTADO.**

**Significación teórica:** Este resultado demuestra que el techo estructural NO es un artefacto del desajuste de tamaño de alfabeto. La barrera persiste independientemente de si el target es un abjad (hebreo, 27 chars), un alfabeto (latín, 26), o un abugida (Ge'ez, 188 sílabas). El match numérico 166≈188 resulta ser una coincidencia.

Notebooks: `33_tibbonid_hebrew.ipynb`, `34_judeo_arabic.ipynb`, `35_geez.ipynb`
Resultados: `tibbonid_resultados.json`, `judeo_arabic_resultados.json`, `geez_resultados.json`

## 35.10 Efecto de la restricción C/V (notebook `27_cv_constraint.ipynb`)

El pipeline Neural v2 clasifica cada glifo Voynich como C(onsonante) o V(ocal) según su posición silábica preferida, y restringe el mapeo: glifos C → consonantes hebreas, glifos V → matres lectionis (א,ה,ו,י). Dado que el hebreo es un abjad que omite la mayoría de las vocales, forzar los glifos nucleares a mapear solo a 4 caracteres podría ser un cuello de botella artificial.

**Diseño:** 3 condiciones × 10 seeds, mismo LSTM, misma arquitectura EM:

| Condición | C/V | Anchors | N-gram %ile | Roots max | Roots mean |
|-----------|-----|---------|-------------|-----------|------------|
| **A: Con C/V + anchors** | Sí | Sí | **100%** | 3 | 2.0 |
| B: Sin C/V + anchors | No | Sí | 96% | 5 | 1.7 |
| C: Sin C/V, sin anchors | No | No | 85% | 6 | 3.0 |

**Resultado:** Eliminar la restricción C/V no mejora el n-gram percentile — de hecho lo baja ligeramente (100% → 96%). La condición C (totalmente libre) encuentra más raíces en media (3.0 vs 2.0) pero con un percentile más bajo (85%). La mayor libertad permite más coincidencias espurias sin mejorar la calidad lingüística.

**Conclusión:** La hipótesis del mismatch abjad queda descartada. La restricción C/V tiene efecto mínimo (~4 pp en percentile); el techo de descifrado es una propiedad estructural del texto Voynich, no un artefacto de forzar glifos vocálicos a las matres lectionis hebreas.

Notebook: `27_cv_constraint.ipynb` · Resultados: `cv_constraint_resultados.json`


---

Continued in Part XI.
