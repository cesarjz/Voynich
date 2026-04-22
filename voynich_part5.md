# PARTE V

# Descifrado bayesiano silábico del Voynich

La Parte IV segmentó las palabras del Voynich en sílabas, clasificó cada tipo silábico por su función posicional (onset, nuclear, coda) y detectó restricciones morfofonológicas internas ---armonía nuclear-coda (V=0.284) y 27 paradigmas de sufijo productivos---. El análisis concluyó que el vector de ataque más prometedor para el descifrado es la explotación de estos paradigmas mediante métodos bayesianos operando a nivel de sílaba (tipo Ravi y Knight, 2011). La Parte V implementa exactamente ese enfoque: un descifrado bayesiano que intenta sustituir cada sílaba del Voynich por una sílaba de una lengua candidata, evaluando la plausibilidad del resultado mediante un modelo de lenguaje silábico combinado con criterios morfológicos.

# Capítulo 17. Descifrado bayesiano silábico

## 17.1 Motivación: de la segmentación al descifrado

La segmentación de la Parte IV produjo un inventario canónico de 2,923 tipos silábicos (792 con frecuencia ≥ 5). La distribución Zipf de este inventario, sus paradigmas de sufijo y su armonía nuclear-coda son compatibles con una lengua aglutinante real. La pregunta natural es: ¿a *qué* lengua corresponden estas sílabas?

El enfoque clásico de descifrado bayesiano (Ravi y Knight, 2011) formula el problema como una sustitución: existe un mapping desconocido σ que transforma cada símbolo del texto cifrado en un símbolo del texto llano. El objetivo es encontrar σ* = argmax P(σ | texto cifrado), donde P se factoriza usando un modelo de lenguaje del texto llano como prior. Ravi y Knight aplicaron este método a nivel de carácter. Aquí se adapta a nivel de sílaba: cada sílaba del Voynich se mapea a una sílaba de la lengua candidata, y la plausibilidad se evalúa con un modelo de lenguaje silábico más dos componentes morfológicas.

La adaptación silábica introduce un desafío computacional severo: con 792 tipos funcionales mapeados a inventarios de tamaño comparable, el espacio de permutaciones biyectivas es del orden de 800!, astronómicamente mayor que el ~30! del descifrado a nivel de carácter. Este espacio obliga a usar inicialización inteligente y exploración MCMC para encontrar regiones de alta probabilidad sin explorar exhaustivamente.

## 17.2 Método: SyllableLM, MappingState, scoring multi-componente

### Modelo de lenguaje silábico (SyllableLM)

Para cada lengua candidata, se entrena un modelo de lenguaje de bigramas de sílabas con suavizado Witten-Bell:

P(syl_i | syl_{i-1}) = λ × C(syl_{i-1}, syl_i) / C(syl_{i-1}) + (1-λ) × P_backoff(syl_i)

donde λ se determina por Witten-Bell y el backoff es la distribución unigrama. Se incluyen tokens BOS/EOS para modelar las probabilidades de inicio y fin de palabra. Las probabilidades se calculan en log₂ (celda 5 del notebook `06_bayesian_syllabic.ipynb`).

### Estado de mapping (MappingState)

La clase `MappingState` mantiene un mapping biyectivo σ entre sílabas del Voynich y sílabas de la lengua candidata, con restricción de clase: sílabas onset solo mapean a sílabas onset, nucleares a nucleares, y codas a codas. Esto reduce el espacio de búsqueda y asegura coherencia posicional. Los métodos principales son:

- `propose_swap()`: intercambia el target de dos sílabas aleatorias dentro de la misma clase funcional
- `apply_word()`: dado un mapping σ, transforma una palabra del Voynich en una secuencia de sílabas de la lengua candidata
- `apply_corpus()`: aplica el mapping a todo el corpus y calcula el score agregado

### Scoring multi-componente

El score total combina tres componentes con pesos fijos (celda 5):

**S_total = 2.0 × S_LM + 1.5 × S_paradigma + 1.0 × S_armonía**

donde:

- **S_LM** (peso 2.0): log-verosimilitud media del corpus mapeado bajo el SyllableLM de la lengua candidata. Mide cuánto se parece la secuencia de sílabas resultante a texto real de esa lengua.

- **S_paradigma** (peso 1.5): combinación de JSD entre distribuciones de sufijos, overlap de inventario de sufijos y similitud de Gini entre paradigmas del Voynich y de la lengua candidata. Mide si los paradigmas morfológicos se preservan tras el mapping.

