# Casos de uso de la venta (CU-05)

El caso de uso **CU-05 — Registrar salidas por venta, vencimiento o deterioro** se describe en el modelado de negocio del equipo con un flujo principal, excepciones y reglas de negocio. Este documento reúne **28 escenarios ejecutables** que recorren la parte de venta de ese caso de uso: 14 que deben proceder y 14 que deben rechazarse.

Cada escenario se puede **verificar** con pytest y **ver funcionando** con `probar_venta.py`. Los dos usan el mismo catálogo, que está en `tests/escenarios_cu05.py`, de modo que lo que se muestra es lo que se prueba.

## Cómo probar

Desde la raíz del repositorio:

```powershell
python probar_venta.py                        # los 28 escenarios, con su resultado
python probar_venta.py --lista                # cada escenario con su código del modelado
python probar_venta.py -e lote_deteriorado    # un escenario, con su explicación
python probar_venta.py --secuencia            # vender hasta agotar el lote
python -m pytest tests/test_casos_de_uso.py -q
```

El ejecutor marca cada línea con `ok` cuando el resultado coincide con lo esperado y con `FALLA` cuando no. Termina con código 1 si algún escenario no coincide.

### Probar un caso propio

Con `propio` se arma una venta con datos libres y se ve si procede o se rechaza, y por qué:

```powershell
python probar_venta.py propio --deteriorado --promocion 800:2026-09-25:2026-09-30
```

```
Lote:       stock 5, vence 2026-10-10
Estado:     BLOQUEADO - En observación: revisar y retirar de la venta
Venta:      2 unidades el 2026-09-27, precio regular S/ 10,00
Promoción:  S/ 8,00 del 2026-09-25 al 2026-09-30, aprobada, activa
Resultado:  RECHAZADA
            No se puede vender este lote. En observación: revisar y retirar de la venta
```

```powershell
python probar_venta.py propio --vence 2026-09-27 --revision --cantidad 3
```

```
Lote:       stock 5, vence 2026-09-27
Estado:     HOY - Vence hoy: revisar antes de vender
Venta:      3 unidades el 2026-09-27, precio regular S/ 10,00
Resultado:  PROCEDE
            stock 5 -> 2 | precio S/ 10,00 | total S/ 30,00
```

| Opción | Significado | Valor por defecto |
| --- | --- | --- |
| `--stock` | Stock del lote | 5 |
| `--cantidad` | Unidades que se venden | 2 |
| `--vence` | Fecha de vencimiento `AAAA-MM-DD`, o `ninguna` | 2026-10-10 |
| `--fecha` | Fecha de la venta | 2026-09-27 |
| `--precio` | Precio regular en centavos | 1000 |
| `--promocion` | `PRECIO:INICIO:FIN`, con el precio en centavos | sin promoción |
| `--sin-aprobar` | La promoción no fue aprobada por el jefe | — |
| `--inactiva` | La promoción está marcada como inactiva | — |
| `--deteriorado` | El lote está marcado como deteriorado | — |
| `--bloqueado` | El lote está bloqueado por envase o conservación | — |
| `--no-perecible` | El producto no es perecible | — |
| `--revision` | El personal registró la revisión del día del vencimiento | — |

## Qué verifican las pruebas

Para los escenarios que **proceden**:

- el stock final y el precio unitario son los esperados, y el total es cantidad por precio;
- el movimiento registra el motivo `venta`, el lote, la cantidad y el responsable;
- el lote nuevo solo cambia en el stock.

Para los escenarios que **se rechazan**:

- el motivo del rechazo es el esperado;
- no se genera ni un lote nuevo ni un movimiento.

Para **todos**, el lote de entrada nunca se modifica.

Además, `--secuencia` y sus pruebas encadenan tres ventas sobre el mismo lote: vender 2 de 5, vender 3 de 3 y rechazar la tercera por falta de stock. Comprueban que la suma de lo vendido es exactamente el stock inicial, es decir, que el stock se descuenta una sola vez.

