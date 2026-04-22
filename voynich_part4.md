# PARTE IV

# Del forward modeling al descifrado: segmentación silábica del Voynich

La Parte III estableció, mediante once modelos generativos, que el modelo SilPart (silabario probabilístico con partición de glifos, d=0.445) es el que mejor reproduce la huella estadística del Voynich. Este resultado identifica el *tipo* de sistema, pero no dice cómo leerlo. La Parte IV da el siguiente paso: bajo la hipótesis silábica, segmentar las palabras del Voynich en sílabas, clasificarlas funcionalmente, detectar patrones morfológicos internos y validar los resultados contra lenguas aglutinantes reales. El análisis implementa las cuatro primeras fases computacionales del descifrado silábico.

# Capítulo 16. Segmentación y análisis silábico

## 16.1 Fase 1: Segmentación silábica

### Método

Se implementan dos métodos complementarios de segmentación, ambos operando sobre la matriz de transición intra-palabra (que cuenta solo bigramas dentro de cada palabra, sin cruzar fronteras):

**Método A — Probabilidad de transición (TP).** Marca una frontera silábica donde P(g_{i+1} | g_i) cae por debajo de un percentil del corpus. Inspirado en Saffran et al. (1996), que demostró que los humanos usan caídas de probabilidad transicional para segmentar habla continua en palabras. Aquí se adapta el principio a fronteras de sílaba dentro de palabras. Se evalúan tres umbrales: percentiles 10, 20 y 30.

**Método B — Entropía forward.** Marca una frontera donde la entropía H(g_{i+1} | g_i) es alta ---es decir, donde el glifo actual tiene muchos sucesores posibles con probabilidad similar. Inspirado en Harris (1955), que propuso que los puntos de máxima incertidumbre en una secuencia corresponden a fronteras morfológicas. Se evalúan tres umbrales: top 60%, 70% y 80% de la distribución de entropías.

### Resultados del sweep de parámetros

| Método | Parámetro | Tipos silábicos | Syl/word |
|--------|-----------|----------------|----------|
| A (TP) | P10 | 5,511 | 1.32 |
| A (TP) | P20 | 2,923 | 1.64 |
| A (TP) | P30 | 1,473 | 1.97 |
| B (Entropía) | Top-60% | 462 | 3.66 |
| B (Entropía) | Top-70% | 623 | 3.51 |
| B (Entropía) | Top-80% | 996 | 3.29 |

Los dos métodos capturan niveles de estructura diferentes. El método A produce sílabas más largas y menos numerosas por palabra (1.64 syl/word con P20): segmenta en unidades tipo morfema, agrupando raíz y afijos en bloques. El método B produce sílabas más cortas y abundantes (3.51 syl/word con Top-70%): segmenta más finamente, en unidades más cercanas a sílabas fonológicas.

Se selecciona el **Método A con P20 como canónico**, produciendo un inventario de 2,923 tipos silábicos.

### Interpretación del inventario

El número bruto de 2,923 tipos es muy superior a cualquier silabario conocido (kana=46, Linear B=87, Cherokee=85). Sin embargo, la distribución de frecuencias es extremadamente concentrada:

- **40 tipos** cubren el 50% de los tokens
- **201 tipos** cubren el 80%
- **794 tipos** cubren el 95%

El *núcleo funcional* del inventario tiene ~200 sílabas, comparable a un sistema akshárico (devanagari ~300+). Los ~2,100 tipos restantes son combinaciones raras o hapax legomena ---exactamente lo esperado en una lengua aglutinante donde raíces poco frecuentes generan combinaciones únicas. La distribución Zipf de las sílabas sigue una ley de potencia con pendiente α=-1.47, consistente con unidades lingüísticas reales.

### Acuerdo entre métodos

La correlación Spearman entre el número de fronteras por palabra de ambos métodos es ρ=0.228 (p≈0), con un acuerdo exacto del 13.6%. Esta divergencia no es un fallo: refleja que capturan niveles distintos de estructura. Sin embargo, 23 de las 50 sílabas más frecuentes de cada método coinciden, indicando que el núcleo del inventario es robusto.

Los 10 tipos más frecuentes del inventario canónico son:

| Rango | Sílaba | Freq | % |
|-------|--------|------|---|
| 1 | A2 | 2,027 | 3.3% |
| 2 | K1 | 2,010 | 3.3% |
| 3 | B1-A2 | 1,933 | 3.2% |
| 4 | A1 | 1,885 | 3.1% |
| 5 | C2 | 1,556 | 2.6% |
| 6 | B1 | 1,528 | 2.5% |
| 7 | A1-B2 | 1,269 | 2.1% |
| 8 | B1-A3-G1 | 1,047 | 1.7% |
| 9 | B3 | 957 | 1.6% |
| 10 | L1 | 892 | 1.5% |