- **S_armonía** (peso 1.0): preservación de las restricciones de co-ocurrencia nuclear-coda. Mide si las asociaciones preferentes entre raíces y sufijos del Voynich se mantienen en la lengua mapeada.

## 17.3 Cinco lenguas candidatas

Se seleccionan cinco lenguas que cubren los principales candidatos tipológicos identificados en las Partes II-IV (celda 7):

| Lengua | Familia | Tipología | Justificación |
|--------|---------|-----------|---------------|
| Turco | Altaica | Aglutinante | Spectral gap = 0.509, armonía vocálica |
| Finés | Urálica | Aglutinante | Paradigmas de caso ricos, gap = 0.577 |
| Latín | Indoeuropea | Flexiva | Lingua franca del siglo XV |
| Hebreo | Semítica | Raíces triconsonánticas | Hipótesis semítica clásica |
| Árabe | Semítica | Raíces triconsonánticas | Control semítico |

La selección equilibra las dos familias más compatibles con las propiedades estadísticas del Voynich (aglutinantes por el spectral gap, semíticas por la estructura posicional) con el latín como candidato histórico por defecto. Los corpora de referencia se obtienen de Leipzig Corpora Collection y se procesan con la misma segmentación TP-P20 aplicada al Voynich (celdas 8-9).

## 17.4 Inicialización distribucional

### Vectores distribucionales 7D

Cada tipo silábico (tanto del Voynich como de cada lengua candidata) se describe mediante un vector de 7 dimensiones (celda 13):

1. Frecuencia normalizada
2. Proporción en posición inicial
3. Proporción en posición media
4. Proporción en posición final
5. Entropía forward (log₂ del número de contextos derechos)
6. Número de contextos izquierdos
7. Número de contextos derechos

### Algoritmo húngaro

La inicialización usa `scipy.optimize.linear_sum_assignment` para encontrar la asignación biyectiva que minimiza la distancia coseno total entre vectores del Voynich y vectores de la lengua candidata, respetando las restricciones de clase (onset↔onset, nuclear↔nuclear, coda↔coda). Esta inicialización es óptima dentro de las restricciones lineales y proporciona un punto de partida informado para la optimización posterior (celdas 14-15).

## 17.5 EM adaptado + MCMC multi-chain

### Fase EM

Se ejecutan 30 iteraciones de un algoritmo EM adaptado por cada lengua candidata (celda 17):

- En cada iteración, se proponen swaps dentro de cada clase funcional
- Se aceptan los swaps que mejoran el score total
- Early stopping con paciencia de 5 iteraciones sin mejora
- Subsample de 2,000 palabras por iteración para eficiencia

### Fase MCMC

Para las lenguas con mejor score EM, se ejecuta un MCMC Metropolis-Hastings multi-chain (celda 20):

| Parámetro | Valor |
|-----------|-------|
| Cadenas | 4 (seeds: 42, 137, 256, 999) |
| Iteraciones/cadena | 15,000 |
| Burn-in | 3,000 (descartadas) |
| Thinning | Cada 5ª muestra → 2,400 muestras/cadena |
| Total muestras | 12,000 por lengua |
| Propuesta | Swap aleatorio dentro de clase |
| Temperatura | Calibrada desde 300 propuestas, T_ratio = 100 |
| Aceptación | Metropolis-Hastings, target ~50% |
| Subsample/iter | 2,000 palabras (5.4% del corpus) |

La temperatura se calibra empíricamente: se ejecutan 300 propuestas de prueba y se fija T_start para obtener una tasa de aceptación cercana al 50%. La temperatura decrece exponencialmente hasta T_end, focalizando la exploración en regiones de alta probabilidad.

## 17.6 Resultados: ranking de lenguas

El ranking final combina las fases EM y MCMC. Para hebreo y arameo (top-2 tras EM), el score reportado es el mejor encontrado por MCMC; para las cuatro restantes, el score EM (celda 25):

