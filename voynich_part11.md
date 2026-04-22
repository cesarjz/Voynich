# PARTE XI — Codificación de Dos Niveles y Decodificación Estructural (Capítulos 35.11–36)

## 35.11 Descubrimiento de la codificación de dos niveles (notebooks `36_silpart_structure.ipynb`, `37_distributional_clustering.ipynb`, `38_constructed_languages.ipynb`)

El fracaso de 19 modelos monoalfabéticos motiva un análisis estructural más profundo de los pools posicionales de SilPart. En lugar de preguntar "¿qué idioma está codificado?", esta sección pregunta "¿qué tipo de mecanismo de codificación produce esta estructura?"

**Diseño:** Cada uno de los 166 glifos distintos se clasifica por su perfil de probabilidad de transición (TP) en dos niveles:

- **Nivel-1 (estructural):** glifos con alta fidelidad posicional (TP ≥ umbral), que representan el 48.3% de los tokens. Estos glifos operan como marcadores estructurales — selectores de posición deterministas que definen los límites silábicos.
- **Nivel-2 (contenido):** glifos con menor fidelidad posicional (TP < umbral), que representan el 51.7% de los tokens. Estos glifos portan el contenido variable y muestran mayor flexibilidad distribucional.

**Métricas clave:**

- **Utilización:** solo el 6.7% de las combinaciones posibles de bigramas Nivel-2 aparecen en el texto — el 93.3% del espacio combinatorio está prohibido.
- **Ratio onset/coda:** 1.95 — los onsets son casi el doble de frecuentes que las codas, indicando una plantilla silábica asimétrica.
- **Entropía Nivel-1:** significativamente menor que la de Nivel-2, confirmando la distinción estructural vs. contenido.

**Clustering distribucional** (notebook 37) aplica clustering jerárquico a las distribuciones de glifos onset y coda. Los onsets se agrupan en 4–6 grupos funcionales; las codas en 3–4 grupos. Los clusters no corresponden a ninguna categoría fonológica de lengua natural conocida.

**Comparación con lenguas construidas** (notebook 38): las métricas de dos niveles del Voynich se comparan con Esperanto, Enoquiano (Dee/Kelley) y Lingua Ignota (Hildegard von Bingen). Ninguna lengua natural en el conjunto de control (hebreo, latín, árabe, turco, finés) muestra una separación de dos niveles comparable. El Esperanto es la coincidencia más cercana, compartiendo la regularidad estructural pero no la restricción extrema de utilización. El Enoquiano muestra similitudes superficiales pero carece de consistencia posicional. **Ningún sistema conocido — natural o construido — reproduce la huella digital completa del Voynich.**

Notebooks: `36_silpart_structure.ipynb`, `37_distributional_clustering.ipynb`, `38_constructed_languages.ipynb`
Resultados: `silpart_structure_resultados.json`, `distributional_clustering_resultados.json`, `constructed_languages_resultados.json`

## 35.12 Sección herbal: clusters de onset vs. categorías de plantas (notebook `39_herbal_onset_analysis.ipynb`)

Si los onsets de Nivel-1 codifican una categoría temática (p.ej., tipo de planta en las páginas herbales), entonces los folios herbales asignados a la misma categoría de planta deberían compartir distribuciones de onset. Esta sección testea si la estructura de clusters de onset se correlaciona con el contenido botánico.

**Diseño:** Los 130 folios herbales se agrupan por categoría de planta (según la asignación de los estudios botánicos estándar del Voynich). Para cada folio, se calcula la distribución de glifos onset. Un test de permutación evalúa si la similitud intra-categoría supera la similitud inter-categoría.

**Resultado:** El test de permutación arroja p = 0.336 — **los onsets no codifican categorías de plantas**. Las distribuciones de onset no se agrupan por contenido botánico dentro de la sección herbal.

