# PARTE II

**Fundamentos matemáticos**

> *Esta parte desarrolla las herramientas matemáticas que usa el análisis. Para cada una se explica qué mide, por qué esa medida es útil para estudiar el Voynich, y cómo se calcula en la práctica. No se requieren conocimientos matemáticos previos más allá de la aritmética básica.*


| **Capítulo** | **Herramienta**                               | **Pregunta que responde**                                                   |
|--------------|-----------------------------------------------|-----------------------------------------------------------------------------|
|              |                                               |                                                                             |
| **5**        | **Entropía e información mutua de Shannon**   | ¿Cuánta incertidumbre tiene el texto? ¿Cuánto predice la posición el glifo? |
|              |                                               |                                                                             |
| **6**        | **Tests de permutación y p-valores**          | ¿Podría el patrón observado aparecer por azar?                              |
|              |                                               |                                                                             |
| **7**        | **Chi-cuadrado y divergencia Jensen-Shannon** | ¿Son distintas dos distribuciones de frecuencias?                           |
|              |                                               |                                                                             |
| **8**        | **Cadenas de Markov y spectral gap**          | ¿Cómo se propagan las dependencias entre glifos?                            |
|              |                                               |                                                                             |
| **9**        | **Redes neuronales, huella estadística, distancia ponderada y sensibilidad** | ¿Qué mecanismo generativo reproduce la huella del Voynich? ¿Es robusto el resultado? |
|              |                                               |                                                                             |
| **10**       | **Optimización combinatoria e inferencia bayesiana** | ¿Con qué lengua candidata es más compatible el mapping silábico del Voynich? |


# Capítulo 5. Entropía e información mutua de Shannon

## 5.1 El problema de medir la incertidumbre

Imagine que tiene que adivinar el siguiente símbolo en una secuencia. Si la secuencia es completamente aleatoria, cada símbolo es igualmente probable y su tarea es imposible de hacer mejor que el azar. Si la secuencia tiene estructura, algunos símbolos son más probables que otros en cada contexto, y puede hacerlo mejor. La teoría de la información de Claude Shannon (1948) nació precisamente para cuantificar cuánta incertidumbre existe en una fuente de información y cuánta desaparece cuando se observa el contexto.

Shannon era un matemático e ingeniero de los Laboratorios Bell que trabajaba en el problema de transmitir mensajes de forma eficiente por canales con ruido. Para resolverlo, necesitaba una medida de cuánta información contiene un mensaje. Su solución fue la entropía, una función que tiene exactamente las propiedades intuitivas que uno esperaría de una medida de incertidumbre.

## 5.2 Entropía: midiendo la incertidumbre

### 5.2.1 La idea intuitiva

Piense en lanzar una moneda. Si la moneda es justa, cara y cruz son igualmente probables: hay máxima incertidumbre sobre el resultado. Si la moneda está trucada y sale cara el 99% de las veces, hay poca incertidumbre: casi siempre sabemos qué va a salir. Un dado de seis caras equilibrado tiene más incertidumbre que la moneda, porque hay seis posibilidades en lugar de dos.

Shannon formalizó esta intuición en una función que llamó entropía, tomando prestado el nombre de la termodinámica por la similitud matemática entre ambas cantidades. La entropía de una distribución de probabilidades mide cuánta incertidumbre media hay cuando se observa un símbolo de esa distribución.


> **Definición de entropía de Shannon**
>
> Dada una distribución de probabilidad sobre N símbolos posibles, donde el símbolo i tiene probabilidad p_i, la entropía H se define como: H = −Σ p_i · log₂(p_i) La suma recorre todos los símbolos posibles. La función log₂ usa logaritmos en base 2, lo que hace que la entropía se mida en bits. El signo negativo garantiza que el resultado sea siempre positivo o cero.


### 5.2.2 Por qué funciona esta fórmula

La fórmula puede parecer arbitraria al principio. Para entender por qué tiene sentido, pensemos en qué propiedades queremos que tenga una medida de incertidumbre:

-   Si todos los símbolos son igualmente probables (máxima incertidumbre), la entropía debe ser máxima.

-   Si un símbolo tiene probabilidad 1 (certeza absoluta), la entropía debe ser 0.

-   Si añadimos un símbolo imposible (probabilidad 0), la entropía no debe cambiar.

-   Si tenemos dos fuentes independientes, la entropía de la combinación debe ser la suma de las entropías individuales.

La función −p·log₂(p) satisface exactamente estas cuatro propiedades. Cuando p=1, el log₂(1)=0 y el término es 0. Cuando p es muy pequeño pero positivo, el término también es pequeño (p tiende a 0 más rápido que log₂(p) tiende a infinito). La suma ponderada produce una cantidad que es máxima cuando todos los p_i son iguales.


> **Ejemplo numérico: el alfabeto del Voynich**
>
> El Voynich tiene 166 glifos distintos. Si todos fueran igualmente frecuentes, la entropía sería log₂(166) ≈ 7.37 bits. Pero en realidad los glifos tienen frecuencias muy distintas: A1 aparece miles de veces, mientras que glifos como Ys o Yp aparecen menos de 100 veces. Esta desigualdad reduce la entropía real. El corpus del Voynich tiene una entropía H₀ ≈ 4.14 bits, significativamente por debajo del máximo teórico.


### 5.2.3 Los bits como unidad

La elección de la base 2 para el logaritmo hace que la entropía se mida en bits. Un bit es la cantidad de información de un lanzamiento de moneda justa: hay dos opciones, 0 o 1, y cada una tiene probabilidad 1/2. La fórmula da −(1/2)·log₂(1/2)−(1/2)·log₂(1/2) = 1 bit, exactamente.

Una entropía de 4.14 bits significa que, en promedio, se necesitan aproximadamente 4.14 bits de información para especificar cuál glifo del Voynich viene a continuación, asumiendo que conocemos solo la distribución global de frecuencias pero no el contexto. Para comparar: el latín medieval tiene H₀ ≈ 4.12 bits (similar al Voynich porque también tiene un alfabeto de tamaño parecido con distribución no uniforme).

## 5.3 Entropía condicional: el papel del contexto

### 5.3.1 De la entropía global a la entropía condicional

La entropía que acabamos de describir mide la incertidumbre media de un símbolo cuando no sabemos nada sobre su contexto. Pero en un texto real, el símbolo anterior (o los N anteriores) nos da información sobre el siguiente. En español, después de \'q\' casi siempre viene \'u\'. La entropía condicional mide cuánta incertidumbre queda sobre el siguiente símbolo cuando conocemos los N anteriores.

La entropía condicional de orden N, que escribimos H_N, se define como la incertidumbre media del símbolo en la posición t+1, dado que conocemos los N símbolos anteriores (posiciones t-N+1 a t). Matemáticamente:

> **H_N = −Σ P(contexto, símbolo) · log₂ P(símbolo \| contexto)** *(Entropía condicional de orden N)*

donde la suma recorre todos los pares (contexto de longitud N, símbolo siguiente) que aparecen en el corpus.

### 5.3.2 Una ley fundamental: la entropía condicional no puede crecer

Existe una propiedad matemática fundamental que toda entropía condicional debe respetar: H_N ≤ H\_{N-1} para todo N. En palabras: conocer más contexto nunca puede aumentar la incertidumbre. Esto tiene sentido intuitivamente: si ya sabías los últimos 3 glifos y ahora te digo también el cuarto anterior, tienes más información, no menos.

Esta propiedad es una de las razones por las que detectamos el error en nuestra primera versión del código. Cuando el parser producía un vocabulario inflado de 9.762 tokens, los cálculos de entropía violaban esta ley: H₁ \> H₀, lo que es matemáticamente imposible. Fue la señal de que algo estaba mal en los datos, no en las matemáticas.


> **La monotonicidad como prueba de corrección**
>
> Si en cualquier análisis de entropía condicional se observa que H_N \> H\_{N-1} para algún N, hay casi con certeza un error en los datos o en el estimador. Esta propiedad matemática funciona como una prueba de sanidad automática: los resultados del bloque C del análisis incluyen una verificación explícita de monotonicidad antes de interpretar cualquier resultado.


### 5.3.3 Cómo se calcula en la práctica y el problema de los datos escasos

Calcular H_N en la práctica requiere estimar P(símbolo \| contexto) contando cuántas veces cada símbolo sigue a cada contexto posible en el corpus. Para N=1 esto es sencillo: hay 166 glifos posibles como contexto y 166 como símbolo siguiente, así que necesitamos estimar 166×166 = 27.556 probabilidades.

Para N=2, el contexto tiene 166² = 27.556 posibles pares, y para N=3 hay 166³ ≈ 4.6 millones. El problema es que nuestro corpus tiene solo \~157.000 glifos. Para N=3, la mayoría de los contextos posibles nunca aparecen en el texto, y su probabilidad estimada sería 0 si no aplicamos ninguna corrección.

Este problema se llama el problema de los datos escasos (data sparsity en inglés), y hay varias técnicas para manejarlo. La más simple es el suavizado de Laplace, que añade 1 a todos los conteos, incluidos los cero. El problema es que con un vocabulario grande (9.762 tokens falsos en la versión errónea), añadir 1 a miles de celdas vacías introduce más ruido que señal. Con el vocabulario correcto de 166 tokens, el suavizado es proporcional y bien comportado.

Para el análisis de entropía condicional de este trabajo (Bloque C), usamos el estimador Witten-Bell, que es más robusto que Laplace para vocabularios moderados. La idea del estimador Witten-Bell es que la probabilidad de ver un símbolo nuevo en un contexto dado es proporcional al número de tipos distintos de símbolos que ya se han visto en ese contexto, no a un 1 fijo.

## 5.4 Información mutua: midiendo la dependencia

### 5.4.1 La pregunta que responde la información mutua

La entropía mide incertidumbre absoluta. La información mutua mide cuánta incertidumbre sobre una variable se reduce cuando conocemos otra. Formalmente, la información mutua I(X;Y) entre dos variables aleatorias X e Y mide cuántos bits de información comparten.

En el contexto del análisis del Voynich, usamos la información mutua para responder una pregunta específica: ¿cuánta información comparte el glifo con su posición dentro de la palabra (inicio, medio, final)? Si la respuesta es mucha, significa que los glifos no se distribuyen aleatoriamente a lo largo de la palabra: algunos prefieren el inicio, otros el final. Esto es exactamente la firma de un sistema con morfología.

