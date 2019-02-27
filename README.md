# Codingame Contests

Mis bots para los concursos de [codingame](https://www.codingame.com/).

## CodeRoyale

Máxima liga: Gold | Lenguaje: Python

Durante los primeros días usé una máquina de estados que cada vez fue ganando complejidad hasta llegar a un punto inmantenible.

Todo el movimiento pasa por una función "smoother" que evita que mi reina se encuentre en una posición peligrosa.

Durante los últimos días programé una copia del engine del juego para poder ser capaz de simular los turnos. Después planeé en usar un algoritmo
genético para encontrar una posible lista de órdenes que minimizaran la vida perdida de la reina, con el plan de ir añadiendo más parámetros.

Esto resultó imposible porque, aunque las simulaciones funcionaban correctamente, solo era capaz de hacer unas 200 antes de obtener un timeout y
ya era demasiado tarde para reescribir el código.

Aunque en el archivo están implementadas las simulaciones y el AG, no se usa para nada ya que es ineficiente.

## CodeOfKutulu

Máxima liga: Wood1 | Lenguaje: Python

En este caso empecé el concurso pensando en hacer simulaciones, por lo que intenté optimizar lo máximo posible el rendimiento.

Hice uso del primer turno (en el que tienes 1000ms en vez de 50ms) para precalulcar todas las distancias posibles usando dijkstra.

En CodeRoyale, para pasar de una simulación a otra, tenía que hacer varias copias de listas de objetos. Esto era muy costoso, ya que tenía que
hacer una copia profunda de cada objeto de forma recursiva, teniendo incluso estos objetos algunos atributos con más listas.

A raíz de eso pensé en usar estructuras más simples y pasar sólo listas de enteros o strings, con el índice indicando la entidad que corresponde.
También usé diccionarios siendo la clave y el valor una tupla de enteros.

Al final acabé con una gran cantidad de listas y diccionarios que tenía que copiar igualmente. Aunque era más rápido, probablemente haya otra
forma más eficiente de hacerlo en python.

Para seleccionar la mejor lista de órdenes, he usado un BFS limitando el ancho de cada nivel a 40, seleccionando las 40 simulaciones que
mejor puntuación tienen. La forma de conseguir las mejores puntuaciones es muy aproximada, ya que se hace con una heap queue
La profundidad del árbol es de 4, significando esto que se van a simular 4 turnos en el futuro.

Esta vez conseguí hacer alrededor de 1000 simulaciones, pero seguían siendo muy pocas y no encontraba ninguna forma de aumentarlas más.

Al final acabé dejando el concurso a la mitad, ya que no veia forma de aumentar el nº de simulaciones.

Si quiero hacer simulaciones, lo más probablem es que necesite un lenguaje como c++.


## LegendsOfCodeAndMagic

Máxima liga: Gold | Posición general: 140/2174 | Lenguaje: C++

Diario: https://github.com/Orzzet/100-days-of-code/blob/master/diario.md

Este concurso trataba sobre un juego de cartas similar a Hearthstone, aunque simplificado. Dos jugadores se enfrentan entre sí con un mazo de 30 cartas. Se pueden jugar criaturas y tres tipos de objetos distintos para afectar el campo de batalla. Las criaturas tienen habilidades que modifican su comportamiento con otras criaturas (o jugadores) y estas habildiades se pueden añadir o eliminar de criaturas en juego usando objetos (que además provocan otros efectos distintos, como hacer daño o ganar vida).

Si esto fuera poco, también tienes que construir el mazo con el que vas a jugar la partida con un método parecido a los drafts de Hearthstone, en el que vas elegiendo las cartas una a una de un pool de 3 cartas cada vez, hasta que has elegido 30. A los dos jugadores se les presentan exactamente las mismas cartas para elegir, pero cada jugador (cada bot) puede elegir cartas distintas.

El bot en realidad tenía dos partes, la del draft y la de la partida.

<b>Para el draft</b> puntué cada carta de forma individual y usé este valor como base, modificandolo a lo largo del draft en función del nº de cartas de cada coste. El nº de cartas de cada coste se conoce como curva de maná y mi intención era tener una buena curva de maná para poder sacar el máximo provecho de cada turno. También realizaba otras modificaciones teniendo en cuenta el nº de cartas que quedaban o dando prioridad a tener criaturas de coste bajo si no tenía ninguna.

Sinceramente, el draft fue mucho más importante de lo que parecía en un principio. Usando esta técnica, cada pequeña modificación podía tener un gran impacto. Otra técnica más analítica basándose en un entrenamiento previo para obtener estos valores numéricos (en vez de ponerlos a mano), probablemente habría dado mejor resultado.

<b>Para la partida</b> hice lo que ya tenía pensado de concursos anteriores: un árbol de búsqueda con una anchura fija, en el que los nodos son los estados del juego, siendo cada nodo hijo el resultante de efectuar una acción posible.

Aquí es donde estaba lo que más me interesaba, el motivo de por qué usé c++ en este concurso. Si en el concurso anterior llegué a realizar 1000 simulaciones en 50ms, en este llegué a realizar 1000 sims/ms. Hay que tener en cuenta que en este juego no había que tener en cuenta colisiones ni pathfinding. Aún así, el cambio de un lenguaje interpretado como python a un lenguaje compilado como c++ habiéndole añadido parámetros de optimización (`#pragma GCC optimize("-O3", "inline", "omit-frame-pointer", "unroll-loops")`), es abismal para este tipo de tareas. 

Así que el "experimento" fue un éxito, una vez teniendo la potencia de cálculo necesaria, he podido ir implementando varias estrategias. 

Mi idea era ver hasta donde podía preveer. Lo ideal habría sido preveer un turno mío, el turno del rival (al menos su ataque con las criaturas en mesa) y luego el siguiente turno mío. Esto no tuvo éxito ya que en este juego se desconocen demasiados factores (la mano del rival, las de su mazo). Además tenía que repartir la carga entre mis turnos y los del rival, mientras más tiempo le dedicase a los turnos del rival mejor decisión iba a tomar él y peor yo y viceversa.

Al final opté por simular un sólo turno. Que no es poco, ya que en un turno del juego hay que realizar muchas acciones y el orden importa. Si en el campo cada jugador tiene 5 criaturas, hay que tener en cuenta qué criatura ataca a cuál, importando el orden de ataque. Además cualquier nº de criaturas u objetos que juegues se pueden intercalar entre estos ataques cambiando mucho el resultado. El ataque entre criaturas era el mayor coste computacional, por lo que, aún simulando un sólo turno, tuve que establecer limitadores en el tiempo de búsqueda.

La función eval de StateManager puntuaba el estado. Aquí tenía en cuenta el nº de criaturas en cada lado, la diferencia de puntuación de las criaturas de cada lado (se puntúa individualmente cada criatura), si algún jugador tiene letal (puede ganar en el siguiente turno) y otros factores. 

Aprendí mucho y quedé en buena posición, así que perfecto. Si participo en otro concurso, no sé qué lenguaje usaré pero tengo claro que no haré el mismo árbol de búsqueda, investigaré como podría implementar otra técnica aquí como pueden ser las redes neuronales y algún tipo de aprendizaje.
