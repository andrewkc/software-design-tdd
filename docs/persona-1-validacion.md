# Módulo de validación — Persona 1

Documento de sustento de `src/validacion.py`, según el acuerdo técnico
del Grupo 2. Metodología: **TDD**.

---

## 1. Qué hace este módulo

Dos funciones, ambas **puras**: no tocan base de datos, no modifican el
lote y no registran nada. Solo responden preguntas.

| Función | Devuelve | Responsabilidad |
|---|---|---|
| `estado_lote(lote, fecha_actual)` | `(estado, texto)` | Etiqueta interna del lote y el texto que ve el personal |
| `validar_venta(lote, cantidad, fecha_venta, revision_hoy=False)` | `None` | Deja pasar la venta o la rechaza con `ValueError` |

`validar_venta` es la primera que llama `registrar_venta` (persona 2).
Si lanza, no se calcula precio ni se crea movimiento: la venta se
detiene ahí.

## 2. La tabla del acuerdo, implementada

El orden de evaluación **es el orden de la tabla**, y eso importa: los
bloqueos del personal pesan más que cualquier estado de fecha.

| Condición | Estado | Venta |
|---|---|---|
| `deteriorado` o `bloqueado` | `BLOQUEADO` | Bloqueada |
| Perecible sin fecha | `SIN_FECHA` | Bloqueada |
| `dias < 0` | `VENCIDO` | Bloqueada |
| `dias == 0` | `HOY` | Solo con `revision_hoy=True` |
| `1 <= dias <= 3` | `PROXIMO` | Permitida |
| `dias > 3` o fecha no aplicable | `NORMAL` | Permitida |

Un caso que conviene subrayar: **la revisión del día no habilita un
lote deteriorado.** Como el bloqueo se evalúa antes que la fecha, un
lote deteriorado que además vence hoy sale como `BLOQUEADO`, y
`revision_hoy=True` no cambia nada. Está cubierto por la prueba 4.7.

## 3. Decisiones de diseño que puedo defender

**`validar_venta` reutiliza `estado_lote` en vez de repetir las
condiciones.** Si mañana el equipo cambia la ventana de alerta o agrega
un estado, hay un solo lugar que tocar. El precio de esta decisión es
que las dos funciones quedan acopladas, pero es el acoplamiento
correcto: la segunda pregunta *"¿en qué estado está?"* y no necesita
saber cómo se calcula.

**Las etiquetas y los textos son constantes, no literales sueltos.**
Los textos son un acuerdo entre tres personas; si alguien corrige una
redacción, debe poder hacerlo en un lugar y no buscarla por el archivo.
Lo mismo con las etiquetas: eran cadenas repetidas en las dos
funciones, y un error de tipeo no habría fallado ruidosamente, solo
habría dado una comparación falsa en silencio.

**La columna "Venta" quedó como dato, no como código.**
`ESTADOS_QUE_BLOQUEAN` es un conjunto, así que la regla se lee de un
vistazo y se compara contra la tabla del acuerdo sin interpretar
condicionales.

**La ventana de 3 días es una constante documentada.** El acuerdo dice
que es una decisión del equipo para este prototipo y que no representa
una garantía sanitaria. Eso está escrito junto a la constante, donde
alguien que la cambie lo va a leer.

## 4. Las 23 pruebas

| # | Caso | Tipo |
|---|---|---|
| 1.1 | Fecha lejana → `NORMAL` con la fecha visible | Normal |
| 1.2 | Tres días antes → `PROXIMO` | Límite |
| 1.3 | Un día antes → `PROXIMO` | Límite |
| 1.4 | Vence hoy → `HOY` | Límite |
| 1.5 | Fecha pasada → `VENCIDO` | Límite |
| 2.1 | Lote deteriorado → `BLOQUEADO` | Normal |
| 2.2 | Lote marcado bloqueado → `BLOQUEADO` | Normal |
| 2.3 | Deteriorado **y** vencido → `BLOQUEADO` | Límite |
| 2.4 | Perecible sin fecha → `SIN_FECHA` | Límite |
| 2.5 | Producto sin fecha aplicable → `NORMAL` | Límite |
| 3.1 | Venta válida no lanza | Normal |
| 3.2 | Cantidad cero → error | Error |
| 3.3 | Cantidad negativa → error | Error |
| 3.4 | Cantidad mayor al stock → error | Error |
| 3.5 | Cantidad igual al stock → aceptada | Límite |
| 4.1 | Lote bloqueado → error | Error |
| 4.2 | Lote deteriorado → error | Error |
| 4.3 | Lote vencido → error | Error |
| 4.4 | Perecible sin fecha → error | Error |
| 4.5 | Vence hoy sin revisión → error | Error |
| 4.6 | Vence hoy con revisión → aceptada | Límite |
| 4.7 | La revisión no habilita un deteriorado | Límite |
| 4.8 | Próximo a vencer → se puede vender | Normal |

```
23 passed
```

## 5. Los ciclos, verificables en Git

```bash
git log --oneline --reverse
```

| Ciclo | RED | GREEN | REFACTOR |
|---|---|---|---|
| 1 — Estados por fecha | `8336364` | `9fdbf22` | `998cd59` |
| 2 — Prioridad de bloqueos | `749a732` | `e7ffb9b` | `2b20f35` |
| 3 — Cantidad y stock | `886cf74` | `b41eff1` + `7e2a57a` | `89e97c9` |
| 4 — Estados que bloquean | `3181f10` | `8adeb61` | `778b87a` |

La salida real de pytest de cada paso está en `tests/evidencias/`.

**Sobre el ciclo 3:** el GREEN necesitó dos commits. El primero
(`b41eff1`) declaraba la suite en verde y no lo estaba: el mensaje de
error empezaba con "Stock" en mayúscula y la prueba buscaba "stock",
que distingue mayúsculas. El error quedó en el historial y se corrigió
en `7e2a57a`, en lugar de reescribir los commits. La regla 2 del
acuerdo pide evidencia real, y eso incluye los tropiezos.

## 6. Decisiones de interpretación del acuerdo

Dos puntos del acuerdo admitían más de una lectura. Se resolvieron a
favor del texto literal, para que el módulo encaje con el de los demás
integrantes sin sorpresas.

**El texto se respeta en singular y plural.** El acuerdo fija «Vence en
X días», así que a un día del vencimiento el sistema muestra «Vence en
1 días». Se mantuvo literal: el texto es un acuerdo entre tres
personas, y cambiarlo por cuenta propia rompería las pruebas de los
demás. La prueba 1.3 lo deja documentado.

**Si hay fecha, se aplican las reglas de fecha.** El acuerdo indica que
un producto sin fecha aplicable lleva `perecible=False` y `vence=None`,
y también que «la fecha se muestra siempre que exista». De ahí que un
lote con fecha registrada reciba su estado por fecha aunque
`perecible` sea `False`. Un producto sin fecha y no perecible queda
como `NORMAL` con «Fecha no aplicable», que es el caso 2.5.

## 7. Cómo correr las pruebas

```bash
pip install -r requirements.txt
pytest
```

```
23 passed
```
