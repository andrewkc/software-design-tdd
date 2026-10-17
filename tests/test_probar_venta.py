from probar_venta import main, mostrar_escenarios
from tests.escenarios_cu05 import ESCENARIOS, Escenario, lote


def test_el_catalogo_completo_coincide_con_lo_esperado(capsys):
    assert main([]) == 0

    salida = capsys.readouterr().out
    assert f"{len(ESCENARIOS)} escenarios" in salida
    assert "0 no coinciden" in salida


def test_el_ejecutor_avisa_cuando_un_escenario_no_coincide(capsys):
    equivocado = Escenario(
        id="expectativa_equivocada",
        flujo="prueba",
        descripcion="Espera un stock que la venta no deja",
        lote=lote(),
        cantidad=2,
        stock_final=99,
        precio_unitario=1000,
    )

    assert mostrar_escenarios([equivocado]) == 1
    assert "FALLA" in capsys.readouterr().out


def test_un_escenario_inexistente_termina_con_error(capsys):
    assert main(["-e", "no_existe"]) == 2
    assert "No existe" in capsys.readouterr().out


def test_un_caso_propio_rechazado_muestra_el_motivo(capsys):
    assert main(["propio", "--deteriorado"]) == 0

    salida = capsys.readouterr().out
    assert "RECHAZADA" in salida
    assert "BLOQUEADO" in salida


def test_un_caso_propio_aceptado_muestra_el_total(capsys):
    main(["propio", "--cantidad", "3"])

    salida = capsys.readouterr().out
    assert "PROCEDE" in salida
    assert "total S/ 30,00" in salida
