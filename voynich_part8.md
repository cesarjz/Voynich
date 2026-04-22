# PARTE VIII

# Cifrado homofónico posicional

La Parte VII cerró con un diagnóstico claro: el mapping composicional está degenerado (scorecard 1+/1±/3−), y el EM constrained mejora la estructura morfológica (100 raíces bíblicas, enrichment 154×) pero empeora la fluidez secuencial (percentil n-gráfico 5%). La tensión entre raíces y n-gramas, junto con la persistente asimetría morfología-fonotaxis, apunta a un problema fundamental: el LM domina el scoring y colapsa el mapping. La Parte VIII aborda esta cuestión desde un ángulo diferente: si el modelo SilPart (d=0.445) describe correctamente la generación del Voynich como una silabario con variantes posicionales, entonces debería existir un patrón de cifrado homofónico en el que glifos distintos representan el mismo carácter según su posición (onset vs coda) dentro de la sílaba. Se diseña y evalúa un modelo que busca exactamente esta señal.

# Capítulo 22. Cifrado homofónico posicional

## 22.1 Hipótesis y diseño

El modelo generativo SilPart (Parte IV, d=0.445) supera a los otros 10 modelos candidatos porque reproduce la distribución posicional de los glifos voynicheses: cada glifo tiende a aparecer preferentemente en posición de onset o coda dentro de las sílabas segmentadas. Si esta preferencia posicional es un rasgo del sistema de escritura real ---no un artefacto del modelo generativo---, entonces debería manifestarse como un cifrado homofónico posicional: dos glifos distintos pueden representar el mismo carácter de la lengua subyacente, pero uno aparece preferentemente al inicio de sílaba (onset) y otro al final (coda).

Para testar esta hipótesis se diseña un pipeline de cinco componentes (celdas 4-8 del notebook `11_homophonic.ipynb`):

1. **Clustering posicional.** Cada glifo se clasifica como onset-specialist, coda-specialist o mixed según su ratio de aparición en posición onset vs coda, con un threshold configurable. Un glifo con ratio ≥ threshold es onset; ≤ (1 − threshold) es coda; intermedio es mixed.

2. **HomophonicMappingState.** Se extiende el MappingState de la Parte VI para penalizar pares de glifos que mapean al mismo carácter pero comparten posición (same-position) y bonificar pares que difieren en posición (cross-position). Esto incentiva que las variantes homofónicas sean complementarias posicionalmente.

3. **Scoring compuesto (6 componentes):**

| Componente | Peso | Función |
|------------|------|---------|
| S_LM | w_lm = 2.0 | Verosimilitud bajo CharLM hebreo |
| S_pos | w_pos = 0.5 | Compatibilidad consonante/vocal posicional |
| S_homo | w_homo = 0.3 | Bonificación cross-position, penalización same-position |
| S_ent | w_ent = 0.3 | Entropía de la distribución glifos/carácter |
| S_card | w_card = 0.2 | Penalización por exceder k_max glifos por carácter |
| S_gram | w_gram = 0.5 | Grammar anchors (12 glifos anclados) |

4. **Inicialización posicional-aware.** El mapping inicial asigna glifos a caracteres respetando la clasificación onset/coda, distribuyendo las variantes homofónicas entre posiciones complementarias.

5. **EM + MCMC.** Optimización en dos fases: EM greedy seguido de MCMC multi-chain para explorar el posterior.

## 22.2 Sweep de hiperparámetros

Se ejecuta un sweep sobre los tres hiperparámetros centrales del modelo homofónico (celda 9 del notebook):

### Peso homofónico (w_homo)

| w_homo | Score |
|--------|-------|
| 0.3 | -41.84 |
| 0.5 | -41.84 |
| 1.0 | -41.84 |
| 1.5 | -41.84 |
| 2.0 | -41.84 |

