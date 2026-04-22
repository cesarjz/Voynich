ANÁLISIS COMPUTACIONAL DEL

# MANUSCRITO VOYNICH

*¿Lengua natural, cifrado o sistema artificial? Una investigación desde la teoría de la información, el aprendizaje automático y la estadística computacional*


| **Formato:**       | Trabajo de investigación                                                              |
|--------------------|---------------------------------------------------------------------------------------|
|                    |                                                                                       |
| **Idioma:**        | Español                                                                               |
|                    |                                                                                       |
| **Versión:**       | Parte I de XI --- Contexto e introducción                                            |
|                    |                                                                                       |
| **Corpus:**        | STA1 2.0 --- Manuscrito Voynich (37 087 palabras, 157 254 glifos)                     |
|                    |                                                                                       |
| **Herramientas:**  | Python 3.12 · PyTorch · scikit-learn · NumPy · NetworkX                               |
|                    |                                                                                       |
| **Código fuente:** | 01_statistical_fingerprint.ipynb · 02_permutation_bootstrap.ipynb · 03_entropy_spectral.ipynb · 04_multilingual_controls.ipynb · 05_generative_models.ipynb · 06_bayesian_syllabic.ipynb · 07_compositional.ipynb · 08_validation.ipynb · 09_constrained_em.ipynb |


*--- Parte I: Contexto e introducción ---*

# Prefacio

Este trabajo nació de una pregunta aparentemente simple: ¿puede una máquina decir algo útil sobre el texto más misterioso de la historia? La respuesta, como ocurre con todo lo interesante, resultó ser complicada.

El Manuscrito Voynich lleva más de un siglo resistiendo todos los intentos de descifrado. Criptógrafos, lingüistas, historiadores, matemáticos y entusiastas de todo el mundo han intentado leerlo. Algunos han afirmado haberlo descifrado. Ninguno ha convencido a la comunidad científica. Este trabajo no pretende descifrarlo tampoco. Lo que sí pretende es aplicar herramientas matemáticas y computacionales modernas para responder una pregunta más modesta pero más rigurosa: ¿qué tipo de sistema es el texto del Voynich? ¿Se comporta como una lengua natural? ¿Como un cifrado? ¿Como algo distinto?

El documento está escrito para un lector que puede tener formación en lingüística, en historia, o en estadística, pero no necesariamente en las tres. Por eso, cada herramienta matemática que se usa en el análisis se explica desde sus fundamentos: no el cómo se deriva su fórmula, sino qué mide, por qué esa medida es útil para nuestro problema, y qué nos dice su resultado concreto sobre el Voynich.

El código que produce todos los resultados de este trabajo está disponible en nueve notebooks de Python. Cada vez que se cita un número o un gráfico, se indica qué celda lo generó y cómo interpretarlo. La reproducibilidad no es un lujo académico, es la única forma de que los resultados sean realmente argumentos y no afirmaciones.

Este es el primer volumen de siete. Aquí se establece el contexto histórico y científico, se describe el corpus que se analiza y se plantea con precisión la pregunta de investigación. Los volúmenes siguientes desarrollan los fundamentos matemáticos (Parte II), los resultados del análisis (Parte III), la segmentación silábica (Parte IV), el descifrado bayesiano silábico (Parte V), el descifrado composicional (Parte VI) y la validación con restricciones gramaticales (Parte VII).

# Capítulo 1. El Manuscrito Voynich: historia y descripción

## 1.1 Descripción física

El Manuscrito Voynich es un libro manuscrito de pergamino que contiene aproximadamente 240 folios, aunque se cree que originalmente tenía más páginas, algunas de las cuales se han perdido. Su formato es pequeño, unos 23 por 16 centímetros, y está encuadernado en una cubierta de piel que probablemente no es la original. Actualmente se conserva en la Biblioteca Beinecke de Libros Raros y Manuscritos de la Universidad de Yale, donde está catalogado como MS 408.

La datación por radiocarbono, realizada en 2011 sobre muestras de pergamino, sitúa su creación entre 1404 y 1438. Esto lo ubica en el siglo XV, en el período del Renacimiento temprano. El texto está escrito con tinta de color marrón oscuro, con algunos añadidos en rojo. Las ilustraciones, que ocupan una parte considerable del volumen, incluyen plantas de aspecto fantástico o desconocido, diagramas astronómicos o astrológicos, figuras femeninas en lo que parecen ser piscinas o bañeras comunicadas por tubos, y tablas con estrellas y símbolos.

El sistema de escritura es completamente desconocido. No ha podido identificarse con ningún alfabeto conocido. Los símbolos, que en este trabajo llamaremos glifos, tienen una apariencia que evoca remotamente el latín medieval o el árabe, pero sin ser ninguno de los dos. Hay aproximadamente 25 a 30 glifos básicos, aunque dependiendo del sistema de transcripción utilizado el número varía. El texto se escribe de izquierda a derecha, con márgenes razonablemente regulares y ausencia de puntuación visible.


> **¿Por qué el nombre \'Voynich\'?**
>
> El manuscrito toma su nombre de Wilfrid Voynich, un librero polaco-estadounidense que lo adquirió en 1912 en la Villa Mondragone de Frascati, Italia, de la Compañía de Jesús. Voynich lo promocionó activamente en círculos académicos y científicos, aunque su procedencia exacta antes de 1912 es parcialmente incierta. En 1969, su viuda lo donó al librero Hans Kraus, quien a su vez lo cedió a la Biblioteca Beinecke en 1969.


## 1.2 Historia de la transmisión del manuscrito

El rastro documental del Voynich empieza en serio con una carta de 1666, en la que el erudito bohemio Johannes Marcus Marci lo envía al jesuita Athanasius Kircher en Roma, pidiéndole ayuda para descifrarlo. En la carta, Marci menciona que el libro habría pertenecido anteriormente al Emperador Rodolfo II de Habsburgo, quien supuestamente habría pagado seiscientos ducados de oro por él, una suma enorme para la época que sugiere que ya entonces se le atribuía una importancia especial.

Antes de Rodolfo II, la historia del manuscrito es especulativa. La carta de Marci menciona también el nombre de Roger Bacon, el fraile franciscano inglés del siglo XIII conocido por sus intereses en la filosofía natural y la alquimia, como posible autor. Esta atribución ha sido muy debatida y la mayoría de los investigadores modernos la consideran improbable, entre otras razones porque la datación por radiocarbono es posterior a Bacon en más de un siglo.

