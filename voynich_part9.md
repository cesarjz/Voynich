# PARTE IX — Modelos de Descifrado Neural y Silábico (Capítulos 23–27)


# Neural LM y scoring léxico-radicular

La Parte VIII cerró con un diagnóstico convergente desde tres modelos (composicional, constrained, homofónico): la dominancia del CharLM trigrama con smoothing Witten-Bell es el problema fundamental. El LM colapsa el mapping hacia pocos caracteres de alta frecuencia (especialmente shin), y ninguna combinación de restricciones adicionales resuelve el conflicto entre verosimilitud y validez lingüística. La Parte IX ataca directamente esta raíz causal sustituyendo el CharLM trigrama por un Neural CharLM (LSTM) con temperatura controlable (Capítulo 23), y luego evalúa si un componente de scoring léxico-radicular puede añadir especificidad léxica sin destruir la diversidad ganada (Capítulo 24).

# Capítulo 23. Neural CharLM con gramática y cardinalidad

## 23.1 Motivación: superar la dominancia del CharLM trigrama

El diagnóstico de las Partes V--VIII identifica al CharLM trigrama como causa raíz del mapping degenerado. El problema tiene dos facetas:

1. **Colapso por verosimilitud.** El smoothing Witten-Bell asigna probabilidades desproporcionadas a bigramas y trigramas frecuentes del hebreo, creando un gradiente que empuja todos los glifos hacia shin (ש), la consonante más frecuente del corpus Torah.

2. **Temperatura fija.** El CharLM opera implícitamente a T=1.0, sin mecanismo para controlar la "dureza" de la distribución de probabilidad. No hay forma de suavizar el LM para permitir mayor diversidad.

Un Neural CharLM (LSTM) resuelve ambos problemas: aprende representaciones distribuidas que generalizan mejor que counts + smoothing, y admite temperatura ajustable T que controla el trade-off entre concentración (T baja → peaky) y diversidad (T alta → flat).

## 23.2 Arquitectura y entrenamiento

Se implementa un LSTM de 2 capas como modelo de lenguaje a nivel de carácter (celda 4 del notebook `12_neural_lm.ipynb`):

| Parámetro | Valor |
|-----------|-------|
| Embedding | 32 dims |
| Hidden | 192 dims |
| Capas LSTM | 2 |
| Dropout | 0.2 |
| Parámetros totales | 476,991 |
| Contexto | Bigrama (2 caracteres) |

El modelo se entrena sobre el corpus hebreo (Torah, subsampleado a 37K palabras para igualar el Voynich) con split 80/20, AdamW, cosine annealing, early stopping con patience=5.

| Métrica | Valor |
|---------|-------|
| Épocas entrenadas | 30 |
| Mejor val loss | 2.004 |
| PPX baseline (trigrama) | 7.37 |
| PPX neural (T=1.0) | 7.48 |

La perplejidad neural a T=1.0 es prácticamente idéntica a la del trigrama (7.48 vs 7.37), confirmando que el LSTM aprende una distribución comparable. La ventaja del neural no es en PPX absoluta sino en la **controlabilidad vía temperatura**.

Se mantienen los grammar anchors (12 glifos con roles prefix/root/suffix anclados a subconjuntos del alfabeto hebreo) y la clasificación C/V posicional de las partes anteriores.

## 23.3 Análisis de temperatura

Se evalúa el efecto de T sobre la entropía y PPX del LM (celda 6):

| T | H media | PPX |
|---|---------|-----|
| 0.3 | 1.18 | 30.1 |
| 0.5 | 1.88 | 11.5 |
| 0.8 | 2.62 | 8.1 |
| 1.0 | 2.98 | 7.7 |
| 1.5 | 3.58 | 8.2 |
| 2.0 | 3.92 | 9.2 |
| 3.0 | 4.31 | 11.4 |
| 5.0 | 4.64 | 15.0 |

T controla un continuo entre concentración (T=0.3, H=1.18) y uniformidad (T=5, H=4.64). A T≥2, la entropía supera los 3.9 bits, suficiente para soportar 27 caracteres activos sin colapso.

## 23.4 Scoring compuesto y sweep

El scoring neural tiene 5 componentes (celda 7):

| Componente | Peso | Función |
|------------|------|---------|
| S_LM | w_lm = 2.0 | Log-prob bajo LSTM con temperatura T |
| S_pos | w_pos = 0.5 | Compatibilidad C/V posicional |
| S_card | w_card = 0.5 | Penalización cuadrática si K < K_max |
| S_ent | w_ent = 0.3 | Entropía normalizada del mapping |
| S_gram | w_gram = 2.0 | Grammar anchors (12 glifos) |

Se implementa scoring incremental: al cambiar un glifo, solo se re-evalúan las palabras que lo contienen (GPU batch), reduciendo el coste por propuesta de O(N) a O(k) donde k es el número medio de palabras por glifo.

El sweep explora T × w_gram × w_card × K_max (90 configuraciones, 200 iter EM corto, 500 palabras). El resultado es claro: **T=3.0, w_gram=2.0, w_card=0.5, K_max=20** domina el ranking. T=3 es el punto óptimo donde la entropía es suficiente para diversidad (H=4.3) sin destruir completamente la estructura n-grámica.

## 23.5 EM completo y MCMC

Con la mejor configuración del sweep, se ejecuta EM completo (3000 palabras, 2000 iter, patience=100) seguido de MCMC multi-chain:

**EM:**

| Config | Score | K_eff | Grammar | Convergencia |
|--------|-------|-------|---------|--------------|
| T=3, K_max=20 | -36.23 | 27 | 1.00 | iter 268 |
| T=3, K_max=23 | -36.23 | 27 | 1.00 | iter 261 |
| T=3, K_max=27 | -36.23 | 27 | 1.00 | iter 210 |
| Baseline trigrama | -40.66 | 27 | 0.00 | iter 243 |

**Resultado clave:** el neural con T=3 alcanza K_eff=27/27 (todos los caracteres hebreos activos) y grammar=1.00 (12/12 anchors correctos). El score (-36.23) supera ampliamente al baseline trigrama (-40.66).

**MCMC (4 cadenas × 20K iteraciones):**

| Métrica | Valor |
|---------|-------|
| Best score | -36.23 |
| K_eff | 26 |
| R-hat < 1.1 | **69.9%** |
| Accept rates | 29--32% |

La convergencia MCMC (69.9%) es la mejor de todos los modelos probados.

## 23.6 Validación: scorecard 4 PASS / 0 MARGINAL / 1 FAIL

| Test | Valor | Criterio | Resultado |
|------|-------|----------|-----------|
| 1. Collapse z-score | -0.72 | z > -1.0 | **PASS** |
| 2. N-gram percentile | 38.0% | >15% | **PASS** |
| 3. Root matching | 1 raíz | >10 raíces | **FAIL** |
| 4. Cardinality ratio | 0.96 (26/27) | >0.6 | **PASS** |
| 5. Grammar anchors | 100% (12/12) | >60% | **PASS** |

**Veredicto: 4 PASS / 0 MARGINAL / 1 FAIL.**

El neural resuelve los problemas de las Partes V--VIII:
- **Collapse:** z=-0.72 (PASS), frente a la degeneración shin de los modelos anteriores.
- **N-gramas:** 38% percentil (PASS), el mejor de todos los modelos. T=3 preserva suficiente estructura secuencial.
- **Cardinalidad:** 26/27 chars activos (PASS), frente a ~10 del composicional.
- **Grammar:** 100% anchors correctos (PASS).

