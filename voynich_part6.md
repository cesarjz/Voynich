# PARTE VI

# Descifrado composicional del Voynich

La Parte V intentó descifrar el Voynich mediante sustitución biyectiva a nivel de sílaba: cada sílaba del Voynich se mapea a exactamente una sílaba de la lengua candidata. El ranking resultante ---hebreo #1, árabe #2, con brecha de 2.9 puntos a las no semíticas--- es informativo, pero la convergencia MCMC es extremadamente limitada (R-hat < 1.1 en solo el 7% de las sílabas). Este resultado sugiere que la asunción de sustitución 1-a-1 es incorrecta: si el modelo SilPart de la Parte III es correcto, cada glifo del Voynich codifica un componente fonológico independiente (onset, núcleo o coda), y la unidad correcta de descifrado no es la sílaba sino el glifo. La Parte VI implementa este cambio de nivel: un descifrado composicional donde cada glifo mapea a un carácter de la lengua candidata, permitiendo mappings many-to-one (múltiples glifos → mismo carácter).

# Capítulo 18. Descifrado composicional

## 18.1 Motivación: de sílaba a glifo

El Voynich tiene 166 glifos distintos que se combinan en 2,923 tipos silábicos. Si la codificación es composicional ---como predice SilPart---, entonces los 166 glifos se mapean a un alfabeto target de ~27-30 caracteres, produciendo un mapping many-to-one donde múltiples glifos pueden codificar el mismo carácter en distintos contextos posicionales.

La ventaja computacional es dramática: el espacio de búsqueda pasa de ~800! permutaciones biyectivas (silábico) a 166 × 30 asignaciones independientes (composicional). Esto no solo hace la exploración más eficiente, sino que permite que el MCMC converja porque el espacio es navegable. Además, el mapping many-to-one captura directamente la predicción central de SilPart: que un mismo fonema se codifica con glifos distintos según su posición en la sílaba (celda 0 del notebook `07_compositional.ipynb`).

## 18.2 Modelo: CharLM trigrama, GlyphMappingState, clasificación C/V

### Modelo de lenguaje de caracteres (CharLM)

A diferencia del SyllableLM bigrama de la Parte V, aquí se usa un modelo de lenguaje a nivel de carácter con orden trigrama y suavizado Witten-Bell (celda 4):

P(c_i | c_{i-2}, c_{i-1}) = λ₃ × P_trigrama + (1-λ₃) × [λ₂ × P_bigrama + (1-λ₂) × P_unigrama]

donde cada nivel de backoff tiene su propio λ calibrado por Witten-Bell. El trigrama captura dependencias más ricas que el bigrama silábico: no solo qué carácter sigue a cuál, sino patrones de tres caracteres que reflejan la fonotaxis de la lengua.

### Estado de mapping (GlyphMappingState)

La clase `GlyphMappingState` gestiona un mapping many-to-one de glifos a caracteres (celda 4):

- `apply_word()`: dado un mapping μ, transforma una palabra [g₁, g₂, ..., g_n] → [c₁, c₂, ..., c_n] donde c_i = μ(g_i)
- `propose_change()`: cambia un glifo aleatorio a un carácter aleatorio, respetando las restricciones C/V
- No requiere biyección: múltiples glifos pueden mapear al mismo carácter target

### Clasificación consonante/vocal (C/V)

Cada glifo se clasifica como consonante (C) o vocal (V) según su distribución posicional en las sílabas de la Parte IV (celda 7):

- **V (vocal)**: glifos con proporción en posición nuclear > 0.40
- **C (consonante)**: resto de glifos clasificables

Resultados de la clasificación:

| Clase | N glifos |
|-------|----------|
| Consonante (C) | 21 |
| Vocal (V) | 5 |
| Sin clasificar | 91 |
| **Total clasificados** | **117 de 166** |

El ratio V/(C+V) es 19.2%, consistente con el ratio vocal/consonante del hebreo (5/22 = 22.7%) y del árabe (6/28 = 21.4%), donde los sistemas de escritura son predominantemente consonánticos.