## Trazabilidad con el modelado de negocio

La columna **Modelado** indica el flujo o la excepción de CU-05 y las reglas de negocio que respalda cada escenario. La marca *contrato técnico* señala los casos que no figuran literalmente en las reglas del modelado sino en el [contrato técnico](contrato.md): el bloqueo por envase o conservación, el perecible sin fecha y la revisión del día del vencimiento.

### Flujo principal

| Escenario | Modelado | Qué comprueba | Resultado esperado |
| --- | --- | --- | --- |
| `venta_a_precio_regular` | CU-05 flujo principal · RN-04, RN-05 | Venta de 2 unidades de un lote vigente, sin promoción | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `venta_con_promocion_vigente` | CU-05 flujo principal · RN-05, RN-09 | Venta de 2 unidades con promoción aprobada y vigente: total S/ 16,00 | Procede: stock 5 → 3, precio S/ 8,00, total S/ 16,00 |
| `venta_de_una_unidad` | CU-05 flujo principal · RN-03, RN-04 | La cantidad mínima válida es 1 | Procede: stock 5 → 4, precio S/ 10,00, total S/ 10,00 |
| `venta_de_todo_el_stock` | CU-05 flujo principal · RN-04 | Vender exactamente el stock disponible deja el lote en 0 | Procede: stock 5 → 0, precio S/ 10,00, total S/ 50,00 |
| `producto_sin_fecha_aplicable` | CU-05 flujo principal · RN-06 | Un producto no perecible sin fecha de vencimiento se puede vender | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |

### Selección de precio

| Escenario | Modelado | Qué comprueba | Resultado esperado |
| --- | --- | --- | --- |
| `promocion_en_su_primer_dia` | CU-05 flujo principal · RN-09 | La promoción rige desde el día de inicio | Procede: stock 5 → 3, precio S/ 8,00, total S/ 16,00 |
| `promocion_en_su_ultimo_dia` | CU-05 flujo principal · RN-09 | La promoción rige hasta el día final, inclusive | Procede: stock 5 → 3, precio S/ 8,00, total S/ 16,00 |
| `promocion_ya_vencida` | CU-05 flujo principal · RN-09 | Un día después del fin de la promoción se cobra el precio regular | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `promocion_aun_no_iniciada` | CU-05 flujo principal · RN-09 | Un día antes del inicio de la promoción se cobra el precio regular | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `promocion_no_aprobada` | CU-05 flujo principal · RN-09, CU-08 | Una promoción sin aprobación del jefe no se aplica | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `promocion_inactiva` | CU-05 flujo principal · RN-09, CU-08-FA-05 | Una promoción marcada como inactiva no se aplica | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |

### Límites del lote

| Escenario | Modelado | Qué comprueba | Resultado esperado |
| --- | --- | --- | --- |
| `lote_que_vence_en_3_dias` | CU-05 flujo principal · RN-06, CU-06 | Dentro de la ventana de alerta la venta sigue permitida | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `lote_que_vence_en_1_dia` | CU-05 flujo principal · RN-06, CU-06 | A un día del vencimiento la venta sigue permitida | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |
| `vence_hoy_con_revision` | CU-05 flujo principal · RN-06, contrato técnico | El día del vencimiento procede si el personal registró la revisión | Procede: stock 5 → 3, precio S/ 10,00, total S/ 20,00 |

### Rechazo