El **único FAIL** es root matching: solo 1 raíz hebrea reconocible (vs 6 en composicional, 100 en constrained). T=3 rompe la degeneración del LM pero destruye la especificidad léxica: el mapping es diverso y gramaticalmente correcto pero no produce trigramas consonánticos que coincidan con raíces bíblicas.

## 23.7 Comparación con modelos anteriores

| Métrica | Composicional | Constrained | Homofónico | **Neural** |
|---------|---------------|-------------|------------|------------|
| Chars usados | ~10 | — | — | **26** |
| N-gram %ile | 24% | 5% | 28% | **38%** |
| Roots matched | 6 | 100 | — | 1 |
| Collapse z | -0.56 | -0.45 | -0.79 | **-0.72** |
| R-hat < 1.1 | 59% | 40% | 68% | **70%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | **4+/0±/1−** |

El neural domina en 4 de 5 tests. El trade-off es claro: la diversidad ganada por T=3 se paga con la pérdida de raíces léxicas.

Notebook: `12_neural_lm.ipynb` · Resultados: `neural_resultados.json`

# Capítulo 24. Scoring léxico-radicular (S_root)

## 24.1 Hipótesis: combinar diversidad neural con especificidad léxica

El Capítulo 23 establece que el neural LM con T=3 logra 4 PASS pero falla en root matching (1 raíz). El constrained (Parte VII) logra 100 raíces pero con n-gramas al 5% y mapping degenerado. La pregunta es: ¿puede un 6º componente de scoring S_root, que recompense raíces hebreas reconocibles, combinar la diversidad del neural con la coherencia léxica del constrained?

**Hipótesis:** La combinación de temperatura T≥2 (diversidad) + S_root (especificidad léxica) debería mantener cardinalidad alta, n-gramas razonables (>15%) y mejorar significativamente el root matching.

## 24.2 Diseño de S_root

Se implementan tres decisiones de diseño clave (celda 6 del notebook `13_lexical_scoring.ipynb`):

**1. IDF-weighted distinct roots.** S_root cuenta raíces *distintas* (no total de matches) ponderadas por inverse document frequency. Raíces raras en el corpus hebreo valen más, evitando overfitting a raíces comunes.

| Raíz | IDF (top-5, raras) | Raíz | IDF (bottom-5, comunes) |
|------|--------------------|------|-------------------------|
| קרא | 0.0139 | דבר | 0.0062 |
| טמא | 0.0139 | מים | 0.0064 |
| מלא | 0.0139 | היה | 0.0066 |
| נשא | 0.0139 | שים | 0.0067 |
| אבן | 0.0139 | יום | 0.0068 |

**2. Skeleton determinístico durante optimización.** Se extraen solo consonantes (strip matres lectionis), sin wildcards. Más estricto que la validación (que usa confidences), para evitar la inflación artificial que se observó en el constrained (100 raíces, muchas por wildcards en skeletons de baja confianza).

**3. Scoring incremental.** Al cambiar un glifo, solo se re-evalúan las raíces de las palabras que lo contienen. Root matching es string ops puro, sin coste GPU.

**Distribución nula de S_root:**

| Métrica | Valor |
|---------|-------|
| Mean (50 mappings aleatorios) | 0.011 |
| Std | 0.011 |
| Threshold significativo (mean + 2σ) | 0.034 |

## 24.3 Scoring compuesto: 6 componentes

Se extiende el scoring neural con un 6º componente (celda 7):

| Componente | Peso fijo | Función |
|------------|-----------|---------|
| S_LM | w_lm = 2.0 | LSTM con temperatura T |
| S_pos | w_pos = 0.5 | Compatibilidad C/V |
| S_card | w_card = 0.5 | Penalización cardinalidad |
| S_ent | w_ent = 0.3 | Entropía del mapping |
| S_gram | w_gram = 2.0 | Grammar anchors |
| **S_root** | **w_root ∈ {0..5}** | **IDF-weighted distinct roots** |

Los 5 pesos originales se fijan a los valores óptimos del Capítulo 23. Solo se barren w_root × T.

## 24.4 Sweep w_root × T

Grid: w_root ∈ {0, 0.3, 0.5, 1, 2, 3, 5} × T ∈ {2, 3, 5} = 21 configuraciones. EM corto: 200 iter, patience=20, 500 palabras (celda 8):

| w_root | T=2 | T=3 | T=5 |
|--------|-----|-----|-----|
| 0 | 4 | 4 | 2 |
| 0.3 | 5 | 5 | 5 |
| 0.5 | 5 | 5 | 4 |
| 1 | 6 | 5 | 4 |
| 2 | 8 | 5 | 6 |
| 3 | 8 | 5 | 6 |
| 5 | 9 | 8 | **11** |

*(Tabla: número de raíces distintas encontradas por el EM corto con skeleton determinístico)*

**S_root genera un efecto monotónico real.** A w_root=0, el baseline encuentra 2--4 raíces. A w_root=5, se alcanzan 9--11. La cardinalidad K_eff=27 se mantiene en todas las configuraciones. Los JSD son similares (~0.76) en el sweep corto.

## 24.5 EM completo: de 5 a 15 raíces

Se ejecuta EM completo (3000 palabras, 2000 iter, patience=100) con las top-3 configuraciones del sweep más el baseline w_root=0 (celda 9):

| Config | Score | K_eff | Grammar | Roots | Raíces encontradas |
|--------|-------|-------|---------|-------|--------------------|
| T=5, wr=5 | -37.87 | 27 | 1.00 | **15** | ברך בשר גבר דבר דמם דרך כתב לחם מלך עבר עצם רחם רעע שמע שמר |
| T=2, wr=5 | -36.48 | 27 | 1.00 | 13 | — |
| T=2, wr=2 | -36.65 | 27 | 1.00 | 11 | ברך דבר דמם דרך זכר חכם כתב עבר עצם רחם רעע |
| T=2, wr=0 | -36.71 | 27 | 1.00 | 5 | — |

**S_root triplica las raíces durante el EM:** de 5 (baseline) a 15 (T=5/wr=5) o 11 (T=2/wr=2). Las 15 raíces del mejor config incluyen raíces semánticamente coherentes: דבר (hablar), שמע (escuchar), כתב (escribir), מלך (rey), דרך (camino), לחם (pan), בשר (carne).

## 24.6 MCMC y validación: dos configuraciones testadas

Se testaron dos configuraciones en MCMC completo (4 cadenas × 20K iter, burn-in=5000) para evaluar el efecto de la temperatura:

### Config 1: T=5, w_root=5 (maximiza roots)

| Métrica MCMC | Valor |
|--------------|-------|
| Best score | -37.82 |
| K_eff | 25 |
| R-hat < 1.1 | 70.6% |
| Accept rates | 29--30% |

| Test | Valor | Resultado |
|------|-------|-----------|
| 1. Collapse z-score | -0.91 | **PASS** |
| 2. N-gram percentile | 12.0% | **MARGINAL** |
| 3. Root matching | 4 raíces | **FAIL** |
| 4. Cardinality ratio | 0.93 | **PASS** |
| 5. Grammar anchors | 100% | **PASS** |

**Scorecard: 3 PASS / 1 MARGINAL / 1 FAIL.** Raíces validadas: ברך (bendecir), דרך (camino), מלך (rey), עצם (hueso/esencia).

### Config 2: T=2, w_root=2 (preserva n-gramas — hipótesis)

| Métrica MCMC | Valor |
|--------------|-------|
| Best score | -36.65 |
| K_eff | 27 |
| R-hat < 1.1 | 67.3% |
| Accept rates | 30--33% |