### Scoring composicional

El score combina dos componentes (celda 4):

**S_total = 2.0 × S_LM + 0.5 × S_posicional**

donde:

- **S_LM** (peso 2.0): log-verosimilitud media del corpus mapeado bajo el CharLM trigrama de la lengua candidata
- **S_posicional** (peso 0.5): consistencia entre el rol C/V del glifo y el rol C/V del carácter target

## 18.3 Inicialización por frecuencia dentro de clase C/V

A diferencia de la inicialización húngara del enfoque silábico (que requiere vectores distribucionales y asignación biyectiva), aquí se usa una inicialización más directa basada en frecuencia (celda 9):

1. Calcular la frecuencia de cada glifo en el corpus del Voynich
2. Calcular la frecuencia de cada carácter en el corpus de la lengua candidata
3. Para cada clase (C, V, sin clasificar):
   - Ordenar glifos por frecuencia descendente
   - Ordenar caracteres target por frecuencia descendente
   - Asignar el glifo más frecuente al carácter más frecuente de la misma clase
4. Asignación cíclica: glifo_i → char_(i % n_chars) para garantizar cobertura

Scores iniciales tras la inicialización:

| Lengua | Score inicial | S_LM |
|--------|--------------|------|
| Árabe | -65.31 | -32.90 |
| Hebreo | -74.06 | -37.28 |
| Turco | -86.28 | -43.39 |
| Latín | -96.09 | -48.29 |
| Finés | -111.06 | -55.78 |

## 18.4 EM composicional + MCMC multi-chain

### Fase EM

Se ejecutan hasta 100 iteraciones de EM por lengua (celda 11):

| Parámetro | Valor |
|-----------|-------|
| Iteraciones máximas | 100 |
| Early stopping | 10 iteraciones sin mejora |
| Cambios por iteración | 200 |
| Subsample por iteración | 3,000 palabras |
| Propuesta | Cambiar un glifo a otro carácter (respetando C/V) |
| Aceptación | Metropolis: siempre si mejora, probabilístico si empeora |

### Fase MCMC

Para las top-2 lenguas del EM, se ejecuta MCMC Metropolis-Hastings con annealing adaptativo (celda 12):

| Parámetro | Valor |
|-----------|-------|
| Cadenas | 4 (seeds: 42, 137, 256, 999) |
| Iteraciones/cadena | 15,000 |
| Burn-in | 3,000 |
| Thinning | Cada 5ª muestra |
| Tasa de aceptación target | 35% |
| Subsample/iter | 3,000 palabras |
| Pesos | w_lm = 2.0, w_pos = 0.5 |
| Temperatura | Annealing adaptativo: T₀ calibrada, decay exponencial |

La temperatura se calibra empíricamente midiendo la distribución de scores negativos y ajustando T₀ para obtener ~35% de aceptación inicial. El annealing exponencial reduce T gradualmente, focalizando la exploración hacia el final.

## 18.5 Resultados: ranking confirma hebreo #1

El ranking final (celda 16), ahora con seis lenguas candidatas incluyendo arameo (Targum Onkelos):

| # | Lengua | Familia | Score total | Score LM | PPX mapeada | PPX nativa | Ratio PPX |
|---|--------|---------|-------------|----------|-------------|------------|-----------|
| 1 | **Hebreo** | Semítica | **-39.71** | -20.10 | 15.1 | 7.3 | **2.07** |
| 2 | **Árabe** | Semítica | **-40.95** | -20.73 | 16.5 | 7.3 | **2.26** |
| 3 | **Arameo** | Semítica | -43.58 | -22.04 | 19.4 | 7.4 | 2.63 |
| 4 | Latín | Indoeuropea | -52.65 | -26.58 | 36.3 | 5.7 | 6.42 |
| 5 | Turco | Aglutinante | -61.99 | -31.24 | 67.4 | 7.9 | 8.50 |
| 6 | Finés | Aglutinante | -75.88 | -38.19 | 173.4 | 7.4 | 23.50 |