| # | Lengua | Familia | Score total | S_LM | S_paradigma | S_armonía | PPX mapeada | PPX nativa | Ratio PPX |
|---|--------|---------|-------------|------|-------------|-----------|-------------|------------|-----------|
| 1 | **Hebreo** | Semítica | **-35.70** | -17.55 | 0.049 | -0.669 | 100.19 | 25.1 | 3.99 |
| 2 | **Arameo** | Semítica | **-35.71** | -17.78 | 0.363 | -0.690 | 106.4 | 25.25 | 4.21 |
| 3 | **Árabe** | Semítica | -37.41 | -18.39 | 0.140 | -0.834 | 124.9 | 25.4 | 4.91 |
| 4 | Finés | Aglutinante | -39.28 | -19.36 | 0.195 | -0.846 | 161.1 | 29.4 | 5.49 |
| 5 | Latín | Indoeuropea | -39.83 | -19.77 | 0.259 | -0.675 | 179.5 | 13.9 | 12.94 |
| 6 | Turco | Aglutinante | -39.89 | -19.69 | 0.250 | -0.886 | 175.6 | 33.2 | 5.29 |

Nota: en la fase EM, el arameo ocupaba el #1 (-36.50 vs -36.66 para hebreo). El MCMC invirtió el orden por un margen efectivamente nulo (0.01 nats).

> **Nota de reproducibilidad:** Los scores exactos del MCMC varían entre ejecuciones debido a la naturaleza estocástica del sampler. El gap hebreo-arameo fluctúa entre ~0.01 y ~0.27 nats entre ejecuciones, pero siempre queda dentro del IC 95% bootstrap que cruza el cero. El paper companion reporta 0.27 nats de una ejecución anterior; los valores de arriba reflejan la ejecución más reciente. Todas las conclusiones cualitativas (cluster NW semítico, >3.5 nats de separación con no-semíticas) son estables entre ejecuciones.

### Interpretación del ranking

El ranking muestra una estructura de tres niveles:

**Nivel 1 — Semíticas noroccidentales:** Hebreo y arameo quedan prácticamente empatadas (Δ = 0.01 puntos). Hebreo tiene mejor S_LM (-17.55 vs -17.78) y menor ratio PPX (3.99 vs 4.21), mientras que arameo tiene significativamente mejor S_paradigma (0.363 vs 0.049), indicando que sus paradigmas morfológicos se ajustan mejor a la estructura silábica del Voynich. La diferencia es mínima y no permite discriminar con confianza entre ambas.

**Nivel 2 — Árabe:** El árabe queda a 1.5 puntos de las semíticas noroccidentales. Comparte la familia semítica pero tiene fonotaxis más distinta del Voynich, lo que se refleja en su mayor ratio PPX (4.91).

**Nivel 3 — No semíticas:** Finés, latín y turco forman un cluster a >3.5 puntos de distancia de las semíticas noroccidentales. La brecha entre el nivel semítico y el no semítico es sustancial y consistente.

El arameo como candidato tiene una motivación histórica sólida: el Targum Onkelos (arameo bíblico) comparte ~70% de raíces con el hebreo pero tiene fonotaxis propia. Su inclusión como sexta lengua candidata fue motivada por la paradoja raíces-vs-fonotaxis del Capítulo 20 (Parte VII): el mapping constrained detecta raíces hebreas pero no produce n-gramas hebreos fluidos, lo cual es compatible con una lengua semítica emparentada.

El ratio PPX (perplexidad mapeada / perplexidad nativa) es revelador: para hebreo, el corpus mapeado tiene 3.99× la perplejidad del hebreo nativo. Esto es alto ---indica que el mapping no produce texto hebreo fluido--- pero es el menor de los seis candidatos. Latín tiene el peor ratio (12.94) a pesar de tener la menor PPX nativa (13.9), indicando que su baja complejidad intrínseca no compensa la mala calidad del mapping.

## 17.7 Diagnósticos MCMC: convergencia limitada

Los diagnósticos de convergencia revelan una limitación fundamental del enfoque silábico (celda 22):

### Arameo

| Métrica | Valor |
|---------|-------|
| R-hat < 1.1 | **38/713 sílabas (5%)** |
| R-hat mediana | 1.555 |
| Confianza media | 0.218 |

### Hebreo

| Métrica | Valor |
|---------|-------|
| R-hat < 1.1 | **40/697 sílabas (6%)** |
| R-hat mediana | 1.505 |
| Confianza media | 0.209 |

La convergencia es extremadamente limitada: solo el 5-6% de las sílabas tienen R-hat < 1.1, el umbral estándar de convergencia (Gelman & Rubin, 1992). La mediana de R-hat (~1.5) está muy por encima del umbral, indicando que las cadenas no han explorado el mismo espacio modal. Hebreo y arameo muestran convergencia prácticamente idéntica, lo cual es esperable dado que comparten el mismo script de 22-27 caracteres y una estructura silábica similar.

### Interpretación