| Test | Valor | Resultado |
|------|-------|-----------|
| 1. Collapse z-score | -1.07 | **MARGINAL** |
| 2. N-gram percentile | 12.0% | **MARGINAL** |
| 3. Root matching | 3 raíces | **FAIL** |
| 4. Cardinality ratio | 1.00 | **PASS** |
| 5. Grammar anchors | 100% | **PASS** |

**Scorecard: 2 PASS / 2 MARGINAL / 1 FAIL.** Raíces validadas: ברך (bendecir), דבר (hablar), דרך (camino).

### Comparación entre las dos configs

| Métrica | T=5/wr=5 | T=2/wr=2 | Observación |
|---------|----------|----------|-------------|
| N-gram %ile | 12% | 12% | Idéntico — T no es el factor |
| Roots validados | 4 | 3 | Similar |
| Collapse z | -0.91 | -1.07 | T=2 empeora colapso |
| K_eff | 25 | 27 | Ambas diversas |
| Scorecard | 3+/1±/1− | 2+/2±/1− | T=5 ligeramente mejor |

**Hallazgo inesperado:** bajar T de 5 a 2 **no recupera los n-gramas** (12% en ambos casos). La hipótesis de que "T alta degrada n-gramas" era incorrecta: la degradación proviene de S_root en sí mismo, no de T. Además, T=2 empeora el colapso (z=-1.07, 11 grupos DEGENERATE) porque sin la entropía alta de T=5, el LM empuja hacia mayor concentración.

Las raíces son parcialmente inestables entre configuraciones: solo ברך y דרך aparecen en ambas. מלך y עצם desaparecen con T=2; דבר aparece.

## 24.7 Test de significancia estadística

Para determinar si las 3--4 raíces validadas son señal o ruido, se ejecuta un test de nulidad: ¿cuántas raíces encuentra un mapping aleatorio con K=25 sobre las top-200 palabras?

| Estadístico | Null (500 mappings aleatorios) | Lexical |
|-------------|-------------------------------|---------|
| Mean roots | 0.5 | — |
| Std | 0.8 | — |
| Max | 5 | — |
| Lexical T=5/wr=5 | — | **4 raíces** |
| Percentil | — | **99.2%** |
| p-value | — | **0.008** |

Las 4 raíces del lexical (T=5/wr=5) están en el percentil 99.2% de la distribución nula (p=0.008). **La señal es estadísticamente significativa**: un mapping aleatorio con la misma cardinalidad encontraría 0--1 raíces; encontrar 4 es improbable por azar.

Para el EM (3000 palabras, K=27, top-500 palabras):

| Estadístico | Null (200 mappings) | Lexical EM |
|-------------|---------------------|------------|
| Mean roots | 0.9 | — |
| P(≥10) | 0.0% | — |
| P(≥15) | 0.0% | — |
| Lexical EM | — | **15 raíces** |

Las 15 raíces del EM son también altamente significativas vs null.

## 24.8 Diagnóstico: el trade-off es intrínseco al multi-objetivo

El experimento lexical produce tres hallazgos:

### S_root guía eficazmente al optimizador

El efecto es monotónico, significativo y reproduce raíces semánticamente coherentes. De 2--5 raíces (baseline) a 11--15 (con S_root), con p≈0 vs null. El mecanismo de IDF-weighting + skeleton determinístico funciona como diseñado.

### Las raíces no sobreviven la validación estricta

De 15 raíces durante el EM, solo 3--4 pasan la validación con confidences (threshold 0.70). La brecha indica que la mayoría de las raíces del EM son artefactuales: glifos de baja confianza posterior que el optimizador ajusta para "fabricar" trigramas consonánticos de raíces, sin evidencia estadística suficiente en el posterior MCMC.

### El trade-off es intrínseco al multi-objetivo, no a la temperatura

La hipótesis original era que T alta degrada n-gramas y bajar T los recuperaría. Los datos la refutan: n-gram percentile es 12% tanto con T=5 como con T=2. El culpable no es T sino **S_root en sí mismo**. Cualquier w_root > 0 desplaza el mapping de la solución óptima del LM hacia una región del espacio que favorece trigramas de raíces a costa de estructura n-grámica. El espacio de mappings no contiene una región donde coexistan alta calidad n-grámica (>15%) y alta densidad de raíces (>10).

## 24.9 Tabla comparativa final: 5 modelos

| Métrica | Composicional | Constrained | Homofónico | Neural | **Lexical** |
|---------|---------------|-------------|------------|--------|-------------|
| Chars usados | ~10 | — | — | 26 | 25--27 |
| N-gram %ile | 24% | 5% | 28% | **38%** | 12% |
| Roots matched | 6 | 100 | — | 1 | 3--4 |
| Collapse z | -0.56 | -0.45 | -0.79 | -0.72 | -0.91 a -1.07 |
| R-hat < 1.1 | 59% | 40% | 68% | **70%** | 67--71% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | **4+/0±/1−** | 2--3+/1--2±/1− |

El neural puro (Capítulo 23) sigue siendo el mejor modelo global con 4 PASS. El lexical aporta 2--3 raíces adicionales estadísticamente significativas, pero a un coste sustancial en n-gramas y colapso.

## 24.10 Conclusiones del Capítulo 24

1. **S_root funciona como mecanismo de optimización.** El componente IDF-weighted triplica las raíces durante el EM (de 5 a 15), con significancia estadística vs null (p≈0 para EM, p=0.008 para validación).

2. **Las raíces no sobreviven la validación estricta.** De 15 raíces EM, solo 3--4 pasan el test con confidences. La brecha es diagnóstica: el optimizador puede "fabricar" raíces ajustando glifos de baja confianza, pero estas no tienen soporte en el posterior MCMC.

3. **El trade-off diversidad/léxico es intrínseco, no configurable.** Ni la temperatura ni la ponderación de w_root permiten negociarlo: cualquier S_root > 0 degrada los n-gramas de ~38% a ~12%, independientemente de T. El espacio de mappings no tiene una región Pareto-óptima donde coexistan ambas propiedades.

4. **Las 3--4 raíces validadas son estadísticamente significativas** (p=0.008), lo que sugiere que el mapping contiene señal léxica real, aunque demasiado débil para sostener un descifrado completo.

5. **El neural puro (T=3, sin S_root) sigue siendo el mejor modelo** con scorecard 4+/0±/1−. El valor del experimento lexical es demostrar cuantitativamente *por qué* el root matching es el test más difícil de todos los evaluados: requiere simultanear diversidad de mapping, calidad n-grámica y especificidad léxica, tres objetivos que compiten en el espacio de soluciones.

6. **Las 100 raíces del constrained (Parte VII) eran parcialmente artefactuales.** El constrained lograba 100 raíces con enrichment 154× pero n-gramas al 5%, y su skeleton usaba wildcards para glifos de baja confianza. El lexical, con skeleton determinístico (sin wildcards), demuestra que la mayoría de esas raíces desaparecen cuando se exige consistencia en el mapping. El número real de raíces sustentables es 3--4 con p=0.008, un orden de magnitud menor pero estadísticamente más robusto.

Notebooks: `12_neural_lm.ipynb`, `13_lexical_scoring.ipynb` · Resultados: `neural_resultados.json`, `lexical_resultados.json`

# Capítulo 25. Neural v2: Multi-Seed EM + Hard-K Constraint

## 25.1 Motivación: ¿es el root matching sensible al óptimo local?