> **I(X ; Y) = Σ P(x, y) · log₂ \[ P(x, y) / (P(x) · P(y)) \]** *(Información mutua)*

donde X es el glifo, Y es la posición (inicio/medio/final), y la suma recorre todos los pares (glifo, posición) que aparecen en el corpus.

### 5.4.2 Interpretación: cuándo es grande o pequeña

Cuando X e Y son independientes, P(x,y) = P(x)·P(y), el logaritmo es log₂(1) = 0, y la información mutua es 0. Esto significa que conocer el glifo no dice nada sobre su posición y viceversa. Si los glifos se distribuyeran uniformemente entre inicio, medio y final de palabra, la MI sería 0.

Cuando existe dependencia, los pares frecuentes tienen P(x,y) \> P(x)·P(y), el logaritmo es positivo, y contribuyen positivamente a la MI. Los pares infrecuentes tienen lo contrario, pero el peso P(x,y) los hace contribuir poco. El resultado neto es positivo y tanto mayor cuanto más fuerte sea la dependencia.


| **Corpus / sistema**          | **MI posicional** | **Interpretación**                                                              |
|-------------------------------|-------------------|---------------------------------------------------------------------------------|
|                               |                   |                                                                                 |
| Texto completamente aleatorio | **≈ 0.00 bits**   | Los glifos no tienen posición preferida                                         |
|                               |                   |                                                                                 |
| Inglés (Pride & Prejudice)    | **0.232 bits**    | Estructura débil: los prefijos y sufijos ingleses son moderadamente predecibles |
|                               |                   |                                                                                 |
| **Voynich (corpus completo)** | **0.658 bits**    | Estructura fuerte: los glifos tienen posiciones muy preferidas                  |
|                               |                   |                                                                                 |
| Slot probabilístico p=0.75    | **0.821 bits**    | Similar al Voynich: cada slot tiene 75% de prob. de su morfema canónico         |
|                               |                   |                                                                                 |
| Slot rígido (morfología fija) | **1.585 bits**    | Máximo teórico: cada glifo aparece exclusivamente en una posición               |


La MI del Voynich (0.658 bits) está claramente por encima de una lengua natural típica como el inglés (0.232 bits) y claramente por debajo de un sistema de slot perfectamente rígido (1.585 bits). Esto coloca al Voynich en una zona intermedia compatible con un sistema morfológico flexible: hay preferencias posicionales fuertes pero no absolutas.

### 5.4.3 La información mutua de bigrama

Además de la MI entre glifo y posición, también calculamos la información mutua entre glifos adyacentes dentro de una misma palabra: I(glifo_i ; glifo\_{i+1}). Esto mide cuánta información comparte un glifo con el que le sigue inmediatamente.

Un valor alto de MI de bigrama indica que las transiciones entre glifos no son libres: ciertos glifos tienden a ir seguidos de ciertos otros. Esto también es una firma de morfología: las raíces tienen sus propias estructuras de bigramas, distintas a las de los prefijos y los sufijos.

Para el Voynich, la MI de bigrama es 1.681 bits, comparable a la de un sistema de slot probabilístico con p≈0.92. Los bigramas más informativos son D1→A1 (contribución 0.1321 bits), A3→G1 (0.1212 bits) y A1→Q1 (0.1164 bits). Estos bigramas son tan frecuentes y predecibles que solos explican un tercio de toda la MI de bigrama del corpus.

## 5.5 Entropía condicional y la forma de U del Voynich

### 5.5.1 Qué esperamos ver en una lengua natural

En una lengua natural, la curva H_N (entropía de orden N para N=0,1,2,3,4) decrece monótonamente: cada glifo de contexto adicional reduce la incertidumbre. En latín, H₀=4.12 bits, H₁=3.46 bits, H₂=2.95 bits, H₃=2.59 bits, H₄=2.46 bits. La reducción es suave y continua porque las palabras latinas son largas y las dependencias dentro de la palabra se extienden varios caracteres.

En un cifrado monoalfabético como el César, la curva es casi idéntica a la de la lengua cifrada (latín en nuestro caso), porque el cifrado es solo una permutación de los símbolos y no cambia las estadísticas de las transiciones. En un cifrado polialfabético como el Vigenère, la curva decrece más lentamente porque la clave mezcla los patrones, pero sigue siendo monótona.

### 5.5.2 La anomalía del Voynich

La curva del Voynich tiene una forma completamente distinta a todos los sistemas de control. H₀=4.14, H₁=2.96: el contexto de un glifo reduce la entropía en más de un bit. Hasta aquí parece una lengua normal con dependencias fuertes de bigramas. Pero H₂=2.99, H₃=3.32, H₄=3.77: la entropía sube de nuevo. La curva tiene forma de U.

Este patrón, que llamamos \'rebote\', tiene una interpretación morfológica precisa: el bigrama predice bien el siguiente glifo (H₁ bajo), pero el contexto de 2-4 glifos ya cruza la frontera de palabra y pierde poder predictivo. Esto ocurre porque las palabras del Voynich son muy cortas (media de \~4.2 glifos) y las dependencias están confinadas dentro de la palabra. Un contexto de 3-4 glifos abarca casi siempre el final de una palabra y el inicio de la siguiente, donde la correlación es mínima.


| **Corpus / sistema** | **H₀** | **H₁**    | **H₂**    | **H₃**    | **H₄**    |     |
|----------------------|--------|-----------|-----------|-----------|-----------|-----|
|                      |        |           |           |           |           |     |
| **Voynich**          | 4.141  | **2.961** | **2.990** | **3.317** | **3.774** |     |
|                      |        |           |           |           |           |     |
| Latín                | 4.122  | 3.462     | 2.948     | 2.588     | 2.459     |     |
|                      |        |           |           |           |           |     |
| César                | 4.121  | 3.463     | 2.951     | 2.593     | 2.466     |     |
|                      |        |           |           |           |           |     |
| Vigenère             | 4.616  | 4.324     | 3.593     | 3.116     | 2.894     |     |


> *Los valores en naranja para el Voynich son el \'rebote\': H₂, H₃ y H₄ son mayores que H₁. El valor verde (H₁=2.961) es el mínimo de la curva, alcanzado con solo 1 glifo de contexto.*


> **El rebote como firma morfológica única**
>
> El rebote de la curva entrópica (forma de U) es el hallazgo estadístico más singular del análisis. Ninguno de los corpus de control ---latín, César, Vigenère--- tiene este comportamiento. El rebote indica que las dependencias del Voynich son estrictamente locales: muy fuertes dentro de la palabra (especialmente en bigramas) pero inexistentes entre palabras. Esto es incompatible con cifrados de sustitución, que heredarían el alcance de las dependencias de la lengua cifrada.


## 5.6 La entropía y el estimador Witten-Bell

Como mencionamos antes, estimar entropías condicionales de orden alto requiere manejar el problema de los contextos no vistos. El estimador Witten-Bell funciona de la siguiente manera: cuando aparece un contexto que se ha visto antes, usa la frecuencia relativa de cada símbolo observado en ese contexto. Para los símbolos que nunca han seguido a ese contexto, distribuye una probabilidad de \'escape\' proporcional al número de tipos distintos de símbolos que sí aparecen en ese contexto.