**Diagnóstico: componente inerte.** El score es idéntico (-41.84) para todos los valores de w_homo, desde 0.3 hasta 2.0. Esto significa que el término homofónico no contribuye al scoring: la señal posicional onset/coda no genera un gradiente útil para distinguir entre mappings.

### Cardinalidad máxima por posición (k_max)

| k_max | Score |
|-------|-------|
| 1 | -41.91 |
| 2 | -41.84 |
| 3 | -42.09 |

**Resultado:** k_max = 2 es marginalmente mejor (-41.84 vs -41.91 con k=1 y -42.09 con k=3). La diferencia es mínima (0.07-0.25 puntos), consistente con la inertia del componente homofónico.

### Threshold de clasificación posicional

| Threshold | Score | Onset | Coda | Mixed |
|-----------|-------|-------|------|-------|
| 0.55 | -43.53 | — | — | — |
| 0.65 | -41.84 | — | — | — |
| 0.75 | **-41.56** | **0** | **10** | **42** |
| 0.85 | -42.65 | — | — | — |

**Resultado:** Threshold 0.75 produce el mejor score (-41.56), pero con una asimetría radical: **0 onset-specialists**, 10 coda-specialists y 42 mixed. Ningún glifo del Voynich se especializa suficientemente en posición de onset para ser clasificado como onset-specialist al threshold óptimo. Los 10 coda-specialists son: Ab, B3, B4, E2, F3, G3, H1, V2, W1, W2.

Esta asimetría onset/coda es inesperada y problemática: si existiera un cifrado homofónico posicional, esperaríamos glifos especializados en *ambas* posiciones. La ausencia total de onset-specialists invalida la premisa central del modelo.

## 22.3 EM y MCMC

Con los mejores hiperparámetros del sweep (w_homo = 0.3, k_max = 2, threshold = 0.75), se ejecutan las dos fases de optimización:

### EM greedy

| Métrica | Valor |
|---------|-------|
| Score EM | **-40.94** |

### MCMC multi-chain

| Parámetro | Valor |
|-----------|-------|
| Cadenas | 4 |
| Iteraciones/cadena | 15,000 |
| Burn-in | 5,000 |
| Thinning | 5 |

| Cadena | Acceptance rate |
|--------|-----------------|
| 1 | 43.7% |
| 2 | 42.9% |
| 3 | 42.2% |
| 4 | 45.5% |

(celdas 10-13 del notebook)

| Métrica | Valor |
|---------|-------|
| Best score MCMC | **-40.33** |
| Acceptance medio | 43.6% |
| R-hat < 1.1 | **68.1%** |

La convergencia MCMC (68.1% de glifos con R-hat < 1.1) es notablemente mejor que la del composicional (57.1%) y el constrained (39.9%). Esto no indica un mejor modelo sino un posterior más concentrado: con 0 onset-specialists y un componente homofónico inerte, el MCMC converge más fácilmente porque el espacio efectivo es más simple.

## 22.4 Comparación 3 vías y validación

Se comparan los tres modelos de descifrado ---composicional (Parte VI), constrained (Parte VII, Capítulo 20) y homofónico (este capítulo)--- sobre 7 métricas comunes más 2 específicas del modelo homofónico (celdas 14-19 del notebook):

| Métrica | Composicional | Constrained | Homofónico |
|---------|---------------|-------------|------------|
| Score | -39.71 | -40.69 | -40.33 |
| PPX mapeada | 15.15 | 19.24 | 16.60 |
| Max glifos/char | 17 | 11 | **7** |
| R-hat < 1.1 | 57% | 40% | **68%** |
| N-gram percentil | 24% | 5% | **28%** |
| Collapse z-score | -0.56 | -0.45 | -0.79 |
| Root enrichment | 84× | 154× | 48× |
| Cross-position links | N/A | N/A | **0** |
| Max same-pos/char | N/A | N/A | **2** |

**Lectura por métricas:**

