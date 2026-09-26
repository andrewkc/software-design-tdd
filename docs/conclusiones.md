# Conclusiones del equipo

Aplicamos TDD a una parte de CU-05: confirmar la venta de un producto desde un lote. La implementación integrada contiene cuatro módulos y 34 pruebas automatizadas que cubren casos normales, límites y errores.

## 1. ¿Qué cambió en nuestra manera habitual de desarrollar software?

Definimos primero comportamientos verificables: cuándo una venta se rechaza, qué precio se aplica y cómo cambia el stock. Esas pruebas marcaron el alcance de cada módulo y permitieron comprobar los cambios al integrarlos.

## 2. ¿Qué ventajas encontramos?

Las pruebas nos dieron una forma rápida de confirmar reglas concretas. Por ejemplo, la prueba de venta promocional verifica simultáneamente precio, total y stock; la de deterioro comprueba que una venta inválida no cambia el lote. Al hacer explícitos los argumentos entre módulos, las cuatro pruebas de integración siguieron pasando.

## 3. ¿Qué dificultades encontramos?

Tuvimos que acordar la representación del dinero y de los lotes antes de conectar los módulos. También distinguimos entre validar una venta y registrar su movimiento: el movimiento recibe una operación ya validada. Conservar salidas y commits de cada etapa requirió trabajo adicional al código.

## 4. ¿Qué impacto tuvo sobre el diseño del código?

Separamos estado y validación del lote, selección de precio, creación de movimiento y coordinación de la venta. `registrar_venta` llama a esas funciones en un orden visible. `crear_movimiento` devuelve un lote nuevo, lo que permite comprobar que la entrada no se modifica.

## 5. ¿Qué impacto tuvo sobre la calidad?

Las 34 pruebas pasan en la rama integrada y detectan errores en cantidad, stock, vencimiento, deterioro, vigencia de promociones y resultado del movimiento. Esto respalda la calidad de los comportamientos cubiertos. No medimos una reducción de defectos fuera de esos casos ni implementamos persistencia o concurrencia.

## 6. ¿Utilizaríamos TDD nuevamente?

Sí, especialmente cuando las reglas pueden expresarse como entradas y resultados claros. Mantendríamos los ciclos pequeños y guardaríamos la evidencia de cada ejecución junto con el cambio correspondiente.

## 7. ¿En qué proyectos sería más apropiado?

En funcionalidades con reglas de negocio comprobables, como inventario, reservas, pedidos o pagos. En nuestro caso ayudó a precisar el límite entre validación, cálculo de precio y actualización del stock.