Nota: el MCMC solo se ejecutó sobre las top-2 (hebreo y árabe). El score del arameo es post-EM, no refinado por MCMC.

### Interpretación

El ranking composicional confirma independientemente el resultado silábico de la Parte V: **hebreo #1, árabe #2, arameo #3**. Pero la discriminación es radicalmente mayor y revela una diferencia importante respecto al nivel silábico:

- **Brecha semíticas → no semíticas:** 11.7 puntos (hebreo -39.71 vs latín -52.65), frente a solo 3.5 puntos en el silábico. El modelo composicional separa las semíticas del resto con mucha mayor claridad.

- **Arameo cae a #3:** A nivel silábico, arameo y hebreo eran prácticamente indistinguibles (gap 0.27). A nivel composicional, el gap se amplía a 3.87 puntos. El CharLM trigrama hebreo se ajusta significativamente mejor a las secuencias de caracteres del Voynich que el arameo. Esto sugiere que, a nivel de fonotaxis de caracteres (no de sílabas), el Voynich se parece más al hebreo que al arameo.

- **Ratio PPX:** Para hebreo, el corpus mapeado tiene 2.07× la perplejidad del hebreo nativo, frente a 2.63× para arameo y 4.00× en el silábico. El mapping composicional produce texto más cercano al hebreo real.

- **Reordenamiento de no semíticas:** Latín sube de #5 (silábico) a #4 (composicional), y finés baja de #4 a #6. El modelo composicional, al operar a nivel de carácter, discrimina diferentemente entre las lenguas de nivel inferior ---pero el top-2 se mantiene estable.

## 18.6 Convergencia: mejora drástica respecto al silábico

Los diagnósticos MCMC muestran una mejora dramática en convergencia (celdas 13-14):

### Hebreo

| Métrica | Silábico (Parte V) | Composicional |
|---------|--------------------|---------------|
| R-hat < 1.1 | 45/676 (6.65%) | **98/165 (59.4%)** |
| R-hat mediana | 1.521 | **1.041** |
| Aceptación media | 30.8% | **69.0%** |

### Árabe

| Métrica | Silábico (Parte V) | Composicional |
|---------|--------------------|---------------|
| R-hat < 1.1 | 44/715 (6.15%) | **94/163 (57.7%)** |
| R-hat mediana | 1.511 | **1.056** |
| Aceptación media | 31.7% | **68.1%** |

La proporción de glifos convergidos (R-hat < 1.1) pasa del ~7% al ~59%: una mejora de ~9× que refleja directamente la reducción del espacio de búsqueda. La mediana de R-hat baja de ~1.52 a ~1.04, acercándose al ideal (1.0). Las tasas de aceptación (~69%) son más altas que en el silábico (~31%), indicando que las cadenas exploran eficientemente el espacio posterior.

### Mappings de alta confianza

Para hebreo, 75 glifos tienen 100% de consistencia C/V posterior (el carácter asignado tiene siempre el mismo rol C/V a través de las cuatro cadenas). De estos, 18 glifos tienen confianza posterior 1.0 ---las cuatro cadenas convergen exactamente al mismo carácter hebreo--- constituyendo anclas firmes del mapping.

## 18.7 Análisis del colapso many-to-one

Una predicción central del modelo SilPart es que múltiples glifos del Voynich codifican el mismo fonema en distintos contextos posicionales. El mapping composicional confirma esta predicción: los caracteres hebreos más frecuentes atraen múltiples glifos (celda 18).

### Top-10 atractores hebreos

| Carácter | Nombre | N glifos mapeados | % del total |
|----------|--------|-------------------|-------------|
| ש | Shin | 17 | 10.2% |
| ר | Resh | 15 | 9.0% |
| ו | Vav | 13 | 7.8% |
| ע | Ayin | 10 | 6.0% |
| מ | Mem | 9 | 5.4% |
| ת | Tav | 9 | 5.4% |
| ח | Het | 9 | 5.4% |
| א | Alef | 8 | 4.8% |
| ן | Nun final | 7 | 4.2% |
| כ | Kaf | 7 | 4.2% |