Los Capítulos 23--24 establecen un resultado aparentemente paradójico: el neural (T=3) logra el mejor scorecard global (4+/0±/1−) con solo 1 raíz, mientras que el composicional degenerado encontraba 6 y el constrained 100 (parcialmente artefactuales). El Capítulo 24 demuestra que añadir un componente léxico (S_root) degrada n-gramas de 38% a 12%, confirmando que el trade-off es intrínseco al multi-objetivo.

Sin embargo, queda una pregunta sin responder: **¿cuánto depende el root count del óptimo local al que converge el EM?** La función objetivo tiene múltiples mínimos locales de calidad similar (~-36.2), y diferentes inicializaciones podrían converger a soluciones con distintas raíces. Si la varianza del root matching entre seeds es alta, el resultado de 1 raíz del neural v1 podría ser mala suerte.

Este capítulo explora el espacio de soluciones con **dos estrategias ortogonales** que no modifican la función objetivo:

1. **Multi-seed (Estrategia A):** 20 EMs independientes con T=3 y la misma configuración óptima, variando solo la inicialización. Seeds 0--9 usan frequency mapping + scramble parcial aleatorio (~30% de glifos); seeds 10--19 usan mapping completamente aleatorio (respetando roles C/V).

2. **Hard-K + T baja (Estrategia B):** Constraint por rechazo que impide propuestas con K < 20, permitiendo temperaturas T=1.5 y T=2.0 que darían mayor señal LM. 5 seeds por cada T (10 runs total).

## 25.2 Resultados de la Estrategia A: 20 seeds con T=3

Se ejecuta EM completo (3000 palabras, 2000 iter, patience=100, 200 propuestas/iter) para cada seed (celda 7 del notebook `14_neural_v2.ipynb`):

| Seed | Init | Score | K_eff | Grammar | Roots | Raíces encontradas |
|------|------|-------|-------|---------|-------|--------------------|
| 0 | freq | -36.65 | 27 | 1.00 | 2 | ברך, דרך |
| 1 | freq | -36.49 | 27 | 1.00 | 0 | — |
| 2 | freq | -37.04 | 27 | 0.83 | 0 | — |
| 3 | freq | -36.20 | 27 | 1.00 | 1 | דבר |
| 4 | freq | -36.25 | 27 | 1.00 | 3 | חכם, לחם, שלח |
| 5 | freq | -36.18 | 26 | 1.00 | 3 | חכם, לחם, שלח |
| 6 | freq | -36.30 | 27 | 1.00 | 3 | לחם, עבד, שלח |
| 7 | freq | -36.10 | 27 | 1.00 | 1 | עבד |
| 8 | freq | -36.20 | 27 | 1.00 | 1 | דבר |
| 9 | freq | -36.61 | 27 | 1.00 | 0 | — |
| 10 | rand | -36.24 | 27 | 1.00 | 1 | עבר |
| 11 | rand | -36.20 | 27 | 0.83 | 1 | דבר |
| 12 | rand | -36.25 | 27 | 1.00 | 3 | חכם, לחם, שלח |
| 13 | rand | -36.23 | 27 | 1.00 | 3 | דבר, עבד, עבר |
| 14 | rand | -36.25 | 27 | 1.00 | 0 | — |
| 15 | rand | -36.42 | 27 | 1.00 | 2 | שמן, שמע |
| 16 | rand | -36.10 | 27 | 1.00 | 1 | עבד |
| 17 | rand | -36.22 | 27 | 1.00 | 0 | — |
| 18 | rand | -36.20 | 27 | 0.83 | 1 | דבר |
| 19 | rand | -36.63 | 27 | 0.83 | 1 | עבד |

**Estadísticas agregadas:**

| Métrica | Valor |
|---------|-------|
| Score medio ± std | -36.34 ± 0.23 |
| Roots media ± std | 1.4 ± 1.1 |
| Rango roots | 0--3 |
| Seeds con 0 roots | 5/20 (25%) |
| Seeds con 3 roots | 5/20 (25%) |
| K_eff constante | 26--27 en todos |
| Grammar ≥ 0.83 | 20/20 (100%) |

**Hallazgos clave:**

1. **Scores estables.** La desviación estándar de 0.23 sobre un score medio de -36.34 confirma una cuenca de atracción bien definida. Todos los seeds convergen a soluciones equivalentes en calidad.

2. **Root count bajo y acotado.** Ningún seed supera 3 raíces. El neural v1 con 1 raíz no era atípico: está dentro de 1σ de la media (1.4 ± 1.1).

3. **Clusters de raíces recurrentes.** Las raíces no son aleatorias: aparecen en dos clusters que comparten consonantes:
   - Cluster A: שלח/לחם/חכם (comparten ח y ל)
   - Cluster B: עבד/עבר/דבר (comparten ב y ר)

   Esto sugiere que las raíces emergen de un mismo cluster de mapeo consonántico, no de matching léxico genuino.

4. **Inicialización no importa.** Seeds freq y rand producen distribuciones de roots idénticas (media 1.5 vs 1.3, p>0.5). El tipo de inicialización no influye en la calidad final.

## 25.3 Resultados de la Estrategia B: Hard-K + T baja

Se ejecuta EM con constraint hard-K (K_min=20 por rechazo de propuestas) a T=1.5 y T=2.0, 5 seeds cada (celda 8):

| T | Seed | Score | K_eff | Grammar | Roots | Raíces | Reject% |
|---|------|-------|-------|---------|-------|--------|---------|
| 1.5 | 0 | -36.52 | 27 | 0.67 | 3 | לחם, מלך, שלח | 0.0% |
| 1.5 | 1 | -36.75 | 26 | 0.67 | 0 | — | 0.0% |
| 1.5 | 2 | -37.74 | 27 | 0.67 | 3 | דבר, עבד, עבר | 0.0% |
| 1.5 | 3 | -37.63 | 27 | 1.00 | 2 | מלך, עבד | 0.0% |
| 1.5 | 4 | -36.46 | 27 | 1.00 | 0 | — | 0.0% |
| 2.0 | 0 | -36.16 | 27 | 1.00 | 3 | חכם, לחם, שלח | 0.0% |
| 2.0 | 1 | -35.34 | 27 | 0.50 | 0 | — | 0.0% |
| 2.0 | 2 | -37.74 | 27 | 0.67 | 1 | עבד | 0.0% |
| 2.0 | 3 | -36.07 | 27 | 0.67 | 3 | לחם, מלך, שלח | 0.0% |
| 2.0 | 4 | -37.65 | 27 | 1.00 | 1 | רגל | 0.0% |

**Hallazgos:**

1. **Hard-K nunca se activa.** Reject% = 0.0% en los 10 runs. Con la penalización de cardinalidad (w_card=0.5, K_max=20) en la función objetivo, el EM ya mantiene K_eff ≥ 26 por sí solo. El constraint era redundante.

2. **T=1.5 degrada grammar.** Grammar baja a 0.67 en 3/5 seeds (vs 1.00 típico con T=3). La temperatura baja concentra la distribución LM, dificultando que los grammar anchors se mantengan.

3. **T=2.0 comparable a T=3.** Roots media = 1.6 (vs 1.4 en estrategia A), scores similares. No hay ventaja significativa.

4. **Mismos clusters de raíces.** Las raíces שלח/לחם/מלך y עבד/עבר/דבר reaparecen, confirmando que emergen del mismo patrón de mapeo consonántico.

## 25.4 Selección del mejor candidato y MCMC

De los 30 runs totales, se filtran candidatos con K_eff ≥ 20, grammar ≥ 0.8 y score ≥ mediana. Entre estos, se selecciona el de más raíces:

**Seleccionado:** B_T2.0_s0 (estrategia B, T=2.0, seed 0)

| Propiedad | Valor |
|-----------|-------|
| Score | -36.16 |
| K_eff | 27 |
| Grammar | 1.00 |
| Quick roots | 3 (חכם, לחם, שלח) |

MCMC multi-chain (4 cadenas × 20K iteraciones, burn-in=5000, thin=10) con propose_change_hard_k:

| Métrica MCMC | Valor |
|--------------|-------|
| Best score | -36.16 |
| K_eff | 25 |
| R-hat < 1.1 | **71.1%** |
| Accept rates | 27--28% |

La convergencia MCMC (71.1%) es la mejor registrada en todos los modelos del estudio.

## 25.5 Validación: scorecard 4 PASS / 0 MARGINAL / 1 FAIL

| Test | Valor | Criterio | Resultado | Neural v1 |
|------|-------|----------|-----------|-----------|
| 1. Collapse z-score | -0.94 | z > -1.0 | **PASS** | -0.72 |
| 2. N-gram percentile | **68.0%** | >15% | **PASS** | 38.0% |
| 3. Root matching | 3 raíces | >10 raíces | **FAIL** | 1 raíz |
| 4. Cardinality ratio | 0.93 (25/27) | >0.6 | **PASS** | 0.96 |
| 5. Grammar anchors | 100% (12/12) | >60% | **PASS** | 100% |

**Veredicto: 4 PASS / 0 MARGINAL / 1 FAIL** — idéntico al neural v1.

**Cambios respecto a v1:**
- **N-gram mejora notablemente** (68% vs 38%). El candidato seleccionado usa T=2.0, que da mejor señal LM que T=3.0.
- **Roots pasan de 1 a 3**, pero siguen lejos del umbral PASS (>10).
- **Collapse empeora ligeramente** (-0.94 vs -0.72) pero sigue PASS.
- **Convergencia MCMC mejora** (71.1% vs 69.9%).

## 25.6 Tabla comparativa: 6 modelos

| Métrica | Composicional | Constrained | Homofónico | Neural v1 | Lexical | **Neural v2** |
|---------|---------------|-------------|------------|-----------|---------|---------------|
| Chars usados | ~10 | — | — | 26 | 25--27 | **25** |
| N-gram %ile | 24% | 5% | 28% | 38% | 12% | **68%** |
| Roots matched | 6 | 100 | — | 1 | 3--4 | **3** |
| Collapse z | -0.56 | -0.45 | -0.79 | -0.72 | -0.91 | **-0.94** |
| R-hat < 1.1 | 59% | 40% | 68% | 70% | 67--71% | **71%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | **4+/0±/1−** |

El neural v2 establece el nuevo récord en n-gramas (68%) y convergencia MCMC (71.1%), confirmando al neural como la mejor familia de modelos.

## 25.7 Diagnóstico: límite estructural confirmado

### La varianza del root matching es baja

La distribución de raíces a través de 30 runs es: media = 1.5, std = 1.1, max = 3. El neural v1 con 1 raíz estaba dentro de 1σ. Explorar 30 inicializaciones distintas no rompe la barrera: **el límite de ~3 raíces es estructural, no estocástico**.

### Las raíces forman clusters consonánticos

Las raíces encontradas no son léxicamente independientes. Aparecen en dos clusters que comparten consonantes:
- חכם/לחם/שלח comparten ח y ל
- עבד/עבר/דבר comparten ב y ר

Esto indica que las "raíces" emergen porque el mapping asigna ciertos glifos frecuentes a ח, ל, ב, ר, y las combinaciones resultantes coinciden con raíces reales por co-ocurrencia, no por matching léxico genuino.

### Hard-K es innecesario con la función objetivo actual

El constraint por rechazo nunca se activa (0% rejections en 10 runs). La penalización de cardinalidad en la función objetivo ya mantiene K_eff ≥ 26. Esto confirma que el diseño del scoring del Capítulo 23 era suficiente para prevenir colapso.

### T=2.0 mejora n-gramas sin sacrificar estructura

El candidato seleccionado (T=2.0) logra 68% percentil n-grámico vs 38% del neural v1 (T=3.0). La temperatura más baja concentra la distribución LM, produciendo secuencias más "naturales" en hebreo. Sin embargo, esta mejora en n-gramas no se traduce en más raíces, confirmando la independencia entre ambas métricas dentro de la zona de soluciones estables.

## 25.8 Conclusiones del Capítulo 25

1. **El límite de ~3 raíces es estructural.** 30 runs con diferentes inicializaciones y temperaturas producen max 3 raíces (media 1.5 ± 1.1). El root matching FAIL del neural no es sensible al óptimo local: es un límite del espacio de soluciones.

2. **Los scores convergen a una cuenca estable** (-36.34 ± 0.23). La función objetivo define un paisaje con múltiples mínimos locales de calidad equivalente, que difieren solo en detalles del mapping.

3. **Las raíces son artefactos de clusters consonánticos**, no señal léxica. Los dos clusters recurrentes (חכם/לחם/שלח y עבד/עבר/דבר) comparten consonantes, indicando co-ocurrencia posicional más que matching de raíces bíblicas.

4. **Hard-K es redundante** con la función objetivo actual (0% rejections). La penalización cuadrática de cardinalidad ya previene colapso.

5. **T=2.0 ofrece un compromiso interesante**: mejor n-gramas (68% vs 38%) con scorecard equivalente (4+/0±/1−). Si el root FAIL se acepta como límite estructural, T=2.0 es preferible a T=3.0.

6. **El neural v2 refuerza las conclusiones del estudio**: el root matching es el test más resistente a todos los métodos de descifrado probados, y su FAIL refleja una limitación fundamental del pipeline many-to-one sobre un manuscrito cuya estructura estadística es compatible con una lengua semítica pero cuya especificidad léxica escapa a los métodos actuales.

Notebook: `14_neural_v2.ipynb` · Resultados: `neural_v2_resultados.json`

# Capítulo 26. Mapping silábico-posicional: 3 tablas onset/nucleus/coda

## 26.1 Motivación: ¿la posición intra-silábica desbloquea el descifrado?

El modelo SilPart (d=0.445, el más cercano al Voynich entre los 11 modelos generativos del Capítulo 14) predice que el 90% de los glifos son *position-locked*: su selección depende de la posición dentro de la sílaba (onset, nucleus, coda), con superposición mínima entre posiciones (glyph_overlap=0.1, pos_bias=3.0). Sin embargo, los modelos de descifrado de los Capítulos 23--25 usan un mapping plano `{glifo → carácter}`, ignorando esta estructura posicional.

**Hipótesis:** Un mapping condicionado por posición intra-silábica ---tres tablas independientes, una por posición--- desbloquea raíces hebreas que el mapping único oscurecía, al permitir que glifos "polivalentes" mapeen a consonantes distintas según su rol silábico.

## 26.2 Diseño del modelo posicional

### Asignación de posiciones intra-silábicas

Se reutiliza la segmentación silábica por punto de transición (percentil 20) de la celda 2. Cada glifo dentro de una sílaba se asigna a una posición según reglas determinísticas:

| Longitud de sílaba | Asignación |
|---------------------|------------|
| 1 glifo | → nucleus |
| 2 glifos | → primero=onset, segundo=coda |
| 3+ glifos | → primero=onset, último=coda, medios=nucleus |

### Posiciones activas por glifo

Un glifo se considera "activo" en una posición si aparece ≥5 veces en ella (MIN_POS_FREQ=5). Si ninguna posición alcanza el umbral, se asigna la más frecuente como fallback. Esto produce:

| Categoría | Glifos | Porcentaje |
|-----------|--------|------------|
| Activos en 1 posición | 122 | **73.5%** |
| Activos en 2 posiciones | 29 | 17.5% |
| Activos en 3 posiciones | 15 | 9.0% |
| Total entradas de mapping | 225 | (vs 166 en modelo plano) |

**La premisa SilPart queda confirmada:** el 73.5% de los glifos están bloqueados a una sola posición intra-silábica, consistente con la predicción de glyph_overlap=0.1.

### PositionalGlyphMappingState

Se implementa una clase con tres tablas independientes (`mapping_onset`, `mapping_nucleus`, `mapping_coda`). La inicialización parte de las tres tablas idénticas (frequency mapping) y el EM las diverge. Las propuestas de cambio seleccionan aleatoriamente un glifo y una de sus posiciones activas.

El scoring es análogo al del Capítulo 23 (5 componentes) pero adaptado: `apply_word_positional()` consulta la tabla correspondiente a la posición de cada glifo dentro de su sílaba. El scoring incremental indexa por `(glifo, posición)` para re-evaluar solo las palabras afectadas.

## 26.3 Distribución posicional: los 15 glifos más frecuentes

Los glifos de alta frecuencia muestran distribuciones posicionales muy dispares, validando la premisa de SilPart:

| Glifo | Freq | Onset | Nucleus | Coda | Posiciones activas |
|-------|------|-------|---------|------|--------------------|
| A1 | 25,106 | 8,011 | 12,053 | 5,042 | onset/nucleus/coda |
| A2 | 17,464 | 1,528 | 2,465 | 13,471 | onset/nucleus/coda |
| A3 | 14,545 | 2,862 | 9,930 | 1,753 | onset/nucleus/coda |
| K1 | 11,066 | 4,770 | 5,182 | 1,114 | onset/nucleus/coda |
| B2 | 10,668 | 1,077 | 3,035 | 6,556 | onset/nucleus/coda |
| B1 | 10,492 | 4,992 | 5,019 | 481 | onset/nucleus/coda |
| J1 | 10,257 | 133 | 8,552 | 1,572 | coda/nucleus/onset |
| D1 | 5,425 | 5,292 | 133 | 0 | nucleus/onset |
| L1 | 4,174 | 3,280 | 892 | 2 | nucleus/onset |
| G1 | 4,162 | 4 | 325 | 3,833 | coda/nucleus |

D1 y L1 son casi exclusivamente onset (97--79%), G1 es casi exclusivamente coda (92%). Estos glifos son exactamente los "paradigmas" de prefijos y sufijos documentados por Stolfi.

## 26.4 Multi-Seed EM posicional

Se ejecutan 20 runs de EM (10 seeds × 2 temperaturas T=2.0 y T=3.0). Parámetros: SAMPLE_EM=3000 palabras, 2000 iter, patience=100, 200 propuestas/iter. Seeds 0--4: frequency + scramble, seeds 5--9: random C/V.

### Resultados por temperatura

| T | Score medio ± std | Roots medio ± std | Divergent medio ± std |
|---|-------------------|--------------------|-----------------------|
| 2.0 | -34.34 ± 0.75 | 1.8 ± 1.6 | 38.0 ± 2.5 / 44 |
| 3.0 | -34.68 ± 0.50 | 2.1 ± 1.9 | 38.5 ± 1.8 / 44 |

### Hallazgos del EM

1. **K_eff = 27 en todos los runs.** Las tres tablas juntas cubren el 100% del alfabeto hebreo.

2. **Grammar = 1.00 en 17/20 runs.** La estructura gramatical se mantiene perfectamente.

3. **Divergencia masiva: 38/44 glifos multi-posición divergen** (86.4%). El EM efectivamente diferencia las tres tablas --- los glifos que aparecen en múltiples posiciones reciben caracteres *distintos* en cada una. Las tablas no colapsan a idénticas.

4. **Roots: media 1.8--2.1, max 7.** Ligera mejora respecto al neural v2 (media 1.5 ± 1.1) pero lejos del umbral PASS de 10 raíces.

5. **Scores mejores que v2.** -34.3 a -34.7 vs -36.3 en neural v2. El espacio posicional tiene más grados de libertad (225 vs 166 entradas), lo que permite mejor ajuste a la función objetivo.

### Mejor candidato seleccionado

T=2.0, seed 1: score=-34.28, K_eff=27, grammar=1.00, roots=5, divergent=38/44.

## 26.5 MCMC multi-chain

4 cadenas × 20K iteraciones, burn-in=5000, thin=10, con propuestas posicionales:

| Métrica MCMC | Valor |
|--------------|-------|
| Best score | -34.28 |
| K_eff | 27 |
| Divergent | 38/44 |
| R-hat < 1.1 | **92.2%** |
| Accept rates | 27--29% |

La convergencia MCMC (**92.2%**) es la mejor de todos los modelos del estudio, superando ampliamente al neural v2 (71.1%). Las 4 cadenas convergen al mismo punto, indicando un óptimo robusto.

## 26.6 Validación: scorecard 4 PASS / 2 MARGINAL / 0 FAIL

| Test | Valor | Criterio | Resultado | Neural v2 |
|------|-------|----------|-----------|-----------|
| 1. Collapse z-score | -0.20 | z > -1.0 | **PASS** | -0.94 |
| 2. N-gram percentile | 14.0% | >15% | **MARGINAL** | 68.0% |
| 3. Root matching | 5 raíces | >10 raíces | **MARGINAL** | 3 raíces |
| 4. Cardinality ratio | 1.00 (27/27) | >0.6 | **PASS** | 0.93 |
| 5. Grammar anchors | 100% (12/12) | >60% | **PASS** | 100% |
| 6. Divergencia posicional | 86.4% | >20% | **PASS** | — |

**Veredicto: 4 PASS / 2 MARGINAL / 0 FAIL.**

El test 6 es nuevo y específico del modelo posicional: mide la fracción de glifos multi-posición cuyas tablas divergen. PASS > 20% indica divergencia genuina; FAIL < 5% indicaría colapso a una sola tabla (la posición no aporta). El resultado de 86.4% confirma que las tres tablas son genuinamente distintas.

### Comparación detallada con neural v2

| Métrica | Neural v2 | Syllabic | Cambio |
|---------|-----------|----------|--------|
| Collapse z | -0.94 | **-0.20** | Mejora notable |
| N-gram %ile | **68.0%** | 14.0% | Degrada severamente |
| Roots | 3 | **5** | Mejora modesta |
| K_eff | 25 | **27** | Mejora |
| R-hat < 1.1 | 71.1% | **92.2%** | Mejora notable |
| Scorecard | 4+/0±/1− | 4+/2±/0− | Trade-off |

El modelo posicional gana en collapse (-0.20, el mejor de todo el estudio), cardinalidad (27/27), convergencia (92.2%) y roots (5 vs 3). Pero pierde drásticamente en n-gramas (14% vs 68%). El scorecard cambia el FAIL de root matching por dos MARGINAL, eliminando fallos absolutos pero a costa de n-gramas.

## 26.7 Diagnóstico: divergencia posicional vs. coherencia secuencial

### La divergencia es real pero no léxica

Las tres tablas divergen en el 86.4% de los glifos multi-posición. Esto no es artefactual: el EM tiene 225 grados de libertad (vs 166 en el modelo plano) y los explota. Sin embargo, esta divergencia no produce raíces adicionales de forma significativa (5 vs 3, mejora marginal).