![Figura 16.1. Distribución Zipf y comparativa de inventarios silábicos. silabas_zipf_inventario.png)

*Figura 16.1. Panel superior: distribución Zipf para los tres umbrales de cada método. Panel inferior izquierdo: distribución de longitudes silábicas. Panel inferior derecho: tabla comparativa con silabarios reales.*

## 16.2 Fase 2: Clasificación funcional de sílabas

### Método

Cada tipo silábico con frecuencia ≥ 5 se clasifica según su distribución posicional dentro de la palabra:

- **Onset** (prefijo): ratio de aparición en posición inicial ≥ 0.60, con ratio final < 0.30
- **Coda** (sufijo): ratio de aparición en posición final ≥ 0.60, con ratio inicial < 0.30
- **Nuclear** (raíz): ratio de aparición en posición media ≥ 0.40
- **Free**: sin preferencia posicional dominante

### Resultados

De los 2,923 tipos del inventario, 792 superan el umbral de frecuencia mínima (5 tokens) y reciben clasificación:

| Clase | Tipos | Tokens | Interpretación |
|-------|-------|--------|----------------|
| Onset | 171 | 14,368 | Prefijos silábicos |
| Nuclear | 54 | 3,781 | Raíces |
| Coda | 90 | 12,555 | Sufijos silábicos |
| Free | 477 | 27,099 | Sin preferencia posicional |

La categoría *free* domina en tipos (477), lo cual es esperable: muchas combinaciones no muestran preferencia posicional clara, especialmente las que aparecen en palabras de una o dos sílabas donde las posiciones inicio/final se confunden.

### Validación: conexión glifo → sílaba

Si la segmentación es correcta, las sílabas onset deberían empezar con glifos-prefijo conocidos (D1, K1, L1) y las codas deberían terminar con glifos-sufijo conocidos (G1, A2, C1). Los resultados confirman esta predicción parcialmente:

| Clase | Criterio | Coincidencia | Glifo dominante |
|-------|----------|-------------|-----------------|
| Coda | Termina en glifo-sufijo | **64.4%** (58/90) | A2 (41 tipos) |
| Nuclear | Contiene glifo-núcleo | 31.5% (17/54) | A3 (13 tipos) |
| Onset | Empieza con glifo-prefijo | 26.3% (45/171) | A1 (40 tipos) |

La conexión es más fuerte para las codas: el 64.4% termina en glifos-sufijo, con A2 dominando abrumadoramente. Esto es coherente con el conocimiento previo de que A2 aparece en posición final en el 83.8% de sus ocurrencias. Del lado onset, aunque el porcentaje global es menor (26.3%), los casos individuales son contundentes: el tipo D1-A1 aparece en posición inicial en el 98.6% de sus ocurrencias, K1 en el 89.4%, y D1-A1-Q1 en el 98.8%.

El heatmap de clase × sección muestra proporciones estables de onset/nuclear/coda entre secciones temáticas, sugiriendo que la estructura morfológica es compartida entre las secciones del manuscrito ---las diferencias temáticas residen en el léxico (qué raíces se usan), no en la gramática (cómo se construyen las palabras).

![Figura 16.2. Distribución Zipf por clase funcional. silabas_zipf_por_clase.png)

*Figura 16.2. Distribución Zipf para cada clase funcional. Las cuatro clases siguen leyes de potencia con pendientes distintas, consistente con distribuciones lingüísticas reales.*

![Figura 16.3. Proporción de clase silábica por sección. silabas_clase_por_seccion.png)

*Figura 16.3. Heatmap de proporciones de clase silábica por sección temática. La estructura morfológica es compartida entre secciones.*

## 16.3 Fase 3: Patrones morfológicos

### 16.3.1 Armonía vocálica

Si el Voynich tiene restricciones fonológicas internas análogas a la armonía vocálica del turco o el finés, debería existir una asociación preferente entre sílabas nucleares y codas del mismo word. Para testarlo, se extraen todos los pares (nuclear, coda) co-ocurrentes dentro de cada palabra, se construye una tabla de contingencia top-20 × top-20 y se aplica un test chi-cuadrado con validación por permutación (500 shuffles de codas entre palabras).

**Resultados:**