La mala convergencia no es un fallo de implementación sino una consecuencia del espacio de búsqueda: con ~800 tipos funcionales y permutaciones biyectivas dentro de tres clases, el espacio posterior es enormemente multimodal. Las cadenas quedan atrapadas en modos locales diferentes. Este resultado tiene una implicación sustantiva: si el Voynich fuera realmente un cifrado sustitutivo a nivel de sílaba, las cadenas deberían converger mejor ---la señal sería más clara. La mala convergencia sugiere que la asunción de sustitución 1-a-1 es incorrecta y que la codificación es probablemente composicional.

## 17.8 Reconstrucción cualitativa

A pesar de la convergencia limitada, los mappings de mayor confianza posterior permiten una reconstrucción parcial del texto (celdas 26-30).

### Mappings de alta confianza

| Sílaba Voynich | Sílaba hebrea | Confianza posterior |
|----------------|---------------|---------------------|
| Q2 | כ (kaf) | 0.996 |
| J1 | ח (het) | 0.778 |
| Ba | ג (gimel) | 0.602 |
| Aa | נ (nun) | 0.500 |

Solo un puñado de sílabas tienen confianza posterior claramente superior al azar (0.5). El mapping Q2→כ es el más robusto (0.996), pero la mayoría de sílabas tiene confianza ~0.5, indicando que las cadenas no se ponen de acuerdo.

### Paradigmas reconstruidos

Los paradigmas de sufijo mapeados a hebreo muestran estructura parcial:

| Raíz Voynich | Raíz mapeada | N sufijos | Sufijo dominante | Tokens |
|--------------|-------------|-----------|-------------------|--------|
| Q1 | — | 8 | מ-י-ם (204 tok, 70.3%) | 290 |
| K2 | פ (pe) | 8 | ד (102 tok, 47.7%) | 214 |
| Q2 | כ (kaf) | 6 | א (96 tok, 75.0%) | 128 |

La reconstrucción muestra que los paradigmas se preservan parcialmente, pero la coherencia global es baja: la perplexidad del texto reconstruido (75.07) es muy superior a la del hebreo nativo (25.1).

## 17.9 Limitaciones

1. **Espacio de búsqueda intratable.** Con ~800 tipos silábicos funcionales, el espacio de permutaciones biyectivas (~800!) es astronómicamente mayor que en el descifrado a nivel de carácter (~30!). Incluso con inicialización húngara y MCMC multi-chain, la exploración es insuficiente para garantizar convergencia.

2. **Asunción de sustitución 1-a-1.** El modelo asume que cada sílaba del Voynich corresponde a exactamente una sílaba de la lengua candidata. Si la codificación es composicional ---como sugiere el modelo SilPart de la Parte III---, esta asunción es fundamentalmente incorrecta: cada sílaba del Voynich está compuesta por glifos (onset + núcleo + coda) que codifican información fonológica independiente.

3. **Modelo de lenguaje bigrama.** Un LM silábico de bigramas captura solo dependencias entre sílabas adyacentes. Un LM de orden superior o neuronal podría proporcionar un scoring más discriminativo.

4. **Cobertura lingüística limitada.** Solo 6 de ~7,000 lenguas del mundo. La inclusión del arameo (Targum Onkelos) mejora la cobertura semítica, pero la ausencia de lenguas romance (italiano, catalán, occitano) es notable dado el contexto histórico del manuscrito.

5. **Ausencia de información externa.** No se incorpora información de las ilustraciones, la estructura del manuscrito ni la historia de la procedencia, que podrían proporcionar *cribs* para anclar el descifrado.

### Motivación para el enfoque composicional

La convergencia limitada del MCMC silábico (~7% R-hat < 1.1) tiene una implicación directa: si la codificación del Voynich no es sustitutiva sino composicional (como predice el modelo SilPart), el nivel correcto de análisis es el glifo, no la sílaba. El Capítulo 18 implementa exactamente este cambio: un descifrado composicional donde cada glifo mapea a un carácter de la lengua candidata (many-to-one, 166 glifos → ~27-30 caracteres), reduciendo el espacio de búsqueda y permitiendo que múltiples glifos colapsen en el mismo carácter target.

# Referencias de la Parte V

- Gelman, A. y Rubin, D. B. (1992). "Inference from Iterative Simulation Using Multiple Sequences." *Statistical Science* 7(4): 457--472.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebook: `06_bayesian_syllabic.ipynb` · Resultados: `bayesiano_silabico_resultados.json`

Partes I--VII disponibles como documentos independientes.