### El n-gram cae porque la divergencia rompe la coherencia secuencial

Un glifo que en posición onset mapea a `ב` y en coda mapea a `ל` genera secuencias de caracteres que no respetan los patrones de bigramas/trigramas del hebreo. El LSTM está entrenado sobre hebreo coherente, donde la identidad de un carácter no cambia según su posición silábica. Las tres tablas introducen discontinuidades que el LM penaliza.

### La mejora en collapse es un artefacto de la mayor libertad

El mejor collapse z-score (-0.20, frente a -0.94 en v2) se explica por los grados de libertad adicionales: con 225 entradas de mapping, el optimizador puede distribuir glifos entre grupos de collapse de forma más homogénea, no porque la estructura subyacente sea más coherente.

## 26.8 Interpretación: SilPart como mecanismo de producción vs. descifrado

Este resultado exige una distinción crucial entre dos lecturas de SilPart:

### Dirección de codificación (SilPart modela esto)

SilPart describe la **selección de glifos**: dado un carácter en posición onset, el escriba elige un glifo del pool de onset; dado el mismo carácter en posición coda, elige un glifo del pool de coda. La dirección es **muchos glifos → un carácter** (homofonía posicional). El glifo cambia, pero el significado no.

### Dirección de descifrado (nuestro notebook testa esto)

El modelo de 3 tablas testa la dirección opuesta: **un glifo → muchos caracteres** según posición (polifonía posicional). El glifo es el mismo, pero su significado cambia.

### Evidencia empírica y su lectura correcta

| Evidencia | ¿Apoya SilPart (homofonía)? | ¿Apoya 3 tablas (polifonía)? |
|-----------|-----------------------------|-----------------------------|
| 73% glifos position-locked | **Sí** — pools casi disjuntos | Neutral — compatible con ambas |
| D1 solo onset, G1 solo coda | **Sí** — glifos especializados | Neutral — no requiere polifonía |
| Neural v2 (1 tabla) n-gram=68% | **Sí** — cada glifo tiene 1 significado | No — 1 tabla basta |
| 3 tablas degradan n-gram a 14% | **Sí** — forzar polifonía rompe coherencia | **No** — la polifonía daña |
| 3 tablas divergen al 86% | Neutral | Parcial — divergen pero no mejoran roots |

**Conclusión:** Los datos apoyan la lectura de SilPart como **homofonía posicional** (muchos glifos → un carácter, con selección dependiente de posición) y descartan la lectura de **polifonía posicional** (un glifo → muchos caracteres según posición). La dependencia posicional opera en la *selección* del glifo, no en su *significado*.

Esto es análogo a las variantes posicionales del árabe, donde las formas inicial, medial y final de una letra son glifos distintos que codifican el mismo fonema. En el Voynich, D1 (onset) y G1 (coda) podrían ser "alógrafos posicionales" del mismo carácter subyacente, no caracteres distintos que cambian de significado.

## 26.9 Tabla comparativa: 7 modelos

| Métrica | Composicional | Constrained | Homofónico | Neural v1 | Lexical | Neural v2 | **Syllabic** |
|---------|---------------|-------------|------------|-----------|---------|-----------|--------------|
| Chars usados | ~10 | — | — | 26 | 25--27 | 25 | **27** |
| N-gram %ile | 24% | 5% | 28% | 38% | 12% | **68%** | 14% |
| Roots matched | 6 | 100 | — | 1 | 3--4 | 3 | **5** |
| Collapse z | -0.56 | -0.45 | -0.79 | -0.72 | -0.91 | -0.94 | **-0.20** |
| R-hat < 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | 4+/0±/1− | **4+/2±/0−** |

El modelo posicional tiene el mejor collapse, cardinalidad y convergencia MCMC del estudio, pero el peor n-gram después del constrained. El neural v2 (1 tabla) sigue dominando en la métrica más diagnóstica (realismo n-grámico).

## 26.10 Conclusiones del Capítulo 26

1. **La premisa SilPart queda confirmada empíricamente.** El 73.5% de los glifos del Voynich son position-locked (activos en una sola posición intra-silábica), consistente con la predicción del modelo generativo (glyph_overlap=0.1).

2. **La polifonía posicional se descarta.** Las tres tablas divergen (86.4%) pero la divergencia degrada los n-gramas de 68% a 14% y solo añade 2 raíces marginales (5 vs 3). El Voynich no usa mapping condicionado por posición donde un glifo signifique cosas distintas según su rol silábico.

3. **La homofonía posicional sigue viable.** SilPart como mecanismo de *producción* (muchos glifos → un carácter, con selección por posición) es compatible con todos los datos. Glifos como D1 (onset-only) y G1 (coda-only) se interpretan mejor como alógrafos posicionales del mismo carácter subyacente.

4. **El límite de ~3--5 raíces se mantiene.** Ni más parámetros (3 tablas, 225 entradas) ni S_root (Capítulo 24) superan la barrera. El root matching es una limitación estructural del espacio de soluciones, independiente del número de tablas de mapping.

5. **La mejor convergencia MCMC del estudio (92.2%)** indica que el espacio posicional tiene una cuenca de atracción más amplia y mejor definida que el plano, aunque esto no se traduce en mejor descifrado.

6. **Implicación para futuros trabajos:** un modelo de descifrado que aproveche la homofonía posicional de SilPart debería operar en la dirección inversa: identificar clusters de glifos que son variantes posicionales del mismo carácter (colapsar glifos, no expandir mappings), reduciendo el vocabulario efectivo antes de aplicar el descifrado.

Notebook: `15_syllabic_positional.ipynb` · Resultados: `syllabic_resultados.json`

# Capítulo 27. Descifrado silábico-posicional con arameo (Targum Onkelos)

## 27.1 Motivación: hebreo vs. arameo como lengua fuente

El análisis bayesiano del Capítulo 18 mostró que hebreo y arameo son los dos mejores candidatos a nivel silábico, con un gap de solo 0.27 nats (hebreo -35.64, arameo -35.91). A nivel composicional el gap se amplía a 3.87 nats, pero la validación del Capítulo 19 descartó el mapping composicional como degenerado. La pregunta pendiente es: ¿se mantiene la equivalencia hebreo/arameo cuando se aplica el modelo silábico-posicional completo (3 tablas + LSTM)?

Para responderla, se replica el Capítulo 26 sustituyendo la Torah por el **Targum Onkelos** (traducción aramea de la Torah) como corpus de lengua target.

## 27.2 Corpus arameo: Targum Onkelos

El corpus se obtiene de Sefaria (misma fuente que el hebreo), descargando los cinco libros del Pentateuco en su versión aramea:

| Parámetro | Valor |
|-----------|-------|
| Fuente | Sefaria / Targum Onkelos |
| Libros | Génesis, Éxodo, Levítico, Números, Deuteronomio |
| Palabras totales | ~82,842 |
| Subsampleado a | 37,087 (= tamaño Voynich) |
| Caracteres distintos | 27 |
| Alfabeto | Idéntico al hebreo bíblico (alefbet de 22 letras + 5 sofit) |

El alfabeto arameo es formalmente idéntico al hebreo bíblico: las mismas 27 formas gráficas. La diferencia reside en el vocabulario, la morfología verbal (paradigmas distintos) y las partículas gramaticales (arameo usa ד- como relativo donde hebreo usa ש-/אשר).

## 27.3 Neural LM arameo

El LSTM se entrena con la misma arquitectura que el hebreo (2 capas, embed=32, hidden=192, dropout=0.2, 476,991 parámetros):