Entre 1666 y 1912 el manuscrito permanece en los archivos de la Compañía de Jesús, probablemente en la Villa Mondragone. Cuando Voynich lo adquiere, incluido entre una colección de manuscritos que los jesuitas vendían discretamente, comienza la historia moderna del Voynich como objeto de fascinación pública y científica.


| **Fecha aprox.** | **Evento**                                                           |
|------------------|----------------------------------------------------------------------|
|                  |                                                                      |
| 1404--1438       | Creación del manuscrito (datación por radiocarbono de 2011)          |
|                  |                                                                      |
| \~1580--1612     | Posesión por Rodolfo II de Habsburgo (según carta de Marci)          |
|                  |                                                                      |
| 1666             | Johannes Marcus Marci lo envía a Athanasius Kircher en Roma          |
|                  |                                                                      |
| 1666--1912       | Archivos de la Compañía de Jesús, Villa Mondragone (Frascati)        |
|                  |                                                                      |
| 1912             | Wilfrid Voynich lo adquiere y lo da a conocer en círculos académicos |
|                  |                                                                      |
| 1969             | Donado a la Biblioteca Beinecke, Universidad de Yale (MS 408)        |
|                  |                                                                      |
| 1991             | Primera edición facsímil publicada (Interrorum Publishers)           |
|                  |                                                                      |
| 2004             | Digitalización completa y puesta en acceso abierto por Yale          |
|                  |                                                                      |
| 2011             | Datación por radiocarbono: pergamino creado entre 1404 y 1438        |


## 1.3 Las ilustraciones y sus secciones

Aunque el texto del Voynich no ha podido leerse, las ilustraciones han permitido a los investigadores dividir el manuscrito en secciones temáticas con cierta confianza. Esta división es importante para nuestro análisis porque uno de los tests que realizamos pregunta precisamente si el vocabulario de glifos varía entre secciones, algo que esperaríamos si el texto refleja contenidos distintos.

Las secciones principales reconocidas por la tradición investigadora son las siguientes:


| **Sección**      | **Folios aproximados** | **Descripción de las ilustraciones**                                                                                                                             |
|------------------|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                  |                        |                                                                                                                                                                  |
| **Herbal**       | f1--f66, f85--f98      | Plantas con raíces, hojas y flores elaboradas. La mayoría no coinciden con especies botánicas conocidas, aunque algunas han sido identificadas tentativamente.   |
|                  |                        |                                                                                                                                                                  |
| **Astronómica**  | f67--f69               | Diagramas circulares concéntricos con estrellas, símbolos y figuras femeninas. Posibles representaciones de constelaciones o calendarios.                        |
|                  |                        |                                                                                                                                                                  |
| **Zodíaco**      | f70--f73               | Círculos con los signos del zodíaco y figuras femeninas desnudas en el interior. Uno de los pocos elementos identificables con certeza.                          |
|                  |                        |                                                                                                                                                                  |
| **Biológica**    | f74--f84               | Figuras femeninas en bañeras o piscinas conectadas por tubos. Su interpretación es especialmente controvertida: se han propuesto balnearios, alquimia, anatomía. |
|                  |                        |                                                                                                                                                                  |
| **Farmacéutica** | f88--f102              | Recipientes, frascos y vasijas de formas variadas, junto a ilustraciones de plantas. Posibles recetas o inventarios de ingredientes.                             |
|                  |                        |                                                                                                                                                                  |
| **Recetas**      | f103--f116             | Texto denso con pocas ilustraciones. Se asemeja a listas o recetas. Es la sección textualmente más densa.                                                        |


> *Nota: la división de secciones utilizada en nuestro análisis sigue el mapeado estándar de la transcripción STA1 2.0, que asigna cada folio a una sección según su número. Los folios astronómicos y de zodíaco no se incluyen en los tests de diferenciación semántica por su pequeño tamaño (la sección astronómica tiene solo 1 342 palabras, insuficiente para los tests de clasificación).*

## 1.4 El sistema de escritura

El aspecto más desconcertante del Voynich no son sus ilustraciones sino su texto. En apariencia tiene todas las propiedades de una lengua escrita: hay símbolos que se combinan regularmente, forman unidades que se separan por espacios (que interpretamos como palabras), y esas unidades tienen longitudes variables pero distribuidas de forma similar a las palabras de lenguas naturales. Sin embargo, nadie ha podido leerlo.

Algunos rasgos del sistema de escritura son especialmente llamativos para un lingüista o un estadístico:

-   Las palabras son sorprendentemente cortas. La longitud media es de unas cuatro o cinco unidades (glifos), bastante por debajo de la media del latín medieval o el árabe.

-   Algunos glifos aparecen casi exclusivamente al principio de las palabras, otros casi exclusivamente al final. Este patrón, que veremos cuantificado en detalle más adelante, recuerda al comportamiento de prefijos y sufijos en lenguas con morfología rica.

-   El vocabulario de palabras distintas es relativamente pequeño en comparación con el tamaño del corpus. Muchas palabras se repiten frecuentemente, pero hay también un gran número de palabras que aparecen una sola vez.

-   Hay una curiosa uniformidad interna: el texto parece escrito por una sola mano, o como mucho dos, con un estilo muy consistente a lo largo de los 240 folios.


> **El problema de la hapaxlegomena**
>
> En lingüística, un \'hapax legomenon\' (plural: hapax legomena) es una palabra que aparece una sola vez en todo el corpus. Los idiomas naturales tienen una proporción característica de hapax: en textos largos, entre el 40% y el 60% de las palabras distintas suelen ser hapax. El Voynich tiene una proporción de hapax inusualmente alta, lo que algunos investigadores han interpretado como evidencia de un vocabulario fabricado y otros como evidencia de un texto más denso informativamente de lo normal.


# Capítulo 2. Estado del arte: cien años de intentos

## 2.1 Las grandes hipótesis

En más de un siglo de investigación, las hipótesis sobre el Voynich se han organizado en cuatro grandes categorías. Ninguna ha logrado convencer de forma definitiva a la comunidad académica, pero cada una ha aportado evidencia parcial que cualquier análisis serio debe tener en cuenta.

### 2.1.1 Hipótesis del cifrado