Sin embargo, un test complementario a **nivel de sección** (herbal vs. astronómica vs. biológica vs. farmacéutica) muestra una separación altamente significativa (p < 10^−84). Las distribuciones de onset difieren dramáticamente entre las secciones del manuscrito, confirmando que **la codificación a nivel de sección es real** pero opera a una granularidad más gruesa que las categorías individuales de plantas.

Notebook: `39_herbal_onset_analysis.ipynb`
Resultados: `herbal_onset_resultados.json`

## 35.13 Simulación de código de recetas medieval (notebook `40_recipe_code_simulation.ipynb`)

La tasa de utilización del 6.7% — lo que significa que el 93% de las combinaciones posibles de glifos están prohibidas — es la característica estructural más distintiva descubierta por el análisis de dos niveles. Esta sección pregunta: ¿qué tipo de sistema de codificación real podría producir una restricción combinatoria tan extrema?

**Diseño:** Una simulación Monte Carlo modela un **código restringido** inspirado en tradiciones medievales de recetarios/farmacopeas, donde un conjunto fijo de marcadores estructurales (ingredientes, acciones, cantidades) se combinan con glifos de contenido bajo reglas combinatorias estrictas. La simulación barre el parámetro p_valid (probabilidad de que una combinación aleatoria esté permitida) y compara la tasa de utilización resultante con el 6.7% observado en el Voynich.

**Resultado:** Un código restringido con p_valid ≈ 0.08 reproduce la utilización observada. Esto significa que aproximadamente el **92% de las combinaciones de glifos están prohibidas** por las reglas de codificación — consistente con un sistema donde los marcadores estructurales imponen restricciones sintácticas rígidas sobre qué elementos de contenido pueden seguir.

La simulación también reproduce la asimetría onset/coda y el ratio de tokens Nivel-1/Nivel-2 cuando el vocabulario estructural es más pequeño que el vocabulario de contenido. Esto no prueba que el Voynich sea un código de recetas, pero demuestra que las estadísticas observadas son **compatibles con una codificación combinatoria restringida** y no con una lengua natural o un cifrado de sustitución simple.

Notebook: `40_recipe_code_simulation.ipynb`
Resultados: `recipe_simulation_resultados.json`

## 35.14 Decodificación estructural: esqueleto de diccionario de código (notebook `41_structural_decoding.ipynb`)

Dada la separación de dos niveles, esta sección intenta una **decodificación estructural (no lingüística)** — identificando los roles funcionales de los elementos de Nivel-1 sin asumir un idioma objetivo.

**Diseño:** Los glifos de Nivel-1 se clasifican por su comportamiento distribucional en tres categorías funcionales:

- **Marcadores** (20 elementos): glifos de alta frecuencia, posición fija, que aparecen en los límites silábicos. Probablemente funcionan como delimitadores estructurales o indicadores de categoría.
- **Encabezados de sección** (83 elementos): glifos que aparecen predominantemente en posiciones iniciales de bloques de texto. Su distribución se correlaciona con los límites de sección del manuscrito.
- **Modificadores** (21 elementos): glifos de baja frecuencia que se adjuntan a secuencias de contenido Nivel-2, posiblemente indicando variaciones o calificadores.

**Inventario estructural total:** 125 elementos (20 + 83 + 21), con un elemento sin clasificar.

**Gramática de entradas:** El análisis de los patrones de alternancia Nivel-1/Nivel-2 revela una estructura regular: las entradas consisten en secuencias alternantes T1-T2, con longitudes medias de racha de 2.1 palabras (T1) y 2.2 palabras (T2). Esta alternancia es significativamente más regular de lo esperado para una lengua natural (test de permutación p < 0.001).

Notebook: `41_structural_decoding.ipynb`
Resultados: `structural_decoding_resultados.json`

## 35.15 Robustez del umbral TP (notebook `42_tp_threshold_robustness.ipynb`)