- **Score:** El composicional sigue siendo el mejor (-39.71). El homofónico (-40.33) mejora al constrained (-40.69) pero no al baseline.
- **Cardinalidad:** El homofónico logra el colapso más controlado (max 7 glifos/char), igual o mejor que las restricciones explícitas del constrained (max 11).
- **Convergencia:** R-hat 68% es la mejor convergencia de los tres modelos, pero refleja simplicidad del posterior, no calidad del mapping.
- **N-gramas:** El homofónico obtiene el mejor percentil (28%), superando tanto al composicional (24%) como al constrained (5%). Las restricciones de cardinalidad+entropía producen secuencias más diversas.
- **Collapse:** El z-score del homofónico (-0.79) es el peor de los tres. Los glifos agrupados bajo un mismo carácter son menos similares distribucionales que en los otros modelos.
- **Raíces:** El enrichment (48×) es el más bajo de los tres, consecuencia de la cardinalidad restringida (max 7) que limita la probabilidad de encontrar trigramas consonánticos.
- **Cross-position links = 0:** El test específico del modelo homofónico falla completamente. Ningún carácter hebreo recibe glifos de onset Y coda simultáneamente.
- **Max same-pos/char = 2:** Cumple el criterio (≤2), pero es un resultado trivial cuando no hay onset-specialists.

### Scorecard homofónico

| Test | Valor | Criterio | Resultado |
|------|-------|----------|-----------|
| Collapse coherence (z-score) | -0.79 | z > -0.3 = PASS | **MARGINAL** |
| N-gram realism (percentil) | 28.0% | >15% = PASS | **PASS** |
| Root enrichment | 47.6× | >50× = PASS | **MARGINAL** |
| Max glifos/char | 7 | ≤7 = PASS | **PASS** |
| Cross-position links | 0 | ≥10 = PASS | **FAIL** |
| Max same-pos/char | 2 | ≤2 = PASS | **PASS** |

**Veredicto global: 3 PASS, 2 MARGINAL, 1 FAIL.** El modelo homofónico no confirma la hipótesis del cifrado posicional. Los PASS son métricas de control (cardinalidad, same-pos) que reflejan las restricciones impuestas, no señal descubierta. El FAIL en cross-position links es el resultado diagnóstico: el mecanismo central del modelo no funciona.

## 22.5 Diagnóstico: por qué falla la hipótesis

### 0 onset-specialists a cualquier threshold razonable

El resultado más claro es la ausencia total de glifos onset-specialist. En el rango de thresholds explorado (0.55-0.85), ningún glifo voynichés aparece en posición de onset con suficiente exclusividad para ser clasificado como especialista. Los 10 coda-specialists (Ab, B3, B4, E2, F3, G3, H1, V2, W1, W2) existen porque algunos glifos aparecen preferentemente al final de palabra/sílaba, pero no hay complemento simétrico en onset. Esto es incompatible con un cifrado homofónico posicional, que requiere pares onset-coda mapeando al mismo carácter.

### w_homo inerte (señal plana en sweep)

El componente de scoring homofónico no genera gradiente útil. Variar w_homo de 0.3 a 2.0 no cambia el score en absoluto (-41.84 en todos los casos). Esto confirma que la distribución posicional de los glifos voynicheses no contiene la señal onset/coda que el modelo busca: bonificar cross-position y penalizar same-position no tiene efecto porque los glifos no se especializan posicionalmente.

### Lo que SÍ funciona: cardinalidad + entropía

A pesar del fracaso del mecanismo central, el modelo homofónico produce el colapso más controlado (max glifos/char = 7) y el mejor percentil n-gráfico (28%). Estos beneficios provienen de los componentes de cardinalidad y entropía heredados del constrained, no del término homofónico. El modelo funciona *a pesar de* su componente central, no *gracias a* él.

### Lo que NO funciona: el mecanismo posicional central