La hipótesis más persistente, especialmente entre criptógrafos, es que el Voynich es un texto en una lengua conocida, protegido por algún tipo de cifrado. Los tipos de cifrado propuestos van desde sustituciones simples (cada glifo representa una letra latina o árabe) hasta sistemas más elaborados como cifrados de sustitución polialfabética, códigos de nomenclátor, o sistemas de acortamiento y sustitución combinados.

Durante la Segunda Guerra Mundial, el Voynich fue estudiado por criptógrafos profesionales de la Armada y la Marina de los Estados Unidos, entre ellos William F. Friedman, que es considerado el padre de la criptología moderna estadounidense. Friedman y su equipo, que tenían acceso a herramientas y métodos que habían descifrado sistemas de cifrado militar muy sofisticados, no pudieron con el Voynich. Friedman llegó a la conclusión privada, documentada en notas personales, de que era posible que el manuscrito no fuera descifrable con las técnicas clásicas porque podría no estar basado en ninguna lengua natural.

Un problema fundamental de la hipótesis del cifrado simple es que las herramientas estadísticas modernas, incluyendo las que utilizamos en este trabajo, deberían detectar los patrones residuales de la lengua subyacente incluso después de aplicar una sustitución. Si el Voynich fuera un cifrado César o un cifrado Vigenère sobre latín, sus curvas de entropía deberían parecerse a las del latín. Como veremos, no es así. Recientemente, Greshko [2025] ha propuesto el cifrado Naibbe, un cifrado homofónico verboso que puede ejecutarse a mano con materiales del siglo XV y que, aplicado sobre latín e italiano, reproduce varias propiedades estadísticas del Voynich. Nuestra implementación cuantitativa (Capítulo 14) confirma que Naibbe es el modelo de la literatura más cercano al Voynich (d=1.028), con un rebote significativo (0.554) y buena MI de bigrama (1.725), pero con MI posicional nula (0.001), lo que sugiere que un cifrado históricamente plausible no puede descartarse por completo pero tampoco reproduce el fingerprint completo.

### 2.1.2 Hipótesis de la lengua construida

John Dee, el matemático y astrólogo de la corte de Isabel I de Inglaterra, y su asociado Edward Kelley realizaron en la década de 1580 sesiones de espiritismo en las que afirmaban recibir dictados en una lengua angélica que llamaban enoquiano. Algunos investigadores han sugerido que el Voynich podría ser un ejemplo temprano de lengua construida, es decir, un sistema lingüístico inventado deliberadamente con propósitos filosóficos, religiosos o crípticos.

Esta hipótesis ha ganado cierto apoyo moderno. El lingüista Stephen Bax publicó en 2014 un análisis en el que propuso lecturas tentativas para algunos glifos y palabras, sugiriendo una posible lengua semítica subyacente. Sin embargo, sus resultados no han sido replicados de forma independiente. Más recientemente, el investigador Gerard Cheshire propuso en 2019 que el Voynich está escrito en proto-romance, un dialecto mediterráneo medieval. Esta hipótesis fue ampliamente criticada por medievalistas y lingüistas.

### 2.1.3 Hipótesis del sinsentido

La hipótesis más radical, propuesta entre otros por Gordon Rugg [2004], es que el Voynich simplemente no significa nada. Rugg demostró que es posible generar texto con las propiedades estadísticas superficiales del Voynich usando una tabla de Cardan, un dispositivo de cifrado del siglo XVI que combina prefijos, raíces y sufijos de forma mecánica. El texto resultante parece coherente a primera vista pero no codifica ningún mensaje. Rugg y Taylor [2017] extendieron este resultado demostrando que el método también replica propiedades cuantitativas como la distribución de Zipf y las distribuciones de longitud de palabra.

En apoyo parcial de esta línea, Gaskell y Bowern [2022] reclutaron 42 voluntarios para escribir textos sin sentido y encontraron que el Voynich se parece estadísticamente más al gibberish humano que a texto significativo en varias métricas (baja entropía, alta repetición, sesgo posicional de caracteres). Asimismo, Schinner [2007] concluyó que las propiedades del texto son más consistentes con gibberish producido por un método cuasi-estocástico que con lenguas naturales.

Esta hipótesis tiene la virtud de explicar por qué nadie ha podido descifrar el manuscrito, pero enfrenta un problema serio: un texto generado mecánicamente con combinaciones aleatorias debería tener un perfil estadístico diferente al del Voynich en ciertos tests de estructura profunda. Precisamente, el análisis de información mutua posicional que realizamos en este trabajo fue diseñado para distinguir entre texto con estructura morfológica real y texto generado por slots mecánicos. De hecho, nuestra implementación cuantitativa de la tabla de Cardan (Capítulo 14) muestra que este mecanismo produce el corpus más alejado del Voynich de todos los modelos probados (d=4.485), con un decay del 75.5% (vs. 8.9%), una MI de bigrama de 5.087 (vs. 1.681) y una MI posicional de 1.075 (vs. 0.658): la tabla genera un texto demasiado regular y predecible.

### 2.1.4 Hipótesis de la lengua natural cifrada parcialmente

Una cuarta hipótesis, que podríamos llamar intermedia, es que el Voynich combina una lengua natural con un sistema de codificación que no es un cifrado puro sino más bien una transliteración no estándar. Bajo esta hipótesis, los glifos no son letras de un alfabeto cifrado sino símbolos que representan sílabas, morfemas o palabras enteras de alguna lengua, posiblemente con un sistema idiosincrático desarrollado por el autor. Hermes [2022] ha documentado que el cifrado Polygraphia III de Johannes Trithemius, aplicado como procedimiento aleatorio, produce texto que imita las propiedades estadísticas del Voynich y que se presenta como un lenguaje artificial, proporcionando un precedente histórico concreto para este tipo de sistema. No obstante, nuestra implementación cuantitativa (Capítulo 14) muestra que la Polygraphia III destruye la estructura posicional dentro de la palabra (MI_pos≈0 vs. 0.658 del Voynich), lo que limita su plausibilidad como mecanismo generativo completo.

Esta hipótesis es compatible con los resultados que presentaremos: el Voynich tiene más estructura posicional que una lengua natural típica pero menos que un sistema de slot rígido. Sus dependencias entre glifos son muy fuertes a corto alcance (dentro de la palabra) pero se atenúan rápidamente. Esto puede interpretarse como un sistema donde las palabras tienen morfología interna predecible pero el vocabulario léxico es opaco.

## 2.2 Hallazgos estadísticos previos