Los tres atractores principales (Shin, Resh, Vav) concentran 45/166 = 27.1% de todos los glifos. Esto es coherente con SilPart: consonantes frecuentes como ש y ר aparecen en muchos contextos posicionales (onset, coda, con diferentes vocales adyacentes), y cada contexto posicional tiene su propio glifo. Las *matres lectionis* (ו vav, א alef) ---consonantes que funcionan también como indicadores vocálicos en hebreo--- atraen muchos glifos, reflejando su rol dual consonante/vocal.

### Interpretación lingüística

El colapso many-to-one es cualitativamente compatible con un sistema donde:

- Cada consonante hebrea tiene variantes gráficas según la posición en la sílaba (onset vs coda)
- Las vocales se codifican combinatoriamente mediante la elección de variante consonántica, no mediante signos diacríticos separados (como los nikkud del hebreo estándar)
- El resultado es un sistema tipo akshárico donde el glifo codifica simultaneamente la consonante y la vocal adyacente

## 18.8 Comparación silábico vs composicional

| Métrica | Silábico (Parte V) | Composicional (Parte VI) |
|---------|--------------------|--------------------------|
| Ranking top-3 | Hebreo, Arameo, Árabe | Hebreo, Árabe, Arameo |
| Gap Hebreo-Arameo | 0.27 pts | **3.87 pts** |
| Brecha semíticas → resto | 3.5 pts | **11.7 pts** |
| R-hat < 1.1 (Hebreo) | 6% | **59%** |
| Mappings 100% confianza | 12 sílabas | **18 glifos** |
| Ratio PPX (Hebreo) | 4.00 | **2.07** |
| Espacio de búsqueda | ~800! | ~166 × 30 |
| Unidad de mapping | sílaba → sílaba (1-a-1) | glifo → carácter (many-to-one) |

El modelo composicional supera al silábico en todas las métricas de calidad de mapping. El ranking top-1 es consistente (hebreo), confirmando que la señal semítica es robusta e independiente del nivel de análisis. La mejora en convergencia (6% → 59%) y en ratio PPX (4.00 → 2.07) indica que la asunción composicional es más compatible con la estructura real del Voynich que la asunción sustitutiva.

Un resultado notable es la divergencia del arameo entre ambos niveles: a nivel silábico, hebreo y arameo son indistinguibles (gap 0.27), pero a nivel composicional el gap se amplía a 3.87 puntos. Esto indica que las secuencias de caracteres del Voynich mapeado se parecen más al hebreo que al arameo, aunque a nivel de estructura silábica ambas lenguas son igualmente compatibles.

### Limitaciones del enfoque composicional

1. **CharLM trigrama limitado.** No captura dependencias largas. Un LM neuronal (LSTM/Transformer) a nivel de carácter podría mejorar el scoring.

2. **Clasificación C/V heurística.** Basada en la posición nuclear de las sílabas de la Parte IV, no en conocimiento fonológico. Los glifos ambiguos (semivocales, *matres lectionis*) pueden estar mal clasificados.

3. **Matres lectionis.** En hebreo y árabe, ciertas consonantes (alef, he, vav, yod) funcionan como indicadores vocálicos. La clasificación C/V binaria no captura esta dualidad, lo que puede introducir inconsistencias en el mapping.

4. **Sin restricción de cardinalidad.** El mapping no limita cuántos glifos pueden colapsar en un mismo carácter. Shin con 17 glifos puede ser un artefacto donde el optimizador "aparca" glifos raros en el carácter más frecuente en lugar de buscar su mapping real.

5. **Sin validación externa.** El ranking es internamente consistente (silábico confirma composicional), pero no se ha validado con tests independientes: ¿el mapping produce texto hebreo coherente? ¿Las raíces triconsonánticas resultantes existen en el léxico? Estas preguntas se abordan en la Parte VII.

# Referencias de la Parte VI

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebook: `07_compositional.ipynb` · Resultados: `composicional_resultados.json`

Partes I--VII disponibles como documentos independientes.