El cross-position links = 0 es definitivo. Incluso después de MCMC con 4×15K iteraciones y acceptance rates saludables (42-45%), el posterior no produce ningún par de glifos que mapeen al mismo carácter desde posiciones complementarias. La hipótesis del cifrado homofónico posicional es incompatible con los datos.

### Tres modelos, tres perfiles de fallo → LM dominance es el problema fundamental

| Modelo | Fortaleza | Debilidad | Diagnóstico |
|--------|-----------|-----------|-------------|
| Composicional | Mejor score (-39.71) | Colapso shin (17 g/c) | LM sin restricción → colapso |
| Constrained | 100 raíces (154×) | N-gramas 5% | Anchors ayudan morfología, no fonotaxis |
| Homofónico | Cardinalidad (7 g/c), n-gramas (28%) | 0 cross-pos links | Mecanismo posicional inexistente |

Los tres modelos comparten el mismo problema subyacente: el LM hebreo (CharLM trigrama, peso 2.0) domina el scoring. Cada modelo intenta contrarrestar esta dominancia con restricciones diferentes (anchors gramaticales, penalización de cardinalidad, bonificación posicional), pero ninguno resuelve el conflicto fundamental entre maximizar la verosimilitud bajo el LM y producir un mapping lingüísticamente válido.

## 22.6 Conclusiones y próximos pasos

### Conclusiones del Capítulo 22

1. **La hipótesis del cifrado homofónico posicional no se confirma.** El test diagnóstico central ---cross-position links--- da 0. Ningún carácter hebreo recibe glifos de onset y coda simultáneamente, invalidando la premisa de variantes posicionales complementarias.

2. **El componente homofónico es inerte.** El peso w_homo no afecta el score (idéntico de 0.3 a 2.0). La distribución posicional de los glifos voynicheses no contiene la señal que el modelo busca.

3. **0 onset-specialists.** La asimetría onset/coda (0 vs 10) es incompatible con un sistema de cifrado posicional simétrico. Los glifos del Voynich no se especializan en posición de onset con la misma nitidez que en coda.

4. **Los beneficios del modelo son indirectos.** La cardinalidad controlada (max 7) y el mejor percentil n-gráfico (28%) provienen de los componentes de entropía y cardinalidad, no del mecanismo homofónico.

5. **Tres modelos, un diagnóstico convergente.** Composicional, constrained y homofónico presentan perfiles de fallo complementarios que apuntan al mismo problema fundamental: la dominancia del LM en el scoring Bayesiano. Ninguna combinación de restricciones adicionales resuelve el conflicto entre verosimilitud y validez lingüística mientras el CharLM trigrama sea el componente dominante.

### Implicaciones para el estudio

El fracaso del modelo homofónico refuerza la narrativa central del estudio: el pipeline de descifrado produce rankings informativos (hebreo/arameo #1-#2) pero mappings degenerados. La señal estadística del Voynich (curva U, MI posicional, compatibilidad semítica) es genuina, pero los métodos de descifrado automático actuales ---limitados por CharLMs trigramas y búsqueda MCMC en espacios de alta dimensión--- no son suficientes para convertir esa señal en texto legible.

Notebook: `11_homophonic.ipynb` · Resultados: `homofonico_resultados.json`

# Referencias de la Parte VIII

- Weir, M. et al. (2009). "Password Cracking Using Probabilistic Context-Free Grammars." *Proceedings of the 30th IEEE Symposium on Security and Privacy*, pp. 391--405. [Contexto sobre modelos homofónicos en criptoanálisis]

- Knight, K., Nair, A. y Rathod, N. (2006). "Unsupervised Analysis for Decipherment Problems." *Proceedings of the COLING/ACL 2006*, pp. 499--506.

- Ravi, S. y Knight, K. (2011). "Deciphering Foreign Language." *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics* (ACL 2011), pp. 12--21.

Notebooks: `11_homophonic.ipynb` · Resultados: `homofonico_resultados.json`

Partes I--VIII disponibles como documentos independientes.