Más allá de las hipótesis sobre el contenido, la comunidad investigadora ha acumulado un cuerpo de resultados estadísticos sobre las propiedades formales del texto que cualquier análisis debe tener en cuenta.

### 2.2.1 La ley de Zipf y la entropía

Jorge Stolfi [2000--2012], uno de los investigadores que más ha contribuido al estudio estadístico del Voynich, demostró que el texto sigue la ley de Zipf: si ordenamos las palabras por frecuencia, la frecuencia de la n-ésima palabra es aproximadamente proporcional a 1/n. Landini [2001] confirmó este resultado con análisis espectral y mostró además que la autocorrelación de caracteres es compatible con una lengua cifrada. Esta ley se cumple en prácticamente todas las lenguas naturales conocidas. Su cumplimiento en el Voynich es una evidencia moderada a favor de que no es texto completamente aleatorio, aunque también puede verificarse en ciertos textos generados artificialmente [Rugg y Taylor, 2017; Timm y Schinner, 2020].

El análisis de entropía de Shannon del Voynich, que mide cuánta incertidumbre hay en cada símbolo dado el contexto, produce valores que se sitúan entre los de las lenguas naturales y los de un texto aleatorio. Bennett [1976] fue el primero en aplicar análisis de entropía al manuscrito, encontrando que la entropía de segundo orden es considerablemente más baja que la de la mayoría de lenguas de comparación, con valores similares solo a algunas lenguas polinesias. Prescott Currier [1976] amplió estos hallazgos, y Lindemann y Bowern [2020] los extendieron a 316 textos de comparación, encontrando que la entropía condicional de caracteres del Voynich es *"distinctly lower than any of the 316 comparison texts"*. En nuestro análisis lo confirmamos con mayor precisión y lo extendemos a entropías condicionales de orden superior, donde identificamos la forma de U característica que no está documentada en la literatura previa.

### 2.2.2 Los grupos de Currier

Prescott Currier [1976], un criptoanalista de la marina estadounidense, observó que el texto del Voynich se puede dividir en dos grupos estadísticamente distinguibles, que llamó grupo A y grupo B. Los folios del grupo A tienden a tener palabras más largas y un vocabulario distinto al de los folios del grupo B. Esta diferencia es suficientemente marcada como para ser detectada automáticamente.

La interpretación más común de los grupos de Currier es que reflejan diferentes secciones del manuscrito (la división herbal/biológica/recetas que mencionamos antes), posiblemente escritas en momentos distintos o con propósitos diferentes. Algunos investigadores han propuesto que los dos grupos fueron escritos por manos diferentes. Nuestro análisis de diferenciación semántica entre secciones (Bloque E) es una versión moderna y más granular del análisis original de Currier.

### 2.2.3 Resultados del análisis computacional moderno

En la última década, varios grupos han aplicado técnicas cuantitativas avanzadas al Voynich. Montemurro y Zanette [2013] analizaron la estructura de largo alcance del manuscrito usando métodos de entropía de Shannon e identificaron redes de palabras clave semánticas distribuidas por secciones, proporcionando evidencia fuerte de un mensaje genuino. Amancio et al. [2013] compararon el Voynich con el Nuevo Testamento en 15 idiomas usando estadísticas de primer orden, topología de redes complejas y análisis de intermitencia, concluyendo que en el 90% de los casos las propiedades estadísticas del Voynich son compatibles con textos reales.

Stolfi [2000--2012] identificó los "paradigmas" posicionales del Voynich: ciertos glifos son exclusivos de posición inicial, otros de posición final, y otros de posición media, proponiendo un modelo de tres capas (corteza, manto, núcleo). Matlach, Janeckova y Dostal [2022] extendieron este análisis explorando la posibilidad de que algunos glifos sean compuestos o ligaduras, sugiriendo que el alfabeto efectivo podría ser mucho menor de lo que aparenta.

Sobre la identificación de la lengua subyacente, Hauer y Kondrak [2016] aplicaron métodos de descifrado automático a 380 lenguas y sugirieron el hebreo como lengua fuente, aunque el resultado fue criticado por la falta de adecuación de modelos entrenados en lenguas modernas para un manuscrito del siglo XV. Lindemann [2022] aplicó la MATTR (Moving Average Type-Token Ratio) y encontró que la complejidad morfológica del Voynich se sitúa entre las lenguas romances/germánicas y las semíticas/eslavas, con el centroide proximal más cercano en la familia iraní. Babaahmadi [2019] aplicó un modelo oculto de Markov con dos estados internos y encontró que las transiciones identifican regímenes equivalentes a vocales y consonantes, con frecuencias similares a las de lenguas naturales.

Sobre modelos generativos, Timm y Schinner [2020] propusieron un algoritmo de "auto-citación" donde el escriba copiaría y modificaría palabras anteriores del manuscrito, reproduciendo ambas leyes de Zipf. Nuestra implementación cuantitativa (Capítulo 14) muestra que la auto-citación produce buenas correlaciones de bigrama (MI_big=1.836) pero un rebote bajo (0.120) y una distancia de d=1.356 al Voynich. Timm y Schinner [2024] revisaron el debate en la Conferencia Internacional sobre el Manuscrito Voynich (Malta, 2022). Reddy y Knight [2011] proporcionaron una síntesis de lingüística computacional que documentó tanto propiedades lingüísticamente aberrantes (falta de bigramas repetidos, distribuciones anómalas al borde de línea) como propiedades conformes al lenguaje natural (distribuciones de longitud, frecuencia, morfología aparente).

La revisión más completa hasta la fecha es la de Bowern y Lindemann [2021], que evalúa sistemáticamente los argumentos lingüísticos a favor y en contra de que el Voynich codifique un lenguaje natural, concluyendo que la evidencia estadística favorece un sustrato lingüístico genuino.

Ninguno de estos estudios, sin embargo, ha combinado sistemáticamente múltiples tests estadísticos independientes con controles formales (tests de permutación, holdout por folio, comparación con cifrados conocidos y lenguas de cuatro familias lingüísticas distintas) para producir un scorecard completo de evidencia, ni ha aplicado forward modeling con múltiples modelos generativos ---incluyendo implementaciones cuantitativas de las hipótesis de Rugg [2004], Timm y Schinner [2020], Hermes [2022] y Greshko [2025]--- para identificar qué mecanismo reproduce la huella estadística del Voynich. Este es precisamente el objetivo de nuestro trabajo.

## 2.3 Limitaciones del estado del arte