| Estadístico | Valor |
|-------------|-------|
| Pares analizados | 2,062 |
| χ² observado | 3,170.7 |
| p-value (χ²) | ≈ 0 |
| p-value (permutación) | 0.000 (0/500 shuffles ≥ observado) |
| V de Cramér | 0.284 |

La asociación nuclear-coda es altamente significativa: ninguna de las 500 permutaciones produce un χ² comparable al observado. La V de Cramér de 0.284 indica un efecto medio ---no tan fuerte como la armonía vocálica turca completa, pero claramente no aleatorio. Esto sugiere restricciones internas sobre qué sufijos pueden seguir a qué raíces, compatible con armonía vocálica parcial, restricciones fonotácticas u otro tipo de dependencia morfofonológica.

![Figura 16.4. Tabla de contingencia nuclear × coda. armonia_nuclear_coda.png)

*Figura 16.4. Heatmap de la tabla de contingencia entre las 15 sílabas nucleares y las 15 sílabas coda más frecuentes. Los picos de co-ocurrencia (celdas oscuras) indican asociaciones preferentes que no se explican por las frecuencias marginales.*

### 16.3.2 Paradigmas de sufijo

Para cada raíz nuclear con frecuencia ≥ 10, se catalogan todos los sufijos coda co-ocurrentes (frecuencia ≥ 5). La regularidad se mide por el índice de Gini medio (1.0 = un solo sufijo dominante, 0.0 = equiprobable).

**Resultados:**

| Métrica | Valor |
|---------|-------|
| Paradigmas encontrados | 27 |
| Tamaño medio de paradigma | 3.4 sufijos |
| Tamaño máximo | 8 sufijos |
| Regularidad media (Gini) | 0.490 |

El Gini de 0.49 está a medio camino: ni completamente regular (un solo sufijo por raíz) ni equiprobable. Esto es consistente con un sistema aglutinante donde unas pocas terminaciones son muy frecuentes pero hay variedad real.

Las tres raíces más productivas son:

| Raíz | N sufijos | Total tokens | Sufijo dominante |
|------|-----------|-------------|-----------------|
| Q1 | 8 | 290 | A2 (70.3%) |
| K2 | 8 | 214 | C2 (47.7%) |
| Q2 | 6 | 128 | A2 (75.0%) |

La raíz Q1 ---que coincide con uno de los glifos-núcleo más frecuentes del Voynich--- admite 8 sufijos distintos, con A2 como terminación dominante (204/290 = 70.3%). Esto es análogo a una raíz nominal turca que admite múltiples sufijos de caso pero con el nominativo (sin sufijo / sufijo nulo) como forma base.

![Figura 16.5. Grafo bipartito raíz → sufijos. paradigmas_sufijos_grafo.png)

*Figura 16.5. Red bipartita de las 20 raíces más productivas (verde) y sus sufijos coda (amarillo). El grosor de las aristas es proporcional a la frecuencia de co-ocurrencia.*

### 16.3.3 Vocabulario por sección

La especificidad de sílabas nucleares por sección se mide como freq_in_section / (freq_in_section + mean_freq_otras). Si el Voynich tiene contenido temático real, las secciones deberían mostrar sílabas-raíz específicas.

Los resultados muestran vocabulario nuclear diferenciado: la sección biológica tiene sílabas específicas como Q2 (especificidad=0.617) y Ba (0.613), mientras la sección farmacéutica tiene Z1 (0.814) y J1-A1 (0.769). Cada sección presenta un perfil nuclear distinto, coherente con contenido temático.

### 16.3.4 Divergencia entre secciones

La divergencia Jensen-Shannon (JSD) media entre secciones a nivel silábico es **0.204**, inferior a la JSD a nivel de glifo (0.301). El ratio silábico/glifo es 0.68×.

Este resultado ---contraintuitivo a primera vista--- tiene una interpretación coherente: al agrupar glifos en sílabas, se absorbe variación glifo-a-glifo que era "ruido posicional" y la distribución silábica se homogeneiza parcialmente. Las secciones comparten más vocabulario silábico que vocabulario de glifos individuales. Esto no contradice la hipótesis de contenido temático: la variación entre secciones reside en qué raíces nucleares se usan (léxico), pero la morfología (onset + coda) es compartida. De hecho, este patrón es exactamente lo esperado en una lengua real: la gramática es universal dentro del texto, la variación es léxica.

![Figura 16.6. JSD entre secciones a nivel silábico. jsd_secciones_silabico.png)

*Figura 16.6. Heatmap de JSD par a par entre secciones temáticas a nivel silábico.*

## 16.4 Fase 4: Comparación interlingüística

