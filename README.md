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
mejor puntuación tienen. La forma de conseguir las mejores puntuaciones es muy aproximada, ya que se hace con una heap queue.

La profundidad del árbol es de 4, significando esto que se van a simular 4 turnos en el futuro.

Esta vez conseguí hacer alrededor de 1000 simulaciones, pero seguían siendo muy pocas y no encontraba ninguna forma de aumentarlas más.

Al final acabé dejando el concurso a la mitad, ya que no veia forma de aumentar el nº de simulaciones.

Si quiero hacer simulaciones, lo más probablem es que necesite un lenguaje como c++.