La intuición es que si un contexto es seguido por muchos símbolos distintos (contexto \'promiscuo\'), hay más posibilidad de que aparezca un símbolo nuevo; si un contexto siempre va seguido del mismo símbolo (contexto \'rígido\'), la probabilidad de ver algo nuevo es baja. Esto es más razonable que dar la misma probabilidad de escape a todos los contextos, como hace Laplace.


> **Resumen del capítulo**
>
> -   La entropía de Shannon H mide la incertidumbre media de un símbolo en una distribución. Se mide en bits. Una distribución uniforme tiene entropía máxima; una distribución donde un símbolo domina tiene entropía baja.
>
> -   La entropía condicional H_N mide la incertidumbre que queda sobre el siguiente símbolo cuando conocemos los N anteriores. H_N siempre es ≤ H\_{N-1}: más contexto nunca puede aumentar la incertidumbre.
>
> -   La información mutua I(X;Y) mide cuánta información comparten dos variables. En el Voynich se usa para medir cuánto predice el glifo su posición en la palabra (MI posicional = 0.658 bits) y cuánto predice el glifo el siguiente glifo (MI bigrama = 1.681 bits).
>
> -   La curva H₀→H₄ del Voynich tiene forma de U (rebote de 0.813 bits), a diferencia del latín, el César y el Vigenère, que son monótonamente decrecientes. Esto es la firma estadística más distintiva del sistema de escritura del Voynich.


# Capítulo 6. Tests de permutación y p-valores

## 6.1 El problema fundamental de la inferencia estadística

Suponga que calcula la información mutua posicional del Voynich y obtiene 0.658 bits. ¿Es un valor alto? ¿Es evidencia de que el texto tiene estructura? Comparado con el inglés (0.232 bits) parece alto. Pero tal vez el Voynich sea simplemente aleatorio con algunas fluctuaciones que por casualidad producen un 0.658.

Este es el problema central de la inferencia estadística: distinguir entre un patrón real y una fluctuación aleatoria. La respuesta matemática a este problema es el test de hipótesis, y el instrumento clave es el p-valor. Antes de explicar qué es un p-valor, necesitamos entender qué pregunta responde, porque es una de las nociones más malinterpretadas de toda la estadística.

## 6.2 La hipótesis nula y el p-valor

### 6.2.1 La hipótesis nula

En un test de hipótesis estadístico siempre se parte de una hipótesis nula, que representa la explicación más aburrida de los datos: que no pasa nada interesante. En nuestro caso, la hipótesis nula para el test de MI posicional es:

> *\"H₀: los glifos del Voynich se distribuyen aleatoriamente entre las posiciones inicio, medio y final de palabra. La MI observada de 0.658 bits es simplemente el resultado de la fluctuación estadística de una distribución aleatoria.\"*

Si la hipótesis nula fuera verdadera, ¿qué MI esperaríamos observar? No exactamente 0 bits, porque incluso los datos aleatorios tienen fluctuaciones. Observaríamos una MI positiva pero pequeña, y esa MI fluctuaría de una muestra a otra alrededor de algún valor esperado cercano a 0.

### 6.2.2 ¿Qué es exactamente el p-valor?

El p-valor es la probabilidad de observar un resultado tan extremo como el que observamos (o más extremo), asumiendo que la hipótesis nula es verdadera. Un p-valor pequeño significa: \'si el texto fuera aleatorio, sería muy improbable obtener este resultado\'. Un p-valor grande significa: \'este resultado es compatible con el azar\'.

La convención habitual en ciencias es rechazar la hipótesis nula cuando el p-valor es menor que 0.05 (5%) o, para resultados más robustos, 0.001 (0.1%). Estos umbrales son arbitrarios pero están bien establecidos como estándares de la comunidad científica.


> **Lo que el p-valor NO dice**
>
> El p-valor NO es la probabilidad de que la hipótesis nula sea verdadera. No dice \'hay un 0.1% de probabilidad de que el texto sea aleatorio\'. Lo que dice es \'si el texto fuera aleatorio, habría solo un 0.1% de probabilidad de observar una MI ≥ 0.658\'. La diferencia es sutil pero crucial. Para convertir p-valores en probabilidades de hipótesis se necesita el teorema de Bayes, que requiere un conocimiento previo que generalmente no tenemos.


## 6.3 Tests de permutación: un enfoque sin supuestos

### 6.3.1 El problema con los tests paramétricos clásicos

Los tests estadísticos clásicos (como el test chi-cuadrado, que veremos en el capítulo siguiente) asumen que los datos siguen una distribución matemática conocida. El chi-cuadrado, por ejemplo, asume que las frecuencias observadas siguen una distribución chi-cuadrado bajo la hipótesis nula. Este supuesto puede ser incorrecto para textos lingüísticos, donde las palabras no son independientes entre sí.

Los tests de permutación evitan este problema construyendo la distribución de referencia directamente desde los datos, sin asumir ninguna distribución paramétrica. Son una familia de tests no paramétricos particularmente adecuados para análisis lingüísticos.

### 6.3.2 Cómo funciona un test de permutación

La idea es simple y elegante. En lugar de calcular la distribución teórica de la estadística bajo la hipótesis nula, la generamos empíricamente destruyendo el patrón que queremos testar y viendo qué valores produce la estadística en ausencia de ese patrón.

Para el test de MI posicional del Voynich, el procedimiento es:

1.  Calcular la MI posicional del corpus original: 0.658 bits. Este es el valor observado.

2.  Crear una copia del corpus donde, en cada palabra, los glifos se mezclan aleatoriamente entre sí (permutación intra-palabra). Esto destruye el orden dentro de la palabra pero preserva exactamente qué glifos hay en qué palabras.

3.  Calcular la MI posicional del corpus permutado.

4.  Repetir los pasos 2-3 un gran número de veces (en nuestro análisis, n=1.000 permutaciones).

5.  La colección de 1.000 valores de MI de corpus permutados es la distribución de referencia bajo la hipótesis nula.

6.  El p-valor es la proporción de permutaciones que producen una MI igual o mayor que el valor observado (0.658).


> **Por qué la permutación intra-palabra**
>
> La permutación mezcla los glifos dentro de cada palabra, no entre palabras. Esto es importante porque queremos testar específicamente si hay estructura posicional dentro de la palabra. Si mezcláramros glifos entre palabras, también destruiríamos la distribución de frecuencias de glifos por posición de palabra (inicio de palabra vs. final de palabra), lo que introduciría un tipo de destrucción diferente al que nos interesa. La permutación intra-palabra es la perturbación mínima que destruye el orden dentro de la palabra preservando todo lo demás.


### 6.3.3 Resultados del test de permutación en el Voynich

Con n=1.000 permutaciones con semillas fijas (para reproducibilidad), los resultados son:

-   MI observada: 0.658 bits

-   MI media de corpus permutados: 0.198 bits

-   Desviación estándar de MI en permutaciones: 0.004 bits

-   p-valor: 0.000 (ninguna de las 1.000 permutaciones producen una MI ≥ 0.658)

Un p-valor de 0.000 con n=1.000 permutaciones significa que el valor observado es al menos 100 veces más extremo que el peor resultado obtenido en las permutaciones. En términos del número de desviaciones estándar, el valor observado está a (0.658 − 0.198) / 0.004 = 115 desviaciones estándar de la media de la distribución nula. Este es un resultado extraordinariamente significativo.


> **La importancia de testar todos los glifos**
>
> Además del test global de MI, el análisis aplica el test de permutación individualmente a cada uno de los 166 glifos del vocabulario. El resultado es que 32 glifos (de los que tienen frecuencia ≥ 20, para garantizar potencia estadística) muestran preferencias posicionales con p \< 0.001. Entre ellos, D1 aparece en posición de inicio de palabra el 98.9% de las veces, una preferencia extraordinariamente rígida. Esto es la firma computacional de un prefijo.


## 6.4 La validación por holdout como test de permutación temporal

El Bloque B del análisis aplica una variante conceptual del test de permutación: en lugar de permutar los glifos dentro del corpus, divide el corpus en dos mitades independientes (folios pares como entrenamiento, folios impares como test) y verifica que los patrones descubiertos en la primera mitad se replican en la segunda.

La motivación es evitar la circularidad analítica: si descubrimos que D1 es un prefijo usando todos los datos y luego validamos este hallazgo en los mismos datos, estamos viendo lo que queremos ver. El holdout garantiza que la validación se hace sobre datos que no participaron en el descubrimiento del patrón.

Los resultados del holdout (116 folios de entrenamiento, 110 de test, proporciones de palabras y glifos similares en ambos splits) muestran que las preferencias posicionales de todos los glifos significativos se replican en el conjunto de test con alta consistencia. Esto descarta que los resultados sean artefactos de los folios específicos usados para el análisis.


> **Resumen del capítulo**
>
> -   La hipótesis nula es la explicación aburrida de los datos: que no hay patrón real, solo fluctuación aleatoria.
>
> -   El p-valor es la probabilidad de ver un resultado tan extremo como el observado si la hipótesis nula fuera verdadera. NO es la probabilidad de que la hipótesis nula sea verdadera.
>
> -   Los tests de permutación construyen la distribución de referencia destruyendo el patrón que se testea (permutando el orden de los glifos dentro de cada palabra) y calculando la estadística en el corpus destruido, repetido n=1.000 veces.
>
> -   El test de MI posicional del Voynich produce p-valor=0 con n=1.000 permutaciones: el valor observado (0.658 bits) está a 115 desviaciones estándar de la media de la distribución nula (0.198 bits). Es uno de los resultados más significativos del análisis.
>
> -   El holdout por folio (folios pares / folios impares) es un segundo nivel de validación que descarta la circularidad analítica.


# Capítulo 7. Chi-cuadrado y divergencia Jensen-Shannon

## 7.1 El problema de comparar distribuciones

Muchas preguntas interesantes del análisis del Voynich tienen la forma: \'¿son estas dos distribuciones distintas?\'. Por ejemplo: ¿es la distribución de glifos en la sección herbal distinta a la de la sección biológica? Si el Voynich es un texto con contenido semánticamente diferenciado, esperaríamos que sí. Si es texto aleatorio o un cifrado uniforme, esperaríamos que no.

Dos herramientas matemáticas distintas atacan este problema desde ángulos complementarios. El test chi-cuadrado de Pearson responde con un p-valor: \'¿son estas distribuciones significativamente distintas?\'. La divergencia Jensen-Shannon cuantifica cuánto de distintas son, produciendo un número entre 0 (idénticas) y 1 (máximamente distintas).

## 7.2 El test chi-cuadrado

### 7.2.1 La idea intuitiva

El test chi-cuadrado compara lo que observamos con lo que esperaríamos si las distribuciones fueran iguales. Si la distribución de glifos en la sección herbal y en la sección biológica fueran idénticas, cada glifo debería aparecer en cada sección en proporción a su frecuencia global. El chi-cuadrado mide cuánto se desvía lo observado de esta expectativa.

Piense en un ejemplo simple: si la sección herbal tiene el 38.5% de todas las palabras del corpus y la sección biológica tiene el 18.2%, entonces esperaríamos que el glifo A1 aparezca el 38.5% de sus ocurrencias totales en herbal y el 18.2% en biológica. Si en realidad aparece el 45% en herbal y el 12% en biológica, hay una desviación. El chi-cuadrado suma todas estas desviaciones al cuadrado (normalizadas) para los 166 glifos y las 4 secciones.

### 7.2.2 La fórmula y su interpretación

> **χ² = Σ (Observado − Esperado)² / Esperado** *(Test chi-cuadrado de Pearson)*

donde la suma recorre todas las celdas de la tabla de contingencia (todas las combinaciones glifo × sección). El valor χ² resultante sigue aproximadamente una distribución chi-cuadrado con (número de glifos − 1) × (número de secciones − 1) grados de libertad, de la que se obtiene el p-valor.

Para el Voynich, la tabla de contingencia tiene 166 glifos × 4 secciones = 664 celdas, pero algunas se fusionan porque tienen pocos datos. El resultado es χ² = 6.626,75 con p ≈ 0 (esencialmente cero: el valor exacto excede la precisión numérica del ordenador). Los 468 grados de libertad corresponden aproximadamente a (166−1) × (4−1).


> **Interpretación del resultado chi-cuadrado**
>
> χ² = 6.626,75 con p ≈ 0 y 468 grados de libertad significa que la distribución de glifos es estadísticamente distinta entre las cuatro secciones con una certeza que excede cualquier umbral convencional. Para contextualizar: si las distribuciones fueran idénticas, esperaríamos un χ² de aproximadamente 468 (igual a los grados de libertad). Obtenemos 6.626, que es más de 14 veces el valor esperado bajo la hipótesis nula. Este resultado solo es posible si hay diferencias sustantivas en el vocabulario de glifos entre secciones.


### 7.2.3 Limitaciones del chi-cuadrado

El test chi-cuadrado tiene dos limitaciones importantes. Primera, requiere que las frecuencias esperadas sean suficientemente grandes (regla empírica: ≥ 5 en cada celda), de lo contrario la aproximación a la distribución chi-cuadrado es imprecisa. Por eso excluimos las secciones astronómica y zodíaco del análisis: tienen muy pocas palabras y muchos glifos tendrían frecuencias esperadas \< 5.

Segunda, el chi-cuadrado solo dice si hay diferencia, no cuánta ni dónde. Para cuantificar la magnitud de las diferencias entre pares de secciones, necesitamos la divergencia Jensen-Shannon.

## 7.3 La divergencia Jensen-Shannon

### 7.3.1 La divergencia Kullback-Leibler como punto de partida

Para entender la Jensen-Shannon (JSD), conviene empezar por la divergencia Kullback-Leibler (KL), que es el bloque de construcción básico. La divergencia KL de la distribución Q respecto a P mide cuánta información extra se necesita para describir símbolos de P usando Q en lugar de P:

> **D_KL(P \|\| Q) = Σ P(x) · log₂ \[ P(x) / Q(x) \]** *(Divergencia Kullback-Leibler)*

Un valor de D_KL = 0 significa que P y Q son idénticas. Un valor grande significa que Q es una mala aproximación de P. La KL tiene un problema: no es simétrica. D_KL(P \|\| Q) ≠ D_KL(Q \|\| P), así que no puede usarse directamente como una \'distancia\' entre distribuciones.

### 7.3.2 La divergencia Jensen-Shannon

La JSD resuelve el problema de asimetría de la KL promediando las dos direcciones a través de una distribución intermedia M = (P + Q) / 2:

> **JSD(P, Q) = ½ · D_KL(P \|\| M) + ½ · D_KL(Q \|\| M)** *(Divergencia Jensen-Shannon)*

El resultado está entre 0 y 1 (cuando se usa logaritmo en base 2). JSD = 0 significa que P y Q son idénticas. JSD = 1 significa que P y Q no tienen ningún elemento en común: son máximamente distintas.

La JSD es además la raíz cuadrada de una distancia métrica verdadera entre distribuciones de probabilidad, lo que la hace matemáticamente muy bien comportada para comparaciones múltiples.

### 7.3.3 Resultados de la JSD entre secciones del Voynich

Calculamos la JSD entre las distribuciones de palabras (top-500 palabras más frecuentes) de cada par de secciones:


|                  | **herbal** | **biologica** | **farmaceutica** |
|------------------|------------|---------------|------------------|
|                  |            |               |                  |
| **biologica**    | 0.316      | ---           | ---              |
|                  |            |               |                  |
| **farmaceutica** | 0.252      | 0.469         | ---              |
|                  |            |               |                  |
| **recetas**      | 0.217      | 0.168         | 0.384            |


> *Verde: JSD \< 0.25 (secciones similares). Rojo: JSD \> 0.40 (secciones muy distintas). JSD medio entre todos los pares: 0.301.*

El patrón de distancias tiene coherencia temática: biológica y recetas son las secciones más similares (JSD = 0.168), quizás porque ambas son densas en texto con vocabulario funcional parecido. Farmacéutica y biológica son las más distintas (JSD = 0.469), posiblemente porque la sección farmacéutica contiene más nombres de ingredientes específicos.

Un sistema de cifrado uniforme (que no preservara el contenido semántico) produciría JSD ≈ 0 entre todas las secciones, porque el cifrado mezclaría los glifos de forma independiente del contenido. El hecho de que obtengamos valores de JSD entre 0.17 y 0.47 es incompatible con un cifrado uniforme y consistente con vocabulario especializado por sección.

## 7.4 El clasificador logístico como validación adicional

Una forma alternativa de comprobar si las secciones son distinguibles es entrenar un clasificador automático: dado el perfil de glifos de una palabra, ¿puede un algoritmo predecir en qué sección fue escrita?

Usamos una regresión logística (uno de los clasificadores más simples y más interpretables de aprendizaje automático) con los siguientes ingredientes: para cada palabra, calculamos la frecuencia relativa de cada glifo y la longitud de la palabra, produciendo un vector de características de 167 números. La regresión logística aprende a asignar una sección a cada vector.

La validación se hace con 5-fold cross-validation estratificada: el corpus se divide en 5 partes iguales, el clasificador se entrena en 4 y se evalúa en la 5ª, rotando las partes. Esto garantiza que el clasificador no \'ve\' los datos de evaluación durante el entrenamiento.


> **Resultado del clasificador**
>
> Accuracy media = 0.429 ± 0.012 (5-fold CV). El baseline aleatorio es 0.250 (4 secciones de igual tamaño). El clasificador supera el azar en un 72% relativo. La baja varianza entre folds (±0.012) confirma estabilidad. Este resultado significa que el perfil de glifos de una palabra contiene información real sobre la sección temática a la que pertenece.


Una accuracy del 43% puede parecer baja en términos absolutos, pero hay que tenerla en contexto. El clasificador trabaja con palabras individuales de solo \~4 glifos de media, usando solo la frecuencia de glifos como features. Con tan poca información por ejemplo, es notable que supere el azar tan consistentemente.


> **Resumen del capítulo**
>
> -   El test chi-cuadrado compara distribuciones de frecuencias contando cuánto se desvían las frecuencias observadas de las esperadas bajo la hipótesis de igualdad. Para el Voynich, χ² = 6.626,75 con p ≈ 0: las distribuciones de glifos son significativamente distintas entre secciones.
>
> -   La divergencia Jensen-Shannon cuantifica cuánto de distintas son dos distribuciones, con valores entre 0 (idénticas) y 1 (sin solapamiento). El JSD medio entre secciones del Voynich es 0.301, con variación coherente temáticamente.
>
> -   Un clasificador logístico entrenado solo con el perfil de glifos de cada palabra predice la sección correctamente el 43% de las veces (baseline: 25%). Esto confirma que el vocabulario de glifos es temáticamente especializado.
>
> -   Estos tres resultados conjuntos son incompatibles con un cifrado uniforme, que no preservaría la especialización de vocabulario entre secciones.


# Capítulo 8. Cadenas de Markov y spectral gap

## 8.1 Modelar secuencias con memoria

Hasta ahora hemos estudiado propiedades estáticas del texto: distribuciones de frecuencias, preferencias posicionales. Pero el lenguaje tiene una propiedad dinámica esencial: lo que viene a continuación depende de lo que acaba de ocurrir. Un modelo matemático que capture esta dependencia es la cadena de Markov.

Una cadena de Markov es un modelo probabilístico de una secuencia donde la probabilidad del próximo estado depende solo del estado actual, no de toda la historia anterior. Para un texto, el \'estado\' es el glifo actual y la \'transición\' es qué glifo viene a continuación. Esto es una simplificación (en realidad el contexto relevante puede ser más largo), pero captura las dependencias de primer orden y produce resultados analizables.

## 8.2 La matriz de transición

### 8.2.1 Construcción

Para construir la cadena de Markov de un texto, contamos cuántas veces cada glifo va seguido de cada otro glifo dentro de la misma palabra. Esto produce una matriz M de dimensiones (número de glifos) × (número de glifos), donde M\[i\]\[j\] es el número de veces que el glifo i va seguido del glifo j.

Normalizando cada fila por la suma de la fila, obtenemos la matriz de transición estocástica P, donde P\[i\]\[j\] es la probabilidad de que el glifo i vaya seguido del glifo j. Cada fila suma 1 (como debe hacerlo una distribución de probabilidad).

Para el Voynich, la matriz tiene dimensiones 166 × 166 = 27.556 celdas. La mayoría de las celdas tienen valor 0 (la mayoría de los pares de glifos nunca aparecen juntos), pero los pares frecuentes tienen probabilidades sustanciales. Por ejemplo, P\[D1\]\[A1\] ≈ 0.85: cuando aparece D1, hay un 85% de probabilidad de que el siguiente glifo sea A1.

### 8.2.2 Los eigenvalores de la matriz de transición

La herramienta matemática que usamos para analizar la matriz de transición es la descomposición en eigenvalores (también llamados valores propios). Los eigenvalores de una matriz son números especiales que resumen sus propiedades de transformación de formas que son difíciles de ver mirando los elementos individuales.

Para una matriz de transición estocástica de una cadena de Markov ergódica (que puede visitar todos los estados), siempre hay un eigenvalor dominante λ₁ = 1. Este eigenvalor corresponde a la distribución estacionaria de la cadena: la distribución de probabilidad a la que converge la cadena si se deja evolucionar indefinidamente.


> **Importante: λ₁ ≈ 1 no es una anomalía**
>
> En los primeros análisis de este trabajo (notebook 02_permutation_bootstrap.ipynb, celda 44), el eigenvalor dominante de la matriz de transición del Voynich era 0.9997, muy cercano a 1. Esto se interpretó inicialmente como algo notable. En realidad es matemáticamente inevitable en toda cadena de Markov ergódica. Lo que importa para el análisis no es λ₁ sino la diferencia entre λ₁ y el segundo eigenvalor más grande \|λ₂\|, que se llama el spectral gap.


## 8.3 El spectral gap y la velocidad de mezcla

### 8.3.1 ¿Qué mide el spectral gap?

El spectral gap δ = λ₁ − \|λ₂\| mide la velocidad a la que la cadena de Markov \'olvida\' su estado inicial y converge a la distribución estacionaria. Esta velocidad de convergencia es lo que en la teoría de Markov se llama mixing time (tiempo de mezcla).

Intuitivamente: un spectral gap grande significa que la cadena mezcla rápido, es decir, el estado actual predice poco sobre los estados futuros después de unos pocos pasos. Un spectral gap pequeño significa que la cadena tarda muchos pasos en \'olvidar\' su estado inicial, lo que implica dependencias de largo alcance.

> **δ = λ₁ − \|λ₂\| ; t_mezcla ≈ 1 / δ** *(Spectral gap y tiempo de mezcla)*

### 8.3.2 Relación con la estructura del lenguaje

En el contexto del análisis del Voynich, el spectral gap captura qué tan lejos se propagan las dependencias entre glifos. Un sistema con morfología local fuerte (prefijos que se combinan con raíces que se combinan con sufijos) tiene dependencias confinadas dentro de la palabra. Una vez que la cadena cruza la frontera de palabra, la correlación desaparece y la mezcla es rápida dentro del nuevo contexto.

Un cifrado de sustitución monoalfabético (César) hereda exactamente el spectral gap de la lengua cifrada: cambiar A→N, B→O, etc. no cambia la velocidad de mezcla, solo renombra los estados. Un cifrado polialfabético (Vigenère) tiene un spectral gap mayor (mezcla más rápido) porque la clave mezcla los patrones.


| **Corpus**     | **Vocab** | **λ₂**    | **Gap δ** | **t_mezcla** |
|----------------|-----------|-----------|-----------|--------------|
|                |           |           |           |              |
| **Voynich**    | 166       | **0.459** | **0.541** | 1.8 pasos    |
|                |           |           |           |              |
| Latín medieval | 26        | **0.342** | **0.658** | 1.5 pasos    |
|                |           |           |           |              |
| César (ROT-13) | 26        | **0.342** | **0.658** | 1.5 pasos    |
|                |           |           |           |              |
| Vigenère       | 26        | **0.145** | **0.855** | 1.2 pasos    |


El spectral gap del Voynich (0.541) es menor que el del latín (0.658), lo que significa dependencias ligeramente más persistentes entre glifos. Esto es consistente con la morfología local fuerte observada en el análisis de MI posicional: los glifos del Voynich tienen más \'memoria\' de sus vecinos que los caracteres del latín.


> **El Voynich no es un cifrado César ni Vigenère**
>
> Si el Voynich fuera un cifrado César sobre latín, tendría exactamente el mismo spectral gap que el latín (0.658), porque el cifrado solo renombra los glifos. Si fuera un cifrado Vigenère, tendría un gap mayor (0.855). El Voynich tiene un gap de 0.541, significativamente distinto de ambos. Este resultado, combinado con la forma de U de la entropía condicional y la MI posicional alta, constituye evidencia convergente de que el Voynich no es un cifrado de sustitución sobre latín.


## 8.4 El eigenvector de λ₂ como diagnóstico morfológico

Además del eigenvalor λ₂, el eigenvector correspondiente (el vector v₂ tal que M·v₂ = λ₂·v₂) tiene una interpretación morfológica interesante. Los glifos con mayor peso en v₂ son los que más \'diferencian\' los dos grupos de estados que más tardan en mezclarse.

Para el Voynich, los glifos con mayor peso en v₂ son Ys (0.114), Yp (0.049), Yn (0.019), Xd (0.018), Tf (0.017). Estos son glifos de frecuencia media-baja que aparecen en posiciones específicas y tienen bigramas muy predecibles. Su presencia en v₂ es la firma matemática de glifos con distribución posicional marcada, coherente con la función de marcadores morfológicos (indicadores de sección, clase, o derivación).

## 8.5 La relación entre el spectral gap y la forma de U

Existe una conexión profunda entre el spectral gap (Bloque D) y la forma de U de la curva entrópica (Bloque C/F). Ambas miden, desde ángulos distintos, el alcance de las dependencias entre glifos.

La forma de U dice: el contexto de 1 glifo predice bien el siguiente (H₁ bajo), pero el contexto de 3-4 glifos no predice mejor que el de 1 (H₂-H₄ suben). El spectral gap dice: la cadena mezcla en \~1.8 pasos, es decir, después de 2 glifos el estado actual ya predice poco sobre el estado futuro.

Son dos caras de la misma moneda: ambas apuntan a un sistema donde las dependencias son fuertes dentro de la escala de la palabra (1-2 glifos) pero se atenúan rápidamente. Esta coherencia entre dos herramientas matemáticas independientes es evidencia acumulativa de que estamos midiendo una propiedad real del sistema, no un artefacto del método.


> **Resumen del capítulo**
>
> -   Una cadena de Markov modela una secuencia donde la probabilidad del próximo elemento depende solo del actual. La matriz de transición P recoge estas probabilidades para todos los pares de glifos.
>
> -   Los eigenvalores de la matriz de transición resumen sus propiedades dinámicas. El eigenvalor dominante λ₁ = 1 es inevitable en toda cadena ergódica; lo relevante es el spectral gap δ = λ₁ − \|λ₂\|.
>
> -   El spectral gap mide la velocidad de mezcla: gap grande → mezcla rápida → dependencias cortas. El tiempo de mezcla aproximado es t ≈ 1/δ pasos.
>
> -   El Voynich tiene δ = 0.541 (mezcla en \~1.8 pasos), distinto del latín (0.658, \~1.5 pasos) y muy distinto del Vigenère (0.855, \~1.2 pasos). Un cifrado César sobre latín tendría exactamente el gap del latín.
>
> -   El spectral gap y la forma de U de la entropía condicional son herramientas independientes que convergen en la misma conclusión: las dependencias del Voynich son fuertes y locales, confinadas al alcance de 1-2 glifos.


# Capítulo 9. Redes neuronales y Transformers: intuición

## 9.1 Por qué un modelo de lenguaje neuronal

Los cuatro bloques de análisis anteriores (A, B, C/F, D, E) son tests estadísticos sobre propiedades concretas del texto. Complementamos este análisis con un modelo de lenguaje neuronal: un Transformer de pequeño tamaño entrenado sobre el corpus del Voynich. El modelo no es el análisis principal, pero aporta dos cosas que los tests estadísticos no pueden dar: una representación aprendida de los glifos (los embeddings) y una medida de perplexidad que captura la estructura global del texto de forma integrada.

Este capítulo explica la intuición detrás de los componentes del modelo, sin entrar en las derivaciones matemáticas completas. El objetivo es que el lector entienda qué aprende el modelo y qué nos dice ese aprendizaje sobre el Voynich.

## 9.2 Embeddings: representar símbolos como vectores

### 9.2.1 El problema de representar símbolos discretos

Los algoritmos de aprendizaje automático trabajan con números, no con símbolos. Para aplicarlos a glifos del Voynich, necesitamos una forma de convertir cada glifo en un vector numérico. La representación más simple sería un vector de 166 ceros con un solo 1 en la posición del glifo (one-hot encoding). El problema es que esta representación trata todos los glifos como igualmente distintos entre sí: A1 no está más cerca de A2 que de Q1.

Los embeddings son una representación aprendida donde cada glifo se mapea a un vector de números reales de dimensión baja (32 en nuestro modelo). La clave es que el aprendizaje ajusta estos vectores de forma que glifos que se comportan de forma similar en el texto (aparecen en los mismos contextos, predicen los mismos sucesores) tengan vectores parecidos.

### 9.2.2 Lo que revelan los embeddings del Voynich

Aplicamos Análisis de Componentes Principales (PCA) a los embeddings aprendidos para ver cuánta estructura hay en el espacio de representación. El PCA es una técnica que encuentra las direcciones de mayor varianza en un conjunto de vectores, revelando la estructura de bajo rango subyacente.

El modelo v2 (n_embd=32, el que usamos en el análisis final) necesita solo 7 componentes PCA para explicar el 50% de la varianza, comparado con 15 en el modelo v1 (n_embd=128). Esto significa que las representaciones del modelo v2 son más compactas y especializadas: la información relevante está concentrada en menos dimensiones.

El grafo de similitud coseno entre embeddings, donde conectamos con aristas los glifos con similitud coseno \> 0.15, produce 3 comunidades detectadas con el algoritmo Louvain que se corresponden aproximadamente con las categorías morfológicas: sufijos vocálicos, prefijos/raíces, y glifos de función libre. Esta correspondencia entre la representación aprendida y la estructura morfológica observada estadísticamente es una validación cruzada independiente.


> **La convergencia PPMI--Embeddings**
>
> El grafo construido desde coocurrencia estadística pura (PPMI: Positive Pointwise Mutual Information) y el grafo construido desde similitud de embeddings del Transformer producen comunidades similares. Dos métodos completamente distintos ---uno puramente estadístico, el otro basado en aprendizaje--- llegan a la misma agrupación de glifos. Esta convergencia es la validación más robusta del análisis morfológico: no es un artefacto de ninguno de los dos métodos.


## 9.3 La arquitectura Transformer: intuición

### 9.3.1 El problema del contexto variable

Un modelo de lenguaje debe predecir el siguiente glifo dado un contexto de longitud variable. Las arquitecturas clásicas (n-gramas, LSTM) tienen dificultades para capturar dependencias de largo alcance o lo hacen de forma computacionalmente costosa. El Transformer, propuesto por Vaswani y colaboradores en 2017, resuelve este problema con el mecanismo de self-attention.

### 9.3.2 Self-attention: cada glifo mira a todos los demás

La idea central del Transformer es que para predecir el siguiente glifo, el modelo puede mirar a cualquier posición del contexto con diferente grado de atención, aprendiendo qué partes del contexto son relevantes para cada predicción.

Para cada glifo en el contexto, el modelo calcula tres vectores: Query (Q, \'lo que estoy buscando\'), Key (K, \'lo que yo ofrezco\') y Value (V, \'la información que tengo\'). La atención que el glifo actual presta a cada posición anterior es proporcional al producto escalar de su Query con el Key de esa posición. Las Values de todas las posiciones se combinan ponderadas por estas atenciones.

> **Atención(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V** *(Mecanismo de self-attention)*

donde d_k es la dimensión de las Keys, que normaliza el producto escalar para evitar gradientes extremadamente pequeños durante el entrenamiento.

### 9.3.3 Hiperparámetros del modelo VoynichLM v2

El modelo que entrenamos tiene las siguientes características:


| **Parámetro**            | **Valor**         | **Por qué este valor**                               |
|--------------------------|-------------------|------------------------------------------------------|
|                          |                   |                                                      |
| Vocabulario (vocab_size) | **167**           | 166 glifos + separador de palabra \'.\'              |
|                          |                   |                                                      |
| Dimensión de embedding   | **32**            | Ratio 0.19× vocab --- fuerza especialización         |
|                          |                   |                                                      |
| Cabezas de atención      | **4**             | 4 cabezas × 8 dims/cabeza = 32 total                 |
|                          |                   |                                                      |
| Bloques Transformer      | **3**             | Mínimo con capacidad compositiva                     |
|                          |                   |                                                      |
| Longitud de contexto     | **64**            | \~15 palabras de contexto                            |
|                          |                   |                                                      |
| Parámetros totales       | **50.791**        | \~3.2× el tamaño del vocabulario --- sin sobreajuste |
|                          |                   |                                                      |
| Loss final (train / val) | **1.561 / 1.562** | Diferencia \< 0.001 --- sin memorización             |


El dato más importante de la tabla es que la loss de validación (1.562) es prácticamente idéntica a la de entrenamiento (1.561) después de 8.000 iteraciones. Esto significa que el modelo generaliza: no ha memorizado el corpus sino que ha aprendido sus regularidades. Un modelo que memoriza tendría una loss de entrenamiento mucho más baja que la de validación.

## 9.4 La perplexidad como medida de cuánto predice el modelo

La perplexidad es la métrica estándar para evaluar modelos de lenguaje. Se define como dos elevado a la cross-entropy loss del modelo: PPL = 2\^(loss). Una perplexidad de 2 significa que el modelo es tan bueno prediciendo el siguiente glifo como si tuviera que elegir entre 2 opciones equiprobables en cada paso. Una perplexidad de 167 significa que el modelo no es mejor que elegir aleatoriamente entre todos los glifos.

La loss del modelo VoynichLM v2 es 1.562 bits, lo que corresponde a una perplexidad de 2\^1.562 ≈ 2.95. Esto significa que, en promedio, el modelo predice el siguiente glifo como si tuviera que elegir entre aproximadamente 3 opciones. Considerando que hay 166 glifos posibles, esto es una comprensión notable de la estructura del texto.

Para comparar, la entropía de orden 0 del corpus es 4.14 bits (perplexidad ≈ 17.7). El modelo, usando contextos de hasta 64 glifos, reduce la incertidumbre de 17.7 a 2.95: absorbe más del 80% de la incertidumbre original. Esto es consistente con un texto con estructura fuerte y predecible, no con texto aleatorio.


> **Resumen del capítulo**
>
> -   Los embeddings representan cada glifo como un vector en un espacio de 32 dimensiones, de forma que glifos con comportamientos similares en el texto tienen vectores parecidos. El grafo de similitud coseno entre embeddings produce 3 comunidades que se corresponden con categorías morfológicas.
>
> -   La convergencia entre el grafo de coocurrencia (PPMI) y el grafo de embeddings valida ambos métodos de forma cruzada: dos enfoques independientes obtienen la misma estructura.
>
> -   El mecanismo de self-attention del Transformer permite al modelo mirar a cualquier posición del contexto con diferente peso, aprendiendo qué partes del contexto son relevantes para cada predicción.
>
> -   El modelo VoynichLM v2 (50.791 parámetros, 3 bloques, n_embd=32) converge a loss=1.562 bits (perplexidad ≈ 2.95) sin overfitting: train loss ≈ val loss a lo largo de todo el entrenamiento.
>
> -   Una perplexidad de 2.95 sobre 166 glifos posibles significa que el modelo absorbe más del 80% de la incertidumbre del corpus, capturando la estructura morfológica del sistema de escritura.



# Capítulo 10. Optimización combinatoria e inferencia bayesiana

El Capítulo 9 cerró la fase de *caracterización*: hemos medido la huella estadística del Voynich y determinado que un silabario probabilístico es el mecanismo generativo más plausible. Pero caracterizar no es descifrar. Si las sílabas del Voynich codifican una lengua real, ¿cuál? Este capítulo desarrolla las herramientas matemáticas del descifrado bayesiano a nivel de sílaba: cómo encontrar la asignación óptima entre sílabas Voynich y sílabas de una lengua candidata, cómo explorar el espacio de soluciones, y cómo medir la confianza en el resultado.

El enfoque se basa en el trabajo de Ravi y Knight (2011), que demostraron que el descifrado de sustitución puede formularse como un problema de optimización bayesiana. Aquí adaptamos su método para operar a nivel de sílaba en lugar de carácter, incorporando restricciones de clase posicional (onset, nuclear, coda) y una función de scoring multi-componente.

## 10.1 El problema de la asignación: matching bipartito

### 10.1.1 La formulación

El descifrado de sustitución a nivel silábico se reduce a encontrar una función biyectiva *f* que mapee cada sílaba Voynich *sv* a una sílaba de la lengua candidata *st*, de forma que el corpus Voynich "traducido" sea lo más natural posible bajo el modelo de lengua del candidato. Si el inventario Voynich tiene *n* tipos silábicos funcionales y el candidato tiene *m*, la función *f* selecciona uno de los *m!/(m−n)!* matchings posibles ---un número astronómico incluso para inventarios modestos.

Una restricción crucial reduce este espacio: las sílabas Voynich están clasificadas en cuatro clases posicionales (onset, nuclear, coda, free), y solo se permite mapear sílabas de la misma clase. Si una sílaba Voynich es onset, solo puede mapearse a una sílaba onset de la lengua candidata. Esto particiona el problema en cuatro sub-problemas independientes, cada uno mucho más pequeño que el problema completo.

### 10.1.2 El algoritmo húngaro (Kuhn-Munkres)

El algoritmo húngaro resuelve el problema de asignación óptima en tiempo polinomial. Dado un conjunto de agentes (sílabas Voynich) y un conjunto de tareas (sílabas candidatas) con un coste asociado a cada asignación, encuentra la asignación uno-a-uno que minimiza el coste total.

Formalmente, dada una matriz de costes C de dimensiones *n* × *m* donde C\[i\]\[j\] es el coste de asignar la sílaba Voynich *i* a la sílaba candidata *j*, el algoritmo encuentra la permutación σ que minimiza:

> *coste_total = Σᵢ C\[i, σ(i)\]*

El algoritmo opera en O(n³) operaciones, lo que lo hace tratable incluso para inventarios de cientos de sílabas. Fue desarrollado independientemente por Harold Kuhn (1955) y James Munkres (1957), basándose en trabajo previo de los matemáticos húngaros Dénes König y Jenő Egerváry.

### 10.1.3 Vectores distribucionales y distancia coseno

Para construir la matriz de costes del algoritmo húngaro, representamos cada sílaba (tanto Voynich como candidata) como un vector distribucional de 7 dimensiones:

1. Frecuencia normalizada en el corpus
2. Proporción de aparición en posición de inicio de palabra
3. Proporción en posición media
4. Proporción en posición final
5. Entropía forward (log₂ del número de contextos derechos distintos)
6. Número de contextos izquierdos
7. Número de contextos derechos

La distancia coseno entre dos vectores *u* y *v* mide la diferencia angular entre ellos:

> *d_cos(u, v) = 1 − (u · v) / (\|\|u\|\| · \|\|v\|\|)*

donde *u · v* es el producto escalar y \|\|u\|\| es la norma euclidiana. Un valor de 0 indica vectores idénticos en dirección; un valor de 1 indica vectores ortogonales. La distancia coseno es ideal aquí porque es invariante a la escala: dos sílabas con el mismo *perfil distribucional* pero distinta frecuencia absoluta tendrán distancia coseno baja.

El resultado del algoritmo húngaro es una asignación inicial que respeta las clases posicionales y empareja sílabas con distribuciones estadísticas similares. Esta asignación es un punto de partida razonable, pero no tiene en cuenta la estructura secuencial del texto (qué sílabas tienden a aparecer juntas). Para incorporar esa información, necesitamos optimización iterativa.

## 10.2 Expectation-Maximization (EM)

### 10.2.1 La idea

El algoritmo EM (Dempster, Laird y Rubin, 1977) es una técnica iterativa para optimizar funciones en las que hay variables latentes ---variables que no observamos directamente pero que influyen en los datos. En el descifrado, la variable latente es el mapping: no sabemos qué sílaba Voynich corresponde a qué sílaba de la lengua candidata, pero si lo supiéramos, podríamos evaluar qué tan bien la "traducción" resultante se ajusta al modelo de lengua del candidato.

EM alterna entre dos pasos:

**E-step (expectation)**: dado el mapping actual, "traducir" el corpus Voynich a la lengua candidata y evaluar su naturalidad bajo el modelo de lengua bigrama. Esta evaluación produce un score que mide la calidad del mapping.

**M-step (maximization)**: buscar modificaciones del mapping que mejoren el score. En la implementación adaptada a nuestro problema, esto consiste en probar swaps de pares de sílabas dentro de la misma clase posicional y aceptar los que mejoran el score.

### 10.2.2 Convergencia

El EM tiene una propiedad fundamental: el score nunca empeora entre iteraciones. Cada M-step solo acepta cambios que mejoran el score, por lo que la secuencia de scores es monótonamente no decreciente. El algoritmo converge cuando ningún swap mejora el score ---es decir, cuando se alcanza un óptimo local.

> **El EM encuentra un óptimo local, no necesariamente el global.** El resultado depende de la inicialización, lo cual justifica usar el algoritmo húngaro como punto de partida (que ya proporciona una solución razonable) y luego refinar con MCMC.

La convergencia se detecta con un criterio de paciencia: si el score no mejora en *P* iteraciones consecutivas, el algoritmo se detiene. En la práctica, con P = 5 y 30 swaps aleatorios por clase por iteración, el EM converge típicamente en 10-20 iteraciones.

## 10.3 MCMC y Metropolis-Hastings

### 10.3.1 El problema del EM: óptimos locales

El EM está condenado a quedarse atrapado en el óptimo local más cercano. Si el espacio de soluciones tiene muchos óptimos locales ---y con cientos de sílabas los tiene---, el EM podría converger a una solución mediocre simplemente porque no hay ningún swap individual que la mejore, aunque una combinación de varios swaps simultáneos sí lo haría.

Aquí es donde entra la inferencia bayesiana por cadenas de Markov Monte Carlo (MCMC). En lugar de buscar *un* mapping óptimo, MCMC muestrea de la distribución posterior sobre mappings, explorando tanto las regiones de alto score como las transiciones entre ellas.

### 10.3.2 El algoritmo Metropolis-Hastings

El algoritmo Metropolis-Hastings (Metropolis et al., 1953; Hastings, 1970) es el caballo de batalla de la inferencia bayesiana computacional. Construye una cadena de Markov cuya distribución estacionaria es la distribución posterior que nos interesa. La cadena explora el espacio de soluciones haciendo propuestas aleatorias y aceptándolas o rechazándolas según una regla precisa.

El ciclo es:

1. **Estado actual**: un mapping completo sílaba Voynich → sílaba candidata, con score *S_actual*.
2. **Propuesta**: swap de dos sílabas Voynich aleatorias de la misma clase posicional, produciendo un mapping candidato con score *S_propuesta*.
3. **Decisión**: aceptar la propuesta con probabilidad:

> *α = min(1, exp((S_propuesta − S_actual) / T))*

Si *S_propuesta > S_actual* (la propuesta mejora), se acepta siempre (α = 1). Si *S_propuesta < S_actual* (la propuesta empeora), se acepta con probabilidad exponencialmente decreciente en la magnitud del empeoramiento. La temperatura *T* controla cuánto empeoramiento se tolera: con *T* alta, se aceptan empeoramientos grandes; con *T* baja, solo se aceptan mejoras o empeoramientos minúsculos.

Esta regla de aceptación es la clave de MCMC: permite escapar de óptimos locales aceptando temporalmente soluciones peores, para explorar después regiones del espacio que podrían contener soluciones mejores.

### 10.3.3 Tasa de aceptación como diagnóstico

La fracción de propuestas aceptadas (tasa de aceptación) es un indicador clave de la salud de la cadena. Una tasa demasiado alta (> 60%) indica que la cadena no está explorando eficientemente: casi todas las propuestas se aceptan, lo que sugiere que la temperatura es demasiado alta o que los swaps son demasiado conservadores. Una tasa demasiado baja (< 10%) indica que la cadena está atascada: casi todas las propuestas se rechazan y la exploración es mínima. El rango óptimo está entre el 15% y el 40%, dependiendo de la dimensionalidad del problema.

## 10.4 Simulated annealing: el schedule de temperatura

### 10.4.1 La analogía metalúrgica

El simulated annealing (recocido simulado) toma su nombre de la metalurgia: cuando se enfría un metal lentamente desde alta temperatura, los átomos tienen tiempo de reorganizarse en la configuración cristalina de mínima energía. Si se enfría demasiado rápido, los átomos quedan atrapados en configuraciones desordenadas (metaestables). La idea matemática es idéntica: empezar con una temperatura alta que permita exploración amplia, y reducirla gradualmente para que la cadena se concentre en las regiones de alto score.

### 10.4.2 El schedule geométrico

El schedule de temperatura más común ---y el usado en nuestro análisis--- es el geométrico:

> *T(t) = T_start · (T_end / T_start)^(t / (N − 1))*

donde *t* es la iteración actual (de 0 a N−1), *T_start* es la temperatura inicial y *T_end* es la temperatura final. La temperatura decae exponencialmente, pasando la mitad del tiempo total en la fase de alta temperatura (exploración) y la otra mitad en la fase de baja temperatura (explotación).

Con *T_start = 1.0* y *T_end = 0.01*, el schedule produce:

| Fase | Iteraciones | Temperatura | Comportamiento |
|------|-------------|-------------|----------------|
| Exploración | primeras ~40% | T > 0.1 | Acepta empeoramientos de hasta ~10% del score |
| Transición | ~40-70% | 0.01 < T < 0.1 | Acepta solo empeoramientos pequeños |
| Explotación | últimas ~30% | T ≈ 0.01 | Prácticamente solo acepta mejoras |

La ventaja del annealing sobre MCMC a temperatura fija es que combina la exploración global (fase caliente) con la optimización local (fase fría). La desventaja es que el resultado depende del schedule: un enfriamiento demasiado rápido atrapa la cadena en un óptimo local, mientras que uno demasiado lento desperdicia tiempo de cómputo en exploración innecesaria.

## 10.5 Multi-chain MCMC y el diagnóstico Gelman-Rubin

### 10.5.1 Por qué múltiples cadenas

Una sola cadena MCMC puede quedarse atrapada en un modo de la distribución posterior sin explorar otros modos igualmente probables. La solución estándar es ejecutar múltiples cadenas independientes, cada una con una semilla aleatoria distinta. Si todas las cadenas convergen a la misma región del espacio, tenemos confianza en que la posterior está bien muestreada. Si convergen a regiones distintas, hay evidencia de multimodalidad y la posterior de una sola cadena sería engañosa.

Además de la diversificación, las múltiples cadenas multiplican el número de muestras efectivas de la posterior. Con *k* cadenas de *N* iteraciones y un periodo de burn-in de *B*, el número total de muestras post-burn-in es *k · (N − B)*. En nuestro análisis, 4 cadenas de 15.000 iteraciones con burn-in de 3.000 producen 4 × 12.000 = 48.000 muestras, frente a las 4.000 de una sola cadena de 5.000 iteraciones con burn-in de 1.000.

### 10.5.2 Burn-in y thinning

Las primeras iteraciones de cada cadena MCMC están contaminadas por la inicialización: la cadena aún no ha convergido a la distribución estacionaria y sus muestras no son representativas de la posterior. El periodo de burn-in descarta estas muestras iniciales.

¿Cuántas iteraciones descartar? En la práctica, se examina la traza del score (score vs. iteración) y se identifica el punto a partir del cual la cadena ha alcanzado un nivel estable. Un criterio conservador es descartar el primer 20% de las iteraciones.

El thinning es una técnica complementaria: almacenar solo cada *k*-ésima muestra en lugar de todas. Con 15.000 iteraciones × 4 cadenas × ~500 sílabas por mapping, almacenar todos los mappings consumiría cientos de megabytes. Un factor de thinning de 5 reduce el consumo de memoria a una quinta parte sin pérdida significativa de información, porque las muestras consecutivas de MCMC están altamente correlacionadas.

### 10.5.3 El diagnóstico R-hat (Gelman-Rubin)

El diagnóstico R-hat (Gelman y Rubin, 1992) es el criterio estándar para determinar si las cadenas MCMC han convergido. La idea es comparar la varianza *entre* cadenas con la varianza *dentro* de cada cadena. Si las cadenas han convergido a la misma distribución, ambas varianzas deberían ser similares.

Para cada sílaba Voynich *sv*, se define un indicador binario: ¿la cadena asigna *sv* a su target MAP (el target más probable a posteriori) en esta iteración? Con este indicador, se calculan:

**Varianza within (W)**: la media de las varianzas de cada cadena individual. Mide cuánto fluctúa el indicador *dentro* de cada cadena.

**Varianza between (B)**: la varianza de las medias de las cadenas. Mide cuánto difieren las cadenas *entre sí*.

El estimador de la varianza posterior es:

> *V̂ = (1 − 1/n) · W + (1/n) · B*

donde *n* es el número de muestras por cadena. El diagnóstico R-hat es:

> *R̂ = √(V̂ / W)*

**Interpretación**:

- *R̂ = 1.0*: convergencia perfecta. La varianza between es cero; todas las cadenas muestrean la misma distribución.
- *R̂ < 1.1*: convergencia aceptable. El estándar de la comunidad bayesiana (Gelman et al., 2013).
- *R̂ > 1.1*: convergencia insuficiente. Las cadenas no han explorado la misma región del espacio; se necesitan más iteraciones o una reparametrización.
- *R̂ → ∞*: las cadenas están en regiones completamente distintas (varianza within ≈ 0, varianza between > 0).

El R-hat se calcula por sílaba, no globalmente. Esto permite identificar qué sílabas tienen mapping estable (R̂ ≈ 1.0) y cuáles permanecen ambiguas (R̂ > 1.1). Un resumen útil es el porcentaje de sílabas con R̂ < 1.1: si este porcentaje es alto (>70%), la mayoría del mapping ha convergido.

## 10.6 La función de scoring multi-componente

### 10.6.1 Tres componentes complementarios

Tanto el EM como el MCMC necesitan una función que evalúe la calidad de un mapping. Nuestra función combina tres componentes que miden aspectos diferentes de la compatibilidad lingüística:

**Score LM (peso 2.0)**: log-verosimilitud promedio del corpus Voynich mapeado bajo el modelo de lengua bigrama del candidato. Mide si las secuencias silábicas resultantes "suenan" como la lengua candidata.

**Score paradigma (peso 1.5)**: combina tres sub-métricas evaluadas mediante la divergencia Jensen-Shannon (Capítulo 7): (a) JSD entre las distribuciones de tamaño de paradigma Voynich y candidato, (b) fracción de sufijos mapeados que existen en el inventario del candidato, y (c) similitud de los coeficientes de Gini de los paradigmas. Mide si la morfología del Voynich se preserva bajo el mapping.

**Score armonía (peso 1.0)**: JSD entre las distribuciones conjuntas de pares (nuclear, coda) en el Voynich mapeado y en el candidato. Mide si las dependencias fonológicas intra-palabra son compatibles.

> *S_total = 2.0 · S_LM + 1.5 · S_paradigma + 1.0 · S_armonía*

### 10.6.2 El coeficiente de Gini

El coeficiente de Gini, usado dentro del score de paradigma, mide la desigualdad de una distribución. Originalmente desarrollado por el estadístico italiano Corrado Gini (1912) para medir la desigualdad económica, se aplica aquí a la distribución de frecuencias de sufijos dentro de un paradigma.

Para un vector ordenado de frecuencias (c₁ ≤ c₂ ≤ ... ≤ cₙ), el Gini se calcula como:

> *G = (2 · Σᵢ i · cᵢ) / (n · Σᵢ cᵢ) − (n + 1) / n*

El valor 0 indica distribución perfectamente uniforme (todos los sufijos igualmente frecuentes); el valor 1 indica concentración total (un solo sufijo acumula toda la frecuencia). El Voynich tiene un Gini de 0.49, a medio camino: los paradigmas tienen variedad real de sufijos pero con unas pocas terminaciones dominantes. Si un mapping produce paradigmas con Gini muy distinto (demasiado uniforme o demasiado concentrado), el score de paradigma lo penaliza.

## 10.7 La distribución posterior y la confianza del mapping

### 10.7.1 De las muestras MCMC a la posterior

Cada muestra de la cadena MCMC (después del burn-in) es un mapping completo. Para cada sílaba Voynich *sv*, podemos contar cuántas veces fue asignada a cada sílaba candidata *st* a lo largo de todas las muestras. La fracción de muestras en las que *sv* → *st* es una estimación de la probabilidad posterior P(*st* | *sv*, datos).

La sílaba candidata con mayor probabilidad posterior es el target MAP (maximum a posteriori). La probabilidad posterior del target MAP es la confianza del mapping para esa sílaba: una confianza de 0.95 significa que el 95% de las muestras MCMC asignaron la misma sílaba candidata, indicando alta certeza. Una confianza de 0.30 significa que las muestras se reparten entre múltiples candidatos, indicando ambigüedad.

### 10.7.2 Umbrales de confianza

La distribución de confianzas sobre todas las sílabas resume la calidad global del mapping:

| Umbral | Interpretación |
|--------|----------------|
| >90% | Mapping prácticamente seguro |
| >70% | Mapping fiable; útil para reconstrucción de texto |
| >50% | Mapping probable; el target MAP es más probable que cualquier alternativa individual |
| <50% | Mapping ambiguo; múltiples candidatos tienen probabilidad similar |

Una mediana de confianza baja (por ejemplo, ~45%) no significa necesariamente que el mapping sea malo: puede significar que la posterior es multimodal (hay familias de mappings igualmente buenos) o que el número de muestras efectivas es insuficiente. La mejora de single-chain a multi-chain MCMC incrementa las muestras efectivas y, con ello, la resolución de la distribución posterior.


> **Resumen del capítulo**
>
> -   El descifrado bayesiano silábico busca la asignación sílaba Voynich → sílaba candidata que maximice la compatibilidad con el modelo de lengua del candidato, respetando las restricciones de clase posicional.
>
> -   El **algoritmo húngaro** (O(n³)) proporciona la asignación inicial óptima basada en la distancia coseno entre vectores distribucionales de 7 dimensiones.
>
> -   **EM** refina iterativamente la asignación: el E-step evalúa el corpus mapeado bajo el LM target, el M-step aplica swaps que mejoran el score. Converge a un óptimo local.
>
> -   **MCMC Metropolis-Hastings** escapa de óptimos locales aceptando empeoramientos con probabilidad *exp(ΔS/T)*. La tasa de aceptación (15-40%) indica la salud de la cadena.
>
> -   **Simulated annealing** enfría la temperatura geométricamente de *T_start* a *T_end*, combinando exploración global (fase caliente) con optimización local (fase fría).
>
> -   **Multi-chain MCMC** ejecuta *k* cadenas independientes para multiplicar las muestras efectivas (k × (N − burn-in)) y diversificar la exploración.
>
> -   El **diagnóstico R-hat** (Gelman-Rubin) compara varianza between/within entre cadenas: R̂ < 1.1 indica convergencia aceptable.
>
> -   El **coeficiente de Gini** mide la desigualdad de sufijos en los paradigmas: 0 = uniforme, 1 = un solo sufijo dominante. El Voynich tiene Gini = 0.49.
>
> -   La **posterior** asigna una confianza por sílaba: la fracción de muestras MCMC que coinciden en el target MAP. Con 48.000 muestras efectivas (4 cadenas × 12.000 post-burn-in), la resolución es 12× superior a una sola cadena.


**Cierre de la Parte II**

Los seis capítulos de esta parte han construido el arsenal matemático completo que usaremos en el análisis. Cada herramienta ha sido presentada con tres elementos: qué mide en términos generales, por qué esa medida es útil para el problema del Voynich en particular, y qué nos dicen ya los primeros resultados numéricos.

Vale la pena detenerse a señalar la arquitectura de argumentación que emerge de estas herramientas. No son redundantes: cada una ilumina un ángulo distinto del mismo objeto.


| **Cap.** | **Herramienta**                  | **Ángulo que ilumina**                                          |
|----------|----------------------------------|-----------------------------------------------------------------|
|          |                                  |                                                                 |
| **5**    | **Entropía e información mutua** | Cuánta estructura hay y dónde está (posicional vs. secuencial)  |
|          |                                  |                                                                 |
| **6**    | **Tests de permutación**         | Si la estructura es real o podría ser una fluctuación aleatoria |
|          |                                  |                                                                 |
| **7**    | **Chi-cuadrado y JSD**           | Si la estructura varía con el contenido temático                |
|          |                                  |                                                                 |
| **8**    | **Cadenas de Markov**            | Qué tan lejos se propagan las dependencias entre glifos         |
|          |                                  |                                                                 |
| **9**    | **Transformer y embeddings**     | Qué representación interna es consistente con el corpus         |
|          |                                  |                                                                 |
| **10**   | **Optimización e inferencia bayesiana** | Con qué lengua candidata es más compatible el mapping silábico  |


## 9.5 La huella estadistica y la metrica de distancia

Los instrumentos matematicos desarrollados en esta parte ---entropia condicional, tests de permutacion, chi-cuadrado y divergencia Jensen-Shannon, cadenas de Markov, redes neuronales, y optimizacion bayesiana--- producen cada uno metricas numericas que caracterizan un corpus. El conjunto de estas metricas forma lo que denominamos la huella estadistica (fingerprint) del corpus: un vector en un espacio multidimensional que captura sus propiedades estructurales esenciales.

Para el Voynich, la huella estadistica incluye: la curva de entropia condicional H₀ a H₄ (que exhibe la forma de U descrita en la Seccion 5.5), las metricas derivadas de forma (rebote, decay), el spectral gap (Seccion 8.3), y las medidas de informacion mutua posicional y de bigrama (Seccion 5.4). Juntas, estas seis metricas definen un punto en un espacio de seis dimensiones que distingue al Voynich de todos los sistemas de control.

### 9.5.1 Distancia euclidea ponderada

Para cuantificar la similitud entre dos huellas estadisticas, empleamos la distancia euclidea ponderada:

*d(A, B) = √( Σᵢ wᵢ · (Aᵢ − Bᵢ)² )*

donde Aᵢ y Bᵢ son los componentes i-esimos de las huellas de los corpus A y B, y wᵢ es el peso asignado al componente i-esimo. La eleccion de pesos permite enfatizar las metricas con mayor poder discriminatorio.


| **Metrica**             **Peso (wᵢ)**           **Justificacion** |
|-------------------------------------------------------------------|

  Rebote                  3.0                     Propiedad mas distintiva del Voynich; unica entre todos los corpus probados

  Decay                   2.0                     Cuantifica la asimetria de la curva de entropia

  MI posicional           1.5                     Dependencia glifo-posicion en la palabra

  MI bigrama              1.5                     Dependencia entre glifos adyacentes

  Spectral gap            1.0                     Velocidad de mezcla de la cadena de Markov

|                                                                                                                              |
|------------------------------------------------------------------------------------------------------------------------------|
| rebote recibe el peso mas alto (w=3) porque es la propiedad mas distintiva del Voynich: ningun otro sistema probado ---ni le |

### 9.5.2 Modelos generativos como banco de pruebas

Una aplicacion directa de la huella estadistica es la metodologia de forward modeling: construir modelos generativos con mecanismos conocidos, generar corpus sinteticos a partir de cada modelo, calcular su huella estadistica, y medir la distancia al Voynich. El modelo cuya huella sea mas cercana sugiere el mecanismo mas plausible detras del manuscrito.

Esta metodologia invierte la direccion habitual del analisis criptografico: en lugar de intentar descomponer un texto cifrado existente, sintetizamos texto bajo hipotesis controladas y observamos cual reproduce mejor las propiedades estadisticas del original. Si un generador basado en un silabario probabilistico produce una huella cercana al Voynich, esto constituye evidencia a favor de que el manuscrito fue producido por un mecanismo de tipo silabico. El Capitulo 14 de la Parte III desarrolla esta metodologia con once modelos generativos ---siete propios y cuatro basados en hipotesis de la literatura (Rugg 2004, Timm y Schinner 2020, Hermes 2022, Greshko 2025).

### 9.5.3 Analisis de sensibilidad: correlacion de Spearman y muestreo Dirichlet

La eleccion de pesos en la distancia ponderada es subjetiva. Para verificar que las conclusiones son robustas a esta eleccion, el Capitulo 14 incluye un analisis de sensibilidad que utiliza dos herramientas matematicas adicionales.

**Correlacion de rango de Spearman.** La correlacion de Spearman (ρ) mide la asociacion monotona entre dos rankings. Dados dos vectores de rangos R y S de longitud n, se define como:

*ρ = 1 − (6 · Σ dᵢ²) / (n · (n² − 1))*

donde dᵢ = Rᵢ − Sᵢ es la diferencia de rangos del elemento i-esimo. El valor ρ = 1 indica rankings identicos; ρ = 0 indica ausencia de correlacion; ρ = −1 indica rankings invertidos. A diferencia de la correlacion de Pearson (que mide asociacion lineal entre valores), Spearman opera sobre los rangos ordinales y es insensible a transformaciones monotónicas de las distancias. Esto la hace ideal para evaluar si el *orden* del ranking se preserva cuando los pesos cambian, independientemente de cuanto cambien los valores absolutos de las distancias.

En nuestro analisis, calculamos ρ entre el ranking base (con los pesos elegidos) y el ranking producido por cada conjunto alternativo de pesos. Si ρ > 0.9 de forma consistente, el ranking es robusto: el modelo ganador no depende de la eleccion especifica de pesos.

**Distribucion de Dirichlet.** Para explorar el espacio de pesos de forma exhaustiva, generamos conjuntos de pesos aleatorios muestreados de una distribucion de Dirichlet simetrica. La distribucion de Dirichlet es una distribucion de probabilidad sobre vectores de k componentes positivos que suman 1. Con parametro de concentracion α = 1 (distribucion uniforme sobre el simplex), cada componente tiene la misma distribucion marginal y no hay preferencia por ningun peso particular.

Formalmente, si (x₁, ..., xₖ) ~ Dir(α₁, ..., αₖ), la densidad es:

*f(x₁, ..., xₖ) = [Γ(Σ αᵢ) / Π Γ(αᵢ)] · Π xᵢ^(αᵢ−1)*

donde Γ es la funcion gamma. Con α₁ = ... = αₖ = 1, todos los vectores de pesos en el simplex son igualmente probables. Los vectores se reescalan para mantener la magnitud total similar a la de los pesos base (suma ≈ 9).

Generando cientos de conjuntos de pesos Dirichlet y calculando el ranking bajo cada uno, obtenemos una distribucion empirica de ρ y una frecuencia de "victorias" para cada modelo: cuantas veces ocupa la primera posicion (top-1) o esta entre los tres primeros (top-3). Si un modelo domina el top-1 con frecuencia alta (>50%) bajo pesos completamente aleatorios, su posicion en el ranking no es un artefacto de la eleccion de pesos.

Cuando estas seis herramientas aplicadas sobre los mismos datos convergen en el mismo diagnóstico, la evidencia es mucho más robusta que si proviniera de una sola técnica. Esa convergencia ---o su ausencia--- es el núcleo argumental de las Partes III y IV.

*--- Continúa en la Parte III: Análisis y resultados ---*