### Método

Se aplica la misma segmentación TP con P20 a corpora de caracteres del turco (Leipzig Wikipedia, subsampled a 37,087 palabras) y finés (Kalevala, subsampled a 37,087 palabras), tratando cada carácter como un "glifo" para obtener métricas comparables.

### Métricas silábicas comparativas

| Lengua | Tipos | Syl/word | Zipf α | Distancia al Voynich |
|--------|-------|----------|--------|---------------------|
| Voynich | 2,923 | 1.64 | -1.47 | — |
| Turco | 8,328 | 2.05 | -1.14 | 1.060 |
| Finés | 7,173 | 2.11 | -1.21 | 0.995 |

El Voynich tiene menos tipos y menos sílabas/palabra que ambas lenguas, pero la pendiente Zipf es más empinada (-1.47 vs. -1.14/-1.21), indicando una distribución más concentrada en pocas sílabas dominantes. La distancia silábica es comparable para ambas lenguas, con finés ligeramente más cercano (0.995 vs. 1.060).

La diferencia en número de tipos (2,923 vs. 7,000-8,000) refleja que el Voynich usa 166 glifos base frente a los 29-30 caracteres de los alfabetos turco y finés. Con un alfabeto más pequeño pero con glifos que ya codifican información silábica, el espacio combinatorio efectivo es diferente.

### Información mutua posicional: el resultado más revelador

| Lengua | MI glifo | MI sílaba | Amplificación |
|--------|----------|-----------|--------------|
| Voynich | 0.658 | 0.608 | 0.92× |
| Turco | 0.164 | 0.752 | 4.59× |
| Finés | 0.197 | 0.830 | 4.20× |

En turco y finés, la MI posicional se amplifica ~4× al pasar de caracteres individuales a sílabas. Las letras individuales tienen poca preferencia posicional, pero las sílabas sí la tienen ---lo esperable en cualquier lengua con morfología.

En el Voynich, **no hay amplificación** (ratio 0.92×). Los glifos ya codifican tanta información posicional como las sílabas resultantes. Esto tiene una implicación profunda: **los glifos del Voynich ya son unidades funcionales de alto nivel, no simples letras que se agregan en sílabas.** El glifo D1, con 98.7% en posición inicial, ya funciona como un marcador de onset. El glifo G1, con 96.9% en posición final, ya funciona como un marcador de coda. La segmentación TP está agrupando estos glifos en unidades más grandes (tipo morfema), pero la información posicional ya estaba codificada a nivel de glifo individual.

Este resultado conecta directamente con el déficit de MI posicional del modelo SilPart (MI_pos=0.477 vs. 0.658 del Voynich, señalado en el Capítulo 14): el mecanismo real del Voynich tiene dependencias glifo-posición más rígidas que las que el modelo SilPart produce, posiblemente porque los glifos no representan fonemas que se agregan en sílabas, sino que cada glifo ya *es* una unidad silábica o morfosilábica.

![Figura 16.7. Comparación silábica multilingüe. comparacion_silabica_multilingue.png)

*Figura 16.7. Comparación silábica entre Voynich, turco y finés. Izquierda: distribución Zipf. Centro: métricas comparativas. Derecha: tabla resumen con distancias.*

## 16.5 Síntesis e implicaciones

Los cuatro análisis convergen en un diagnóstico coherente:

**1. Inventario silábico plausible.** El Voynich tiene un núcleo funcional de ~200 tipos silábicos, con 40 tipos cubriendo el 50% de los tokens. Esto es compatible con un silabario grande tipo akshárico, no con un alfabeto fonémico ni con un silabario simple tipo kana.

**2. Estructura morfológica onset-nuclear-coda.** La clasificación posicional produce tres clases funcionales bien diferenciadas, con una conexión directa y verificable entre glifos-prefijo conocidos (D1, K1) → sílabas onset, y glifos-sufijo conocidos (A2, C1, G1) → sílabas coda. La morfología es compartida entre secciones; la variación temática es léxica.

**3. Restricciones morfofonológicas internas.** La asociación nuclear-coda (V=0.284, p≈0) demuestra que las combinaciones raíz-sufijo no son libres: existen restricciones internas compatibles con armonía vocálica parcial o fonotaxis. Los paradigmas de sufijo (27 raíces productivas, Gini=0.49) muestran un sistema con variedad real pero dominancia de unas pocas terminaciones.