El campo de los estudios sobre el Voynich sufre de varios problemas metodológicos recurrentes que este trabajo intenta evitar. Vale la pena nombrarlos explícitamente porque ayudan a entender por qué tantos análisis anteriores no han convencido a la comunidad científica.

-   Circularidad analítica: descubrir un patrón en los datos y luego validarlo en los mismos datos. Por eso nosotros utilizamos holdout por folio (Bloque B): las reglas se descubren en la mitad del corpus y se validan en la otra mitad.

-   Ausencia de controles: comparar el Voynich solo consigo mismo, sin compararlo con lenguas naturales y cifrados conocidos bajo los mismos tests. En nuestro análisis, cada resultado del Voynich se pone en contexto con ocho corpus de control: latín medieval, cifrado César, cifrado Vigenère, hebreo bíblico, árabe coránico, turco y finés.

-   Confirmación de hipótesis: seleccionar los tests que apoyan la hipótesis preferida e ignorar los que la contradicen. Nosotros reportamos todos los resultados, incluidos los que son ambiguos o que inicialmente apuntaban en la dirección incorrecta.

-   Sobreinterpretación de evidencia parcial: afirmar que se ha descifrado el manuscrito basándose en unas pocas coincidencias léxicas tentativas. Nosotros distinguimos cuidadosamente entre lo que los datos pueden y no pueden demostrar.

# Capítulo 3. El corpus: STA1 2.0 y su preprocesamiento

## 3.1 El problema de la transcripción

Para aplicar cualquier análisis estadístico o computacional al Voynich, primero hay que convertir los glifos manuscritos en símbolos que un ordenador pueda procesar. Este paso, aparentemente trivial, introduce decisiones que afectan profundamente a los resultados.

El problema central es que no hay consenso sobre cuántos glifos distintos existen en el Voynich. Dependiendo de cómo se traten las variantes alográficas (símbolos que parecen variaciones de un mismo glifo básico), el inventario puede variar entre 20 y más de 50 unidades. Una transcripción que agrupe muchas variantes producirá un vocabulario más pequeño y palabras más cortas. Una transcripción que distinga más variantes producirá el efecto opuesto. Esta decisión no es neutral: puede hacer que el texto parezca más o menos similar a una lengua natural.

A lo largo del siglo XX se desarrollaron varios sistemas de transcripción. Los más usados son el alfabeto EVA (European Voynich Alphabet), propuesto en 1998 por René Zandbergen y Gabriel Landini, y el sistema STA (Stolfi-Takahashi Alphabet), propuesto por Jorge Stolfi. Este trabajo usa la versión STA1 2.0 de Stolfi, que es la disponible en acceso abierto y que produce un vocabulario de glifos bien documentado.

## 3.2 La transcripción STA1 2.0

El sistema STA1 2.0 codifica cada glifo como un token de dos caracteres: una letra mayúscula que identifica la familia del glifo, seguida de un dígito o letra minúscula que indica la variante. Por ejemplo, A1, A2, A3 son variantes de la misma familia de glifos \'A\'; Q1 y Q2 son variantes de la familia \'Q\'.