| Métrica | Hebreo (Torah) | Arameo (Onkelos) |
|---------|----------------|-------------------|
| Épocas entrenadas | 30 | 30 |
| Mejor val loss | 2.004 | 2.005 |

La val loss es virtualmente idéntica (Δ = 0.001). Ambos corpora son textos legales/narrativos bíblicos con distribuciones de caracteres casi iguales; el LSTM no puede discriminar entre ellos a nivel de modelo de lenguaje.

## 27.4 EM multi-seed

Se ejecutan 20 runs (10 seeds × 2 temperaturas: T=2.0, T=3.0), con la misma configuración que el Capítulo 26:

| Métrica | Hebreo (Cap. 26) | Arameo |
|---------|------------------|--------|
| Score medio (T=2.0) | -34.48 ± 0.47 | -34.99 ± 0.61 |
| Score medio (T=3.0) | -34.68 ± 0.50 | -35.10 ± 0.56 |
| Roots medio | 1.9 | 1.8 |
| Roots max | 7 | 5 |
| K_eff | 27 (todos) | 27 (todos) |
| Grammar = 1.00 | 17/20 | 18/20 |

Los scores arameos son ~0.5 puntos peores que los hebreos, consistente con el gap bayesiano del Capítulo 18. La distribución de raíces es estadísticamente indistinguible (media 1.8 vs 1.9).

### Mejor candidato

T=2.0, seed 7: score=-34.89, K_eff=27, grammar=1.00, roots=5 {ברך, גבר, עבד, עבר, רבב}, divergent=37/44.

## 27.5 MCMC y convergencia

| Métrica MCMC | Hebreo | Arameo |
|--------------|--------|--------|
| Best score | -34.28 | -34.89 |
| K_eff | 27 | 27 |
| Divergent | 38/44 | 37/44 |
| R-hat < 1.1 | **92.2%** | **90.4%** |
| Accept rates | 27--29% | 28--28% |

La convergencia aramea (90.4%) es ligeramente inferior a la hebrea (92.2%) pero sigue siendo la segunda mejor del estudio, muy por encima del neural v2 plano (71.1%).

## 27.6 Validación: scorecard 4 PASS / 2 MARGINAL / 0 FAIL

| Test | Hebreo | Arameo | Δ |
|------|--------|--------|---|
| 1. Collapse z-score | PASS (-0.20) | PASS (-0.35) | -0.15 |
| 2. N-gram percentile | MARGINAL (14.0%) | MARGINAL (6.0%) | -8.0 pp |
| 3. Root matching | MARGINAL (5 raíces) | MARGINAL (5 raíces) | = |
| 4. Cardinality ratio | PASS (1.00) | PASS (1.00) | = |
| 5. Grammar anchors | PASS (100%) | PASS (100%) | = |
| 6. Divergencia posicional | PASS (86.4%) | PASS (84.1%) | -2.3 pp |

**Veredicto: 4 PASS / 2 MARGINAL / 0 FAIL** — idéntico al hebreo test por test.

### Análisis de las diferencias

La única diferencia cuantitativamente notable es el **n-gram percentile**: 6% arameo vs 14% hebreo (ambos MARGINAL). Los trigramas del Targum Onkelos ajustan peor que los de la Torah al corpus Voynich mapeado, pero la diferencia no alcanza para cambiar veredictos. Las raíces encontradas son las mismas 5 en ambos casos: ברך, עבד y עבר aparecen en ambos, mientras que las dos restantes difieren (hebreo: דרך, מלך; arameo: גבר, רבב). Todas pertenecen al vocabulario bíblico compartido.

## 27.7 Raíces compartidas: señal bíblica genérica, no específica de lengua

Las raíces encontradas por ambos modelos pertenecen al léxico más básico del texto bíblico:

| Raíz | Significado | ¿Compartida? |
|------|-------------|--------------|
| ברך | bendecir | Sí |
| עבד | servir/trabajar | Sí |
| עבר | cruzar/pasar | Sí |
| מלך | reinar | Solo hebreo |
| דרך | camino | Solo hebreo |
| גבר | ser fuerte | Solo arameo |
| רבב | ser muchos | Solo arameo |

Todas son raíces de alta frecuencia en ambos corpora. Su aparición refleja el vocabulario bíblico compartido entre Torah y Targum (que es una traducción casi literal), no una señal discriminatoria entre lenguas.

## 27.8 Tabla comparativa: 8 modelos

| Métrica | Composic. | Constr. | Homof. | Neural v1 | Lexical | Neural v2 | Syl-Heb | **Syl-Ara** |
|---------|-----------|---------|--------|-----------|---------|-----------|---------|-------------|
| Chars usados | ~10 | — | — | 26 | 25--27 | 25 | 27 | **27** |
| N-gram %ile | 24% | 5% | 28% | 38% | 12% | **68%** | 14% | 6% |
| Roots | 6 | 100 | — | 1 | 3--4 | 3 | 5 | **5** |
| Collapse z | -0.56 | -0.45 | -0.79 | -0.72 | -0.91 | -0.94 | **-0.20** | -0.35 |
| R-hat < 1.1 | 59% | 40% | 68% | 70% | 67--71% | 71% | **92%** | 90% |
| Scorecard | 1+/1±/3− | — | 2+/2±/2− | 4+/0±/1− | 2--3+/1--2±/1− | 4+/0±/1− | 4+/2±/0− | **4+/2±/0−** |

## 27.9 Conclusiones del Capítulo 27

1. **Hebreo y arameo son indistinguibles con el modelo silábico-posicional.** El scorecard es idéntico (4+/2±/0−), las métricas difieren en menos de 1σ, y las raíces encontradas provienen del léxico bíblico compartido. Esto confirma y extiende la conclusión del bayesiano silábico (Capítulo 18): el gap de 0.27 nats no es operativamente significativo.

2. **El n-gram arameo (6%) es peor que el hebreo (14%), pero ambos son MARGINAL.** La degradación se explica por diferencias en frecuencias trigramáticas entre Torah y Targum, no por una incompatibilidad fundamental. Los paradigmas verbales arameos (pa'el, af'el, itpa'al) generan transiciones de caracteres ligeramente distintas a los hebreos (pi'el, hif'il, hitpa'el).

3. **La equivalencia es esperable y constituye un resultado positivo.** Torah y Targum Onkelos comparten: (a) alfabeto idéntico (27 formas), (b) morfología trilítera consonántica, (c) vocabulario bíblico (~70% de raíces compartidas), (d) estructura sintáctica similar (el Targum es traducción casi literal). Cualquier método de descifrado basado en modelo de lenguaje será incapaz de discriminar entre ambas como lengua fuente.

4. **Implicación para la hipótesis semítica.** Si el Voynich codifica una lengua semítica noroccidental, la distinción "hebreo vs. arameo" es probablemente anacrónica para el manuscrito. El continuum hebreo-arameo bíblico (siglos V a.C.--II d.C.) comparte demasiada estructura para ser separable por métodos estadísticos de descifrado. La hipótesis correcta sería "semítico noroccidental bíblico" como categoría única.

5. **El límite de ~3--5 raíces se mantiene en ambas lenguas.** Ni el cambio de corpus target ni los 225 grados de libertad posicionales superan la barrera. El root matching es una limitación estructural del espacio de soluciones, confirmando el diagnóstico del Capítulo 25 (neural v2).

Notebook: `16_syllabic_aramaic.ipynb` · Resultados: `syllabic_arameo_resultados.json`

# Capítulo 28. Colapso de alógrafos posicionales

## 28.1 Motivación: de la homofonía posicional al descifrado

---

Continued in Part X.
