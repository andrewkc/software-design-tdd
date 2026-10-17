# TDD aplicado al registro de ventas en bodegas

Trabajo del Grupo 2 del curso Diseño de Software. Aplicamos **Test-Driven Development (TDD)** a una parte de CU-05 del proyecto de bodegas: confirmar la venta de un producto desde un lote.

## Integrantes

- Diaz Ysla, Walter Alexander
- Champi Hinojosa, Miguel Angel
- Cahuana Condori, Kelvin Andreí

## Problema y alcance

Antes de registrar una salida por venta comprobamos la cantidad solicitada, el stock y el estado del lote. Después seleccionamos el precio regular o una promoción aprobada y vigente. La operación devuelve un lote nuevo con el stock reducido una sola vez y un movimiento con responsable, cantidad, precio y total. Si la validación falla, el lote original permanece intacto.

La lógica de venta funciona en memoria. Un adaptador PostgreSQL separado guarda el lote actualizado y el movimiento cuando se necesita persistencia. No incluye múltiples productos o lotes por venta, permisos, cancelaciones ni mermas. No cubre todo CU-05.

## Metodología y tecnologías

Usamos Python 3.10 o superior, pytest, PostgreSQL, Docker Compose y Git. Organizamos el trabajo en ciclos **RED → GREEN → REFACTOR**: primero definimos un comportamiento mediante una prueba, después escribimos el código necesario para pasarla y finalmente mejoramos el diseño con la suite en verde. Los cuatro módulos de negocio separan validación, selección de precio, movimiento e integración.

| Módulo | Responsabilidad |
| --- | --- |
| `src/validacion.py` | Determinar el estado del lote y rechazar ventas inválidas. |
| `src/precios.py` | Seleccionar el precio aplicable. |
| `src/movimientos.py` | Devolver el nuevo lote y el movimiento de salida. |
| `src/venta.py` | Ejecutar validación, precio y movimiento en ese orden. |
| `src/repositorio_ventas.py` | Definir el contrato de persistencia, sin importar una base de datos. |
| `src/venta_aplicacion.py` | Coordinar la venta con cualquier repositorio que cumpla el contrato. |
| `src/infraestructura/postgres_ventas.py` | Guardar lotes y movimientos en PostgreSQL de forma transaccional. |
| `db/schema.sql` | Definir las tablas, separado del código de negocio. |

Las fechas son objetos `datetime.date` y los importes son enteros en centavos. `1000` representa S/ 10,00. El [contrato técnico](docs/contrato.md) reúne las entradas, salidas y reglas compartidas.

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, el entorno se activa con `source .venv/bin/activate`. También es posible instalar la dependencia directamente con `python -m pip install -r requirements.txt`.

## Ejecución

La demostración muestra una venta promocional aceptada y una venta rechazada por deterioro:

```powershell
python demo.py
```

En la primera operación el stock pasa de 5 a 3 y el total es S/ 16,00. En la segunda se muestra el motivo del rechazo y el stock sigue en 5.

## Separación de la base de datos

`registrar_venta` y las reglas de negocio no importan PostgreSQL. La aplicación depende del contrato `RepositorioVentas`; solo el adaptador en `src/infraestructura/` conoce las consultas SQL. Docker Compose inicia PostgreSQL y ejecuta `db/schema.sql` al crear el volumen por primera vez:

```powershell
docker compose up -d --wait
```

La base queda disponible en `127.0.0.1:5434` (puerto configurable con `POSTGRES_HOST_PORT`). Para registrar una venta persistida:

```python
import psycopg
from datetime import date

from src.infraestructura.postgres_ventas import RepositorioVentasPostgres
from src.venta_aplicacion import registrar_venta_persistida

with psycopg.connect(
    "postgresql://bodegas:bodegas@127.0.0.1:5434/bodegas", autocommit=True
) as conexion:
    conexion.execute(
        "INSERT INTO lotes (id, stock, perecible, vence, deteriorado, bloqueado) "
        "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
        ("L1", 5, True, date(2026, 10, 1), False, False),
    )
    nuevo_lote, movimiento = registrar_venta_persistida(
        RepositorioVentasPostgres(conexion), "L1", 2, date(2026, 9, 27),
        1000, None, "Ana",
    )
```

El adaptador bloquea el lote durante la transacción, aplica las reglas y guarda ambos resultados; si la venta falla, revierte la transacción. La conexión debe crearse con `autocommit=True`. El esquema se inicializa solo en un volumen vacío de Docker.

## Pruebas

```powershell
python -m pytest -p no:cacheprovider -q
```

Para incluir las tres pruebas de integración con PostgreSQL, inicia Docker Compose y configura la conexión de pruebas antes de ejecutar el comando:

```powershell
$env:TEST_DATABASE_URL = "postgresql://bodegas:bodegas@127.0.0.1:5434/bodegas"
python -m pytest -p no:cacheprovider -q
```

La suite contiene **38 pruebas**: 23 de validación, 5 de precios, 2 de movimientos, 4 de integración y 4 de persistencia. Las tres pruebas que requieren PostgreSQL se omiten si `TEST_DATABASE_URL` no está configurada. El comando `-p no:cacheprovider` evita crear archivos de caché; no cambia las pruebas.

## Documentación y evidencias

- [Evidencias TDD y resultados](docs/evidencias.md)
- [Contrato técnico](docs/contrato.md)
- [Conclusiones del equipo](docs/conclusiones.md)
- [Validación](docs/persona-1.md), [precios e integración](docs/persona-2.md) y [movimientos](docs/persona-3.md)