**4. Los glifos ya son unidades silábicas.** La ausencia de amplificación de MI posicional (0.92×) al pasar de glifos a sílabas ---frente a ~4× en turco y finés--- indica que los glifos del Voynich ya codifican información de nivel silábico. Esto no significa que la segmentación sea inútil: al contrario, las sílabas segmentadas revelan paradigmas morfológicos que los glifos individuales no exhiben. Pero sí significa que la unidad base del sistema es el glifo-sílaba, no el glifo-fonema.

### Implicaciones para el descifrado

Estos resultados acotan el espacio de posibilidades para futuros intentos de descifrado:

- Cualquier propuesta debe ser compatible con un inventario efectivo de ~200 unidades funcionales
- Las dependencias posicionales de los glifos no son un artefacto: son una propiedad intrínseca del sistema
- La lengua subyacente (si la hay) debería tener armonía vocálica u otra restricción morfofonológica que produzca V ≈ 0.28 en las combinaciones raíz-sufijo
- El vector de ataque más prometedor es la identificación de paradigmas de sufijo: con 27 raíces productivas y sus sufijos catalogados, existe un sistema de restricciones explotable por métodos bayesianos de descifrado (tipo Ravi y Knight, 2011) operando a nivel de sílaba en lugar de carácter

**Nota (resultado de la Parte V)**: El descifrado bayesiano a nivel sílaba (sustitución 1-a-1) produce un ranking robusto (hebreo #1, árabe #2) pero confianza posterior muy baja (R-hat < 1.1 solo en el 7% de sílabas), lo que sugiere que la codificación del Voynich no es sustitutiva sino composicional.

**Nota (resultado del descifrado composicional)**: El descifrado a nivel de glifo→carácter confirma independientemente el ranking silábico (hebreo #1, árabe #2) con discriminación aún mayor: brecha semíticas→no-semíticas de 11.7 puntos (vs 2.9 en el silábico). La convergencia MCMC mejora drásticamente (R-hat < 1.1 en el 59% de glifos vs 7% de sílabas), con 18 glifos mapeados con 100% de confianza posterior. El ratio PPX mapeada/nativa baja de 4.23 a 2.07 para hebreo. Los resultados sugieren que múltiples glifos codifican la misma consonante hebrea en distintos contextos posicionales (e.g., ש atrae 17 glifos, ר 15), compatible con la hipótesis SilPart de codificación composicional por slots

### Limitaciones

1. **Segmentación sin conocimiento fonológico**: los métodos TP y entropía son puramente estadísticos; no incorporan conocimiento sobre las propiedades fonéticas de los glifos
2. **Percentil P20 arbitrario**: la elección del umbral afecta significativamente el tamaño del inventario; los resultados deben interpretarse como condicionales a esta elección, aunque el sweep de parámetros muestra que las conclusiones cualitativas son robustas
3. **Corpus limitado**: ~37K palabras es suficiente para estadísticas robustas a nivel de frecuencias, pero limita el análisis de combinaciones raras y paradigmas con frecuencia baja
4. **Clasificación posicional simplificada**: el umbral 0.60 para onset/coda es heurístico; un enfoque bayesiano con priors informativos sería más riguroso

## 16.6 Trabajo futuro

1. ~~**Descifrado composicional SilPart-aware**~~: completado. Mapping glifo→carácter (many-to-one, 166 glifos → ~27-28 chars) con CharLM trigrama y MCMC multi-chain. Confirma ranking silábico (hebreo #1, árabe #2) con mayor discriminación (brecha 11.7 pts) y mejor convergencia (59% R-hat < 1.1). 18 glifos con 100% de confianza posterior
2. **Monte Carlo fonémico**: explorar asignaciones aleatorias de fonemas a glifos y evaluar cuáles producen fonologías plausibles según las restricciones morfofonológicas detectadas
3. ~~**Descifrado bayesiano a nivel sílaba**~~: completado en la Parte V. El ranking (hebreo #1) es robusto pero la confianza es baja, motivando el enfoque composicional del punto 1
4. **Cruce con imágenes**: correlacionar vocabulario silábico específico por sección con el contenido visual de las ilustraciones para identificar posibles cribs
5. **Validación cruzada**: repetir el análisis con transcripciones alternativas (EVA, Currier) para verificar robustez de los resultados

# Referencias de la Parte IV

- Harris, Z. S. (1955). "From Phoneme to Morpheme." *Language* 31(2): 190--222.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

- Saffran, J. R., Aslin, R. N. y Newport, E. L. (1996). "Statistical Learning by 8-Month-Old Infants." *Science* 274(5294): 1926--1928.

Partes I, II, III y IV disponibles como documentos independientes.