Esta codificación tiene una consecuencia importante para el análisis computacional: el tamaño del vocabulario resultante es de 166 glifos distintos (más el separador de palabra \'.\'), que es un número suficientemente grande para capturar la variedad del sistema de escritura pero suficientemente pequeño para que los tests estadísticos sean estadísticamente potentes.


> **Un error crítico que encontramos durante el análisis**
>
> En la primera versión de nuestro código de preprocesamiento (notebook 01_statistical_fingerprint.ipynb), un error en el parser producía 9.762 tokens únicos en lugar de 166, porque el código concatenaba los glifos en lugar de separarlos. Este error contaminó todos los tests de entropía y los análisis de cadenas de Markov, produciendo resultados absurdos (entropías que aumentaban con el contexto, lo cual viola una ley matemática fundamental). Detectar y corregir este error fue una lección importante sobre la importancia de validar los datos antes de interpretar los resultados. El parser correcto y validado está en el notebook 02_permutation_bootstrap.ipynb, celda 1.


## 3.3 El parser validado

El parser correcto extrae glifos usando la siguiente expresión regular:

> glifos = re.findall(r\'\[A-Z\]\[0-9a-z\]\', palabra_raw)

Esta expresión busca exactamente la combinación de una letra mayúscula seguida de un dígito o letra minúscula, que es la forma de todos los tokens STA1. El proceso completo por cada línea del archivo de transcripción es:

1.  Ignorar líneas vacías, comentarios (que empiezan por #) y metadatos de folio.

2.  Extraer el contenido de texto que sigue a la etiqueta de posición con re.match(r\'\^\<\[\^\>\]+\>\\s+(.\*)\', linea).

3.  Limpiar etiquetas internas y convertir los guiones a puntos (los guiones en STA indican separación de palabra).

4.  Dividir el texto resultante por \'.\' para obtener palabras individuales.

5.  Para cada palabra, aplicar findall para extraer los glifos y añadir \'.\' como marcador de fin de palabra.

## 3.4 Estadísticas del corpus

El corpus procesado con el parser validado tiene las siguientes propiedades:


| **Propiedad**                                    | **Valor**                                   |
|--------------------------------------------------|---------------------------------------------|
|                                                  |                                             |
| Tokens totales (glifos + separadores)            | **194 341**                                 |
|                                                  |                                             |
| Total de glifos (sin separadores)                | **157 254**                                 |
|                                                  |                                             |
| Total de palabras (unidades separadas por \'.\') | **37 087**                                  |
|                                                  |                                             |
| Vocabulario único (glifos distintos)             | **166**                                     |
|                                                  |                                             |
| Separador de palabra \'.\'                       | **Incluido como token 0 en el vocabulario** |
|                                                  |                                             |
| Glifos con frecuencia ≥ 5                        | **76 (el 46% del vocabulario)**             |
|                                                  |                                             |
| Glifos con frecuencia \< 5 (hapax y raros)       | **91 (el 54% del vocabulario)**             |
|                                                  |                                             |
| Longitud media de palabra                        | **\~4.2 glifos**                            |
|                                                  |                                             |
| Longitud mínima de palabra                       | **1 glifo**                                 |
|                                                  |                                             |
| Longitud máxima de palabra observada             | **\~12 glifos**                             |


## 3.5 El mapeado de secciones

Además del corpus plano, para el análisis de diferenciación semántica necesitamos saber a qué sección pertenece cada palabra. El notebook 02_permutation_bootstrap.ipynb (celda 14) implementa una función que lee el número de cada folio directamente de los metadatos de la transcripción y lo asigna a una sección usando los rangos estándar:


| **Sección**  | **Folios**          | **Palabras** | **Glifos**  |
|--------------|---------------------|--------------|-------------|
|              |                     |              |             |
| herbal       | f1--f66, f85--f98   | **14 278**   | **58 832**  |
|              |                     |              |             |
| recetas      | f103--f116          | **10 606**   | **45 661**  |
|              |                     |              |             |
| biologica    | f74--f84            | **6 768**    | **28 911**  |
|              |                     |              |             |
| farmaceutica | f88--f89, f99--f102 | **2 505**    | **10 652**  |
|              |                     |              |             |
| zodiaco      | f70--f73            | **1 588**    | **7 327**   |
|              |                     |              |             |
| astronomica  | f67--f69            | **1 342**    | **5 871**   |
|              |                     |              |             |
| **TOTAL**    | **226 folios**      | **37 087**   | **157 254** |


> *Nota metodológica: en los tests de clasificación por sección (Bloque E), se excluyen las secciones astronómica y zodíaco porque su tamaño reducido (menos de 2 000 palabras) hace que los tests de clasificación sean estadísticamente poco potentes. El análisis trabaja con las cuatro secciones mayores: herbal, recetas, biológica y farmacéutica.*

## 3.6 El corpus de control: latín medieval y cifrados

Un principio básico del análisis estadístico es que un resultado solo tiene significado en relación a un punto de referencia. Que el Voynich tenga una entropía de 4.14 bits no dice nada por sí solo; dice mucho cuando sabemos que el latín medieval tiene 4.12 bits y que un cifrado Vigenère tiene 4.62 bits.

Para todos los tests que realizamos, comparamos el Voynich con tres corpus de control:

-   Latín medieval (Vulgata): descargado del Proyecto Gutenberg (texto #8300). La Vulgata es la traducción latina de la Biblia realizada principalmente por San Jerónimo en el siglo IV, que fue el texto latino de referencia durante toda la Edad Media. Es el mejor proxy disponible para el latín que se usaba en el contexto temporal y geográfico del Voynich.

-   Cifrado César (ROT-13 sobre latín): una sustitución monoalfabética simple donde cada letra se reemplaza por la que está 13 posiciones después en el alfabeto. Es el cifrado más simple posible y representa el límite inferior de sofisticación criptográfica.

-   Cifrado Vigenère (sobre latín, clave \'voynich\'): un cifrado polialfabético donde la clave define qué sustitución aplica en cada posición. Es significativamente más difícil de descifrar que el César y fue considerado irrompible durante siglos. Representa un nivel de sofisticación criptográfica más realista para el siglo XV.


> **¿Por qué cifrar el latín y no el español?**
>
> Utilizamos el latín como texto fuente para los cifrados porque si el Voynich fuera un cifrado de un texto medieval, lo más probable es que ese texto estuviera en latín. Cifrar español moderno y compararlo con el Voynich introduciría una asimetría histórica injustificada. Además, el latín y el Voynich comparten el mismo período histórico y el mismo ámbito cultural aproximado.


## 3.7 Limitaciones del corpus

Antes de entrar en el análisis, es importante ser explícito sobre las limitaciones del corpus que usamos. La honestidad sobre estas limitaciones no debilita las conclusiones: al contrario, las hace más robustas porque delimita claramente qué puede y qué no puede afirmarse.

-   La transcripción STA1 2.0 no es perfecta: hay partes del manuscrito difíciles de leer donde el transcriptor ha tenido que hacer juicios interpretativos. Los resultados podrían variar ligeramente con otras transcripciones.

-   No sabemos si la transcripción captura todas las distinciones relevantes del sistema de escritura original. Si dos glifos que la transcripción trata como iguales son en realidad distintos para el autor del manuscrito, nuestro análisis lo ignorará.

-   El corpus tiene solo \~37 000 palabras. Es suficiente para los tests que realizamos, pero significativamente menor que los corpus usados en estudios lingüísticos serios (que típicamente tienen millones de palabras). Esto aumenta la varianza estadística de algunas estimaciones.

-   La asignación de folios a secciones temáticas es convencional, no universal. Algunos investigadores usan divisiones distintas. Nuestros resultados de diferenciación semántica dependen parcialmente de esta división.

# Capítulo 4. La pregunta de investigación

## 4.1 Formulación precisa del problema

Antes de aplicar cualquier herramienta estadística, hay que formular con precisión qué pregunta se está respondiendo. Las preguntas vagas producen respuestas vagas. \'El Voynich tiene propiedades similares a una lengua\' no es una afirmación científica porque no especifica qué propiedades, similares en qué sentido, y en comparación con qué.

La investigación se articula en torno a una pregunta principal y tres subpreguntas derivadas:


> **Pregunta de investigación principal**
>
> ¿Qué tipo de sistema generativo es compatible con la huella estadística del Manuscrito Voynich?
>
> Concretamente: ¿las propiedades estadísticas del texto ---estructura posicional de glifos, dependencias contextuales, velocidad de mezcla de Markov y vocabulario semánticamente diferenciado por sección--- son más consistentes con las de una lengua natural con morfología, con las de un cifrado de sustitución aplicado sobre una lengua natural, o con las de algún otro mecanismo generativo?

> **Subpregunta 1 — Diagnóstico tipológico**
>
> ¿El perfil estadístico del Voynich se agrupa con alguna familia lingüística conocida (indoeuropea, semítica, aglutinante) o se sitúa fuera del espacio de variación de las lenguas naturales? Para responderla, comparamos el Voynich con seis lenguas de cuatro familias lingüísticas y dos cifrados clásicos bajo los mismos seis tests (Bloques A–F).

> **Subpregunta 2 — Forward modeling**
>
> ¿Qué mecanismo generativo concreto ---entre once candidatos, incluyendo las hipótesis de Rugg [2004], Timm y Schinner [2020], Hermes [2022] y Greshko [2025]--- reproduce mejor la huella estadística completa del Voynich? Para responderla, generamos once corpus sintéticos calibrados y medimos su distancia euclídea ponderada al Voynich en un espacio de cinco métricas (Bloque G).

> **Subpregunta 3 — Filtro cuantitativo**
>
> ¿Es posible definir un conjunto de restricciones numéricas (rebote, MI posicional, MI de bigrama, spectral gap) que cualquier futura propuesta de descifrado deba satisfacer para ser estadísticamente plausible?


Nótese lo que estas preguntas no preguntan: no preguntan si el Voynich es descifrable, no preguntan qué lengua subyace (si hay alguna), y no preguntan si tiene significado. Son preguntas legítimas pero no respondibles con las herramientas que usamos aquí. Nuestras preguntas son específicamente sobre el tipo de sistema que produce el texto observable, sobre su posición en el espacio de variación de las lenguas naturales, y sobre qué mecanismos quedan descartados cuantitativamente.

## 4.2 Por qué esta pregunta es tratable

Una característica importante de nuestra pregunta es que es operacionalizable: podemos convertirla en tests estadísticos concretos con resultados numéricos y p-valores. Esto no ocurre con todas las preguntas sobre el Voynich. "Está escrito en hebreo medieval" o "es un fraude completo" son hipótesis mucho más difíciles de falsificar.

La razón por la que nuestra pregunta es tratable es que las lenguas naturales, los cifrados y los sistemas artificiales tienen firmas estadísticas distintas que podemos medir. La tabla siguiente resume las predicciones de cada tipo de sistema para las cinco propiedades que medimos:


| **Propiedad**                         | **Lengua natural**                             | **Cifrado de sustitución**                  | **Sistema silábico artificial**               |
|---------------------------------------|------------------------------------------------|---------------------------------------------|-----------------------------------------------|
|                                       |                                                |                                             |                                               |
| **Estructura posicional de morfemas** | Fuerte: prefijos y sufijos en posiciones fijas | Heredada de la lengua original              | Muy fuerte: glifos particionados por posición |
|                                       |                                                |                                             |                                               |
| **Entropía condicional (N=1→4)**      | Decrece monótonamente                          | Decrece como la lengua cifrada              | Forma de U: cae en N=1, sube en N≥2          |
|                                       |                                                |                                             |                                               |
| **Velocidad de mezcla de Markov**     | Moderada (spectral gap \~0.5--0.8)             | Misma que la lengua cifrada                 | Baja (gap \~0.5, similar a aglutinantes)      |
|                                       |                                                |                                             |                                               |
| **Vocabulario por sección**           | Diferenciado (temas distintos)                 | Uniforme (el cifrado no distingue temas)    | Diferenciado si codifica contenido real       |
|                                       |                                                |                                             |                                               |
| **Información mutua posicional**      | Moderada (\~0.15--0.31 bits)                   | Igual a la lengua original                  | Alta (\~0.5--0.7 bits)                        |

La columna "sistema silábico artificial" refleja las predicciones del modelo SilPart (Capítulo 14), que resultó ser el más cercano al Voynich. La pregunta de investigación es, en esencia, determinar en cuál de estas tres columnas cae el Voynich ---y si cae en una posición intermedia o fuera de las tres, qué implica eso.


## 4.3 Estructura del análisis

Para responder a la pregunta, organizamos el análisis en seis bloques diagnósticos independientes, más un bloque de forward modeling que evalúa once hipótesis generativas. La independencia entre bloques diagnósticos es clave: si todos los tests usaran la misma propiedad estadística, un resultado favorable sería una sola observación repetida. Con seis herramientas distintas, la convergencia de resultados es evidencia acumulativa genuina.


| **Bloque** | **Herramienta**                     | **Qué mide**                                             | **Parte del estudio**  |
|------------|-------------------------------------|----------------------------------------------------------|--------------------|
|            |                                     |                                                          |                    |
| **A**      | **Información mutua posicional**    | ¿Los glifos tienen posiciones preferidas en la palabra?  | Parte III, cap. 9  |
|            |                                     |                                                          |                    |
| **B**      | **Holdout por folio**               | ¿Los patrones se replican en datos no vistos?            | Parte III, cap. 10 |
|            |                                     |                                                          |                    |
| **C**      | **Entropía condicional de orden N** | ¿Cómo predice el contexto el siguiente glifo?            | Parte III, cap. 11 |
|            |                                     |                                                          |                    |
| **D**      | **Spectral gap de Markov**          | ¿Cómo de persistentes son las dependencias entre glifos? | Parte III, cap. 12 |
|            |                                     |                                                          |                    |
| **E**      | **Diferenciación semántica**        | ¿Varía el vocabulario entre secciones temáticas?         | Parte III, cap. 13 |
|            |                                     |                                                          |                    |
| **F**      | **Métricas de forma de curva**      | ¿La forma de la curva entrópica distingue el Voynich?    | Parte III, cap. 11 |
|            |                                     |                                                          |                    |
| **G**      | **Forward modeling (11 modelos)**   | ¿Qué mecanismo generativo reproduce la huella del Voynich? | Parte III, cap. 14 |


## 4.4 Lo que este análisis puede y no puede demostrar

Es importante ser explícito sobre los límites interpretativos de nuestro análisis antes de que el lector llegue a los resultados. Esto no es modestia retórica: es la única forma de que las conclusiones sean honestas.

**Lo que sí podemos demostrar**

-   Si el Voynich es estadísticamente distinto de un cifrado César o Vigenère aplicado sobre latín, bajo múltiples tests independientes.

-   Si los glifos tienen preferencias posicionales dentro de la palabra que son estadísticamente incompatibles con texto aleatorio.

-   Si el vocabulario de glifos varía entre secciones del manuscrito de forma consistente con contenido semánticamente diferenciado.

-   Si las propiedades de la cadena de transiciones entre glifos se parecen más a las de una lengua natural que a las de un cifrado.

-   Si el perfil estadístico del Voynich se agrupa con alguna familia lingüística específica o se sitúa fuera del espacio de variación de las seis lenguas naturales testadas (Subpregunta 1).

-   Qué mecanismos generativos concretos son capaces de reproducir la huella estadística completa del Voynich y cuáles quedan cuantitativamente descartados (Subpregunta 2).

-   Qué restricciones numéricas mínimas debe satisfacer cualquier propuesta futura de descifrado para ser estadísticamente plausible (Subpregunta 3).

**Lo que no podemos demostrar**

-   Que el Voynich es una lengua natural conocida o desconocida: nuestros tests distinguen "estructura similar a lengua" de "estructura de cifrado", pero no pueden identificar qué lengua.

-   Que el manuscrito tiene significado: un sistema artificial con morfología diseñada puede pasar todos nuestros tests sin codificar ningún mensaje.

-   Que nuestra interpretación de las secciones temáticas es correcta: si la división herbal/biológica/recetas es errónea, el Bloque E no tiene interpretación válida.

-   Que los resultados se mantendrían con otras transcripciones: hemos probado solo con STA1 2.0.

*Con el contexto establecido, el corpus descrito y la pregunta formulada con precisión, estamos listos para desarrollar las herramientas matemáticas que usaremos en el análisis. Eso es el objeto de la Parte II.*


# Referencias de la Parte I

- Amancio, D. R., Altmann, E. G., Rybski, D., Oliveira Jr., O. N., y Costa, L. da F. (2013). "Probing the Statistical Properties of Unknown Texts: Application to the Voynich Manuscript." *PLoS ONE* 8(7): e67310. DOI: [10.1371/journal.pone.0067310](https://doi.org/10.1371/journal.pone.0067310)

- Babaahmadi, K. (2019). "A Hidden Markov Model for the Linguistic Analysis of the Voynich Manuscript." *Mathematical and Computational Applications (MDPI)* 24(1): 14. [https://www.mdpi.com/2297-8747/24/1/14](https://www.mdpi.com/2297-8747/24/1/14)

- Bennett, W. R. (1976). *Scientific and Engineering Problem Solving with the Computer.* Englewood Cliffs: Prentice-Hall.

- Bowern, C. y Lindemann, L. (2021). "The Linguistics of the Voynich Manuscript." *Annual Review of Linguistics* 7: 285--308. DOI: [10.1146/annurev-linguistics-011619-030613](https://doi.org/10.1146/annurev-linguistics-011619-030613)

- Currier, P. (1976). "Papers on the Voynich Manuscript." Presentado en seminario sobre el Manuscrito Voynich. [https://www.voynich.nu/extra/curr_main.html](https://www.voynich.nu/extra/curr_main.html)

- Gaskell, D. E. y Bowern, C. L. (2022). "Gibberish After All? Voynichese Is Statistically Similar to Human-Produced Samples of Meaningless Text." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313. [https://ceur-ws.org/Vol-3313/paper4.pdf](https://ceur-ws.org/Vol-3313/paper4.pdf)

- Greshko, M. A. (2025). "The Naibbe Cipher: A Substitution Cipher that Encrypts Latin and Italian as Voynich Manuscript-Like Ciphertext." *Cryptologia*. DOI: [10.1080/01611194.2025.2566408](https://doi.org/10.1080/01611194.2025.2566408)

- Hauer, B. y Kondrak, G. (2016). "Decoding Anagrammed Texts Written in an Unknown Language and Script." *Transactions of the Association for Computational Linguistics* 4: 75--86. DOI: [10.1162/tacl_a_00084](https://doi.org/10.1162/tacl_a_00084)

- Hermes, J. (2022). "Polygraphia III: The Cipher that Pretends to be an Artificial Language." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313. [https://ceur-ws.org/Vol-3313/paper7.pdf](https://ceur-ws.org/Vol-3313/paper7.pdf)

- Landini, G. (2001). "Evidence of Linguistic Structure in the Voynich Manuscript Using Spectral Analysis." *Cryptologia* 25(4): 275--295. DOI: [10.1080/0161-110191889932](https://doi.org/10.1080/0161-110191889932)

- Lindemann, L. (2022). "Crux of the MATTR: Voynichese Morphological Complexity." *Proceedings of the International Conference on the Voynich Manuscript 2022*, CEUR Workshop Proceedings, Vol. 3313. [https://ceur-ws.org/Vol-3313/paper9.pdf](https://ceur-ws.org/Vol-3313/paper9.pdf)

- Lindemann, L. y Bowern, C. (2020). "Character Entropy in Modern and Historical Texts: Comparison Metrics for an Undeciphered Manuscript." arXiv preprint arXiv:2010.14697. [https://arxiv.org/abs/2010.14697](https://arxiv.org/abs/2010.14697)

- Matlach, V., Janeckova, B., y Dostal, D. (2022). "The Voynich Manuscript: Symbol Roles Revisited." *PLoS ONE* 17(1): e0260948. DOI: [10.1371/journal.pone.0260948](https://doi.org/10.1371/journal.pone.0260948)

- Montemurro, M. A. y Zanette, D. H. (2013). "Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis." *PLoS ONE* 8(6): e66344. DOI: [10.1371/journal.pone.0066344](https://doi.org/10.1371/journal.pone.0066344)

- Reddy, S. y Knight, K. (2011). "What We Know About The Voynich Manuscript." *Proceedings of the 5th ACL-HLT Workshop on Language Technology for Cultural Heritage, Social Sciences, and Humanities*, pp. 78--86. [https://aclanthology.org/W11-1511/](https://aclanthology.org/W11-1511/)

- Rugg, G. (2004). "An Elegant Hoax? A Possible Solution to the Voynich Manuscript." *Cryptologia* 28(1): 31--46. DOI: [10.1080/0161-110491892755](https://doi.org/10.1080/0161-110491892755)

- Rugg, G. y Taylor, G. (2017). "Hoaxing Statistical Features of the Voynich Manuscript." *Cryptologia* 41(3): 247--268. DOI: [10.1080/01611194.2016.1206753](https://doi.org/10.1080/01611194.2016.1206753)

- Schinner, A. (2007). "The Voynich Manuscript: Evidence of the Hoax Hypothesis." *Cryptologia* 31(2): 95--107. DOI: [10.1080/01611190601133539](https://doi.org/10.1080/01611190601133539)

- Stolfi, J. (2000--2012). "Statistical Properties of the Voynich Manuscript." Technical Reports, Institute of Computing, UNICAMP. [https://www.ic.unicamp.br/~stolfi/EXPORT/projects/voynich/](https://www.ic.unicamp.br/~stolfi/EXPORT/projects/voynich/)

- Timm, T. y Schinner, A. (2020). "A Possible Generating Algorithm of the Voynich Manuscript." *Cryptologia* 44(1): 1--20. DOI: [10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999)

- Timm, T. y Schinner, A. (2024). "The Voynich Manuscript: Discussion of Text Creation Hypotheses." *Cryptologia* 48(4): 305--322. DOI: [10.1080/01611194.2023.2225716](https://doi.org/10.1080/01611194.2023.2225716)