La separación de dos niveles depende del umbral de probabilidad de transición utilizado para clasificar los glifos. Esta sección testea si los hallazgos clave son robustos ante diferentes elecciones de umbral.

**Diseño:** El umbral TP se barre a través de 8 valores desde P5 (percentil 5) hasta P40 (percentil 40). En cada umbral, se recalculan la tasa de utilización, el ratio onset/coda y el balance de tokens Nivel-1/Nivel-2.

**Resultados:**

| Métrica | Rango en P5–P40 | ¿Robusto? |
|---------|-----------------|-----------|
| Utilización | 6–12% | Sí |
| Ratio onset/coda | >1 en 7/8 umbrales | Sí |
| Split Nivel-1/Nivel-2 | 35–60% | Depende del umbral |

La tasa de utilización se mantiene en el rango 6–12% independientemente del umbral — la restricción combinatoria extrema es una **propiedad estructural robusta**, no un artefacto de una elección particular de umbral. La asimetría onset/coda (ratio > 1) se mantiene en 7 de los 8 umbrales testeados. Solo el balance exacto de tokens Nivel-1/Nivel-2 varía con el umbral, lo cual es esperado por construcción.

**Conclusión:** La codificación de dos niveles y sus firmas clave (baja utilización, asimetría onset) son hallazgos robustos que no dependen de las elecciones de parámetros.

Notebook: `42_tp_threshold_robustness.ipynb`
Resultados: `tp_robustness_resultados.json`

# Capítulo 36. Balance final: SilPart y los límites del descifrado

## 36.1 SilPart como modelo generativo vs. herramienta de descifrado

A lo largo de los Capítulos 23--35 se han testado 16 modelos de descifrado distintos, muchos de ellos motivados directamente por las predicciones del modelo generativo SilPart (d=0.445, mejor fit del Capítulo 4). Es necesario distinguir entre dos roles de SilPart:

1. **Modelo generativo (descriptivo).** SilPart describe cómo se organiza estadísticamente el texto Voynich: palabras compuestas de sílabas, cada posición silábica (onset/nucleus/coda) con un pool cerrado de glifos. Este rol **se mantiene intacto**: ningún experimento de descifrado contradice la estructura posicional, y el 73% de glifos position-locked se confirma repetidamente.

2. **Guía para el descifrado (prescriptivo).** Las predicciones de SilPart generan hipótesis sobre cómo debería funcionar el mapping glifo→carácter/sílaba. Este rol ha sido **sistemáticamente refutado**: cada estrategia de descifrado que intenta explotar la estructura posicional produce resultados peores que la tabla única de neural v2.

## 36.2 Balance de hipótesis SilPart-derivadas

La siguiente tabla resume las doce hipótesis de descifrado derivadas de SilPart y sus resultados:

| Hipótesis | Modelo | Capítulo | Scorecard | Status |
|-----------|--------|----------|-----------|--------|
| Posición → tabla de mapping distinta por posición | Syl-Heb (3 tablas) | 26 | 4+/2±/0− | n-gram 14% (vs 68%) |
| Posición → variante homofónica del mismo carácter | Homofónico posicional | 22 | 2+/2±/2− | w_homo inerte |
| Glifos en posiciones complementarias = alógrafos | Allograph | 28 | 4+/0±/2− | **Descartado** |
| Glifo = sílaba hebrea, con variantes homofónicas | Syl-Homophonic | 29 | 3+/1±/2− | **Descartado** |
| Registro target equivocado (Mishnah/Zohar) | Registers | 30 | 2+/2±/1− (mejor) | **Descartado** |
| Sílaba Voynich → sílaba hebrea | Syl-to-Syl | 31 | 2+/1±/2− | **Descartado** |
| Onset/coda = NULL estructural, solo nucleus mapea | Nucleus-only | 32 | 4+/0±/1− | **Descartado** (n-gram inflado) |
| NULL parcial con umbral parametrizado θ | Partial NULL | 33 | 4+/0±/1− | **Descartado** (n-gram inflado, 1 raíz) |
| EVA (|Σ|/|A|=1.26, rango resoluble) | Neural v2 EVA | 34 | 2+/0±/3− | **Descartado** (n-gram 0%) |
| Sustitución indexada por rol morfológico (P/R/S) | Morphological | 35 | 4+/1±/1− | **Descartado** (n-gram 16%, 0 raíces) |
| Sustitución morfológica aramea (Zohar) | Morph. Zohar | 35 | 3+/0±/3− | **Descartado** (n-gram 0%, 1 raíz) |
| Posición afecta selección, no significado (tabla única) | Neural v2 | 25 | **4+/0±/1−** | **Mejor resultado** |