| Escenario | Modelado | Qué comprueba | Resultado esperado |
| --- | --- | --- | --- |
| `cantidad_cero` | CU-05-EX-01 · RN-03 | Cantidad 0: no hay nada que vender | Se rechaza: «cantidad» |
| `cantidad_negativa` | CU-05-EX-01 · RN-03 | Una cantidad negativa se rechaza | Se rechaza: «cantidad» |
| `cantidad_mayor_al_stock` | CU-05-EX-01 · RN-04 | Se piden 6 y el lote tiene 5 | Se rechaza: «stock» |
| `lote_sin_stock` | CU-05-EX-01 · RN-04 | Un lote agotado no admite ventas | Se rechaza: «stock» |
| `lote_deteriorado` | CU-05-EX-02 · RN-06 | Un lote marcado como deteriorado no se vende | Se rechaza: «observación» |
| `lote_bloqueado` | CU-05-EX-02 · RN-06, contrato técnico | Un lote bloqueado por envase o conservación no se vende | Se rechaza: «observación» |
| `lote_vencido_ayer` | CU-05-EX-02 · RN-06 | Un día después de la fecha de vencimiento ya no se vende | Se rechaza: «Vencido» |
| `perecible_sin_fecha` | CU-05-EX-02 · RN-06, contrato técnico | Un perecible sin fecha verificada no se vende | Se rechaza: «Fecha sin verificar» |
| `vence_hoy_sin_revision` | CU-05-EX-02 · RN-06, contrato técnico | El día del vencimiento exige la revisión del personal | Se rechaza: «revisión» |
| `deteriorado_que_vence_hoy_con_revision` | CU-05-EX-02 · RN-06 | La revisión del día no habilita un lote deteriorado | Se rechaza: «observación» |
| `bloqueado_que_vence_hoy_con_revision` | CU-05-EX-02 · RN-06, contrato técnico | La revisión del día no habilita un lote bloqueado | Se rechaza: «observación» |
| `deteriorado_y_vencido` | CU-05-EX-02 · RN-06 | El bloqueo por deterioro tiene prioridad sobre el vencimiento | Se rechaza: «observación» |
| `rechazo_con_promocion_vigente` | CU-05-EX-02 · RN-06, RN-09 | Una promoción vigente no salva la venta de un lote deteriorado | Se rechaza: «observación» |
| `no_perecible_con_fecha_vencida` | CU-05-EX-02 · RN-06 | Si hay fecha registrada se aplican las reglas de fecha aunque no sea perecible | Se rechaza: «Vencido» |

## Alcance

Los escenarios cubren la venta: el flujo principal (validación de cantidad y stock, aplicación de precios y promociones, cálculo del total), la excepción **CU-05-EX-01** (cantidad inválida o sin stock) y la excepción **CU-05-EX-02** (producto vencido o deteriorado), con las reglas **RN-03** (cantidades positivas), **RN-04**, **RN-05**, **RN-06** y **RN-09** (vigencia de la promoción).

Quedan fuera de esta demostración, igual que en el resto del trabajo, la merma por vencimiento o deterioro (**CU-05-FA-01**), la cancelación (**CU-05-FA-02**), la revalidación ante cambios concurrentes (**CU-05-EX-03**) y las ventas de varios productos o lotes.

## Cómo se comprobó que las pruebas detectan errores

Las pruebas pasaron desde su primera ejecución porque describen un comportamiento que ya existía. Para comprobar que también pueden fallar, se alteró el código nueve veces, una alteración a la vez, y en las nueve la suite falló:

| Módulo | Alteración |
| --- | --- |
| `src/movimientos.py` | Descontar el stock dos veces |
| `src/movimientos.py` | Modificar el lote original en lugar de devolver uno nuevo |
| `src/precios.py` | Dejar de aplicar la promoción en su último día |
| `src/precios.py` | Ignorar la aprobación del jefe |
| `src/validacion.py` | Omitir la revisión del día del vencimiento |
| `src/validacion.py` | Permitir vender un lote bloqueado |
| `src/validacion.py` | Permitir vender una unidad más que el stock |
| `src/validacion.py` | Aceptar la cantidad cero |
| `src/venta.py` | Registrar la venta sin validar |

Cada alteración se puede reproducir a mano editando la línea correspondiente y ejecutando `python -m pytest tests/test_casos_de_uso.py -q`.
