# Guia de capturas - Persona 3

## Diapositiva 13: ciclo 3 RED-GREEN-REFACTOR

1. `01_reconstruccion_red_pruebas_antes_codigo.png`: pruebas escritas antes de crear el modulo.
2. `02_reconstruccion_red_ejecucion_fallida.png`: RED real de la reconstruccion aislada; falla porque `src.movimientos` aun no existe.
3. `03_reconstruccion_green_codigo_minimo.png`: implementacion minima para satisfacer las dos pruebas.
4. `04_reconstruccion_green_dos_pruebas_aprobadas.png`: GREEN con las dos pruebas aprobadas.
5. `05_reconstruccion_refactor_codigo_mejorado.png`: extraccion del calculo del total y constante para el motivo.
6. `06_reconstruccion_refactor_pruebas_siguen_aprobadas.png`: comprobacion posterior al refactor.

Texto breve sugerido para la diapositiva:

> En el ciclo 3 escribimos primero dos pruebas: descontar el stock exactamente una vez sin modificar el lote original y registrar todos los datos del movimiento. La primera ejecucion fallo porque el modulo aun no existia. Despues implementamos el codigo minimo y ambas pruebas pasaron. Finalmente separamos el calculo del total y el motivo de venta, manteniendo las pruebas en verde.

Ejemplo para explicar oralmente: stock inicial 5, venta de 2 unidades, stock nuevo 3; precio unitario 800 centavos y total 1600 centavos (S/ 16,00).

## Diapositiva 15: evidencia Git

7. `07_real_historial_git_persona_3.png`: historial real de la rama despues de agregar las evidencias.

La reconstruccion reproduce con ejecuciones reales los estados RED, GREEN y REFACTOR. El commit original contiene el resultado final del ciclo; los commits posteriores agregan las evidencias documentales por etapa.

## Orden recomendado en la presentacion

- Mostrar juntas las capturas 01 y 02 para RED.
- Mostrar juntas las capturas 03 y 04 para GREEN.
- Mostrar juntas las capturas 05 y 06 para REFACTOR.
- Usar la captura 07 en la diapositiva de Git.

No usar todavia cifras de pruebas grupales ni capturas del ciclo 4 hasta integrar las ramas de las personas 1 y 2.