El patrón es claro: **cuanto más se intenta explotar la estructura posicional de SilPart para el descifrado, o cambiar el corpus target, peor es el resultado.** El mejor modelo (neural v2) es precisamente el que ignora la posición y usa una tabla única contra Torah.

## 36.3 La paradoja SilPart

Esto constituye una paradoja genuina:

- SilPart es el mejor modelo generativo → la estructura posicional es **real**
- Pero explotar esa estructura empeora el descifrado → la estructura posicional es **irrelevante** para el mapping

La resolución más parsimoniosa es la conclusión del Capítulo 26: **la posición afecta la selección de glifo, no su significado.** Un glifo de onset y un glifo de coda pueden mapear al mismo carácter hebreo, pero el sistema de escritura selecciona cuál usar según la posición. La posición es una propiedad del **sistema gráfico**, no del **código criptográfico**.

Esto es análogo a la escritura árabe cursiva, donde la misma letra tiene formas distintas según su posición en la palabra (inicial, medial, final, aislada), pero el valor fonético no cambia. En el Voynich, los pools posicionales serían variantes gráficas del mismo alfabeto subyacente, no tablas de sustitución independientes.

## 36.4 Espacio de hipótesis residual

Dentro del framework de sustitución monoalfabética + LM hebreo, las combinaciones derivadas de SilPart están esencialmente agotadas. Las hipótesis residuales caen fuera de este framework:

| Hipótesis | Argumento en contra |
|-----------|-------------------|
| Cifrado polialfabético (Vigenère) | Estabilidad inter-folio r=0.9999 — incompatible con rotación de clave |
| Transposición intra-palabra | La estructura onset→nucleus→coda sería inexplicable si los glifos estuvieran desordenados |
| Glifos nulos (onset/coda no codifican) | Caps. 32--33: nucleus-only y partial NULL (θ=0.7) producen n-gram inflado (palabras cortas); 1 raíz máximo |
| Otra lengua target (no semítica) | Gap NW semítico → no semítico >3.5 pts (Capítulo 5); hebreo/arameo indistinguibles (gap 0.27) |
| Registro hebreo alternativo (mishnaico/zohárico) | Cap. 30: 3 registros dan resultados equivalentes; cross-scoring muestra que mappings son artefactos del LM |
| Contenido no lingüístico (tablas, listas) | Fingerprint estadístico (Parte III) confirma estructura lingüística genuina |

Ninguna de estas alternativas tiene soporte empírico suficiente para justificar una nueva batería de experimentos dentro del scope de este trabajo.

## 36.5 Síntesis: qué sabemos y qué no

### Lo que sabemos (con alta confianza)

1. **El Voynich tiene estructura lingüística genuina.** La U-curve, la MI posicional, y la estabilidad inter-folio lo distinguen de todos los controles (aleatorios, glossolalia, cifrados simples).

2. **La estructura posicional es real.** SilPart (d=0.445), 73% de glifos position-locked, pools onset/nucleus/coda con distribuciones propias.

3. **Si el texto codifica una lengua natural, es compatible con hebreo/arameo bíblico.** Hebreo #1 en todos los rankings, arameo indistinguible (gap 0.27), gap a lenguas no semíticas >3.5 pts.

4. **El mapping char-level con tabla única es la representación más parsimoniosa.** Neural v2 (68% n-gram) supera a todos los modelos posicionales, silábicos, alográficos y homofónicos.

5. **Existe un límite estructural de ~2--5 raíces y ~68% n-gram.** 16 modelos independientes convergen en estos límites, que son propiedades del espacio de soluciones, no de los modelos.

6. **El límite es independiente de la transcripción.** Neural v2 sobre EVA (|Σ|/|A|=1.26, rango resoluble) produce 0% n-gram y 0 raíces: la barrera es la codificación del manuscrito, no el ratio de tamaños de alfabeto.

### Lo que no sabemos

1. **Si el Voynich codifica realmente una lengua natural.** El fingerprint lingüístico es necesario pero no suficiente: sistemas formales complejos podrían producir patrones similares.

2. **Cuál es el mecanismo de codificación específico.** Ningún modelo produce texto hebreo legible. El techo de 3--5 raíces (de 100 posibles) sugiere que, o bien el mecanismo es más complejo que sustitución monoalfabética, o bien la lengua subyacente no es hebreo.

3. **Qué significa la estructura posicional.** SilPart la describe pero no la explica: ¿es variación gráfica (como el árabe cursivo)? ¿Morfológica (prefijo/raíz/sufijo)? ¿O un artefacto del mecanismo de generación?

## 36.6 Conclusión metodológica

El resultado principal de los Capítulos 23–35 no es un descifrado exitoso sino una **contribución metodológica**: un pipeline completo (fingerprint → modelo generativo → descifrado bayesiano → validación multi-test) aplicado exhaustivamente a 19 variantes de modelos, incluyendo 3 registros target distintos, mapping sílaba-a-sílaba, filtrado selectivo de glifos estructurales, sustitución indexada por rol morfológico, sustitución morfológica aramea (Zohar), replicación sobre una transcripción alternativa (EVA), y tres experimentos cross-lingüísticos (hebreo tibbónido, judeo-árabe y Ge'ez). El experimento Ge'ez (Modelo 19) es particularmente significativo: con |Σ|/|A| ≈ 0.88 — el primer test con ratio cercano a 1:1 — demuestra que el techo estructural no es un artefacto del desajuste de tamaño de alfabeto sino una propiedad del texto Voynich mismo. El resultado negativo robusto — ningún modelo produce texto legible, todos convergen en los mismos límites — es en sí mismo informativo: establece una cota inferior para la complejidad del mecanismo de codificación del Voynich y descarta formalmente las hipótesis de sustitución simple contra cinco lenguas semíticas que abarcan tres tipos de sistema de escritura (abjad, abjad transliterado, abugida).

SilPart permanece como la mejor descripción de la estructura superficial del manuscrito, pero esa estructura no se traduce en una vía viable de descifrado dentro del paradigma de sustitución. El Voynich, si codifica una lengua, lo hace con un mecanismo que trasciende la sustitución monoalfabética — o bien codifica algo distinto de una lengua natural conocida.

# Referencias de la Parte IX

- Hochreiter, S. y Schmidhuber, J. (1997). "Long Short-Term Memory." *Neural Computation*, 9(8), pp. 1735--1780.

- Hinton, G. E. (2012). "Improving neural networks by preventing co-adaptation of feature detectors." *arXiv preprint arXiv:1207.0580*. [Dropout como regularización]

- Knight, K., Nair, A. y Rathod, N. (2006). "Unsupervised Analysis for Decipherment Problems." *Proceedings of the COLING/ACL 2006*, pp. 499--506.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the ACL*, pp. 12--21.

- Stolfi, J. (2005). "A Tentative Partial Transliteration of the Voynich Manuscript." Manuscrito técnico. [Paradigmas posicionales de prefijos y sufijos]

Partes I--IX disponibles como documentos independientes.
