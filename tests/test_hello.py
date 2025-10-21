"""Tests para el módulo hello.py.

Este módulo contiene tests unitarios para todas las funciones
del script de saludo interactivo.
"""

from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hello import (
    obtener_fecha_hora_santiago,
    formatear_fecha_hora,
    solicitar_nombre,
    generar_saludo,
    ejecutar_programa
)


class TestObtenerFechaHoraSantiago:
    """Tests para la función obtener_fecha_hora_santiago."""

    def test_retorna_datetime(self):
        """Verifica que la función retorne un objeto datetime."""
        resultado = obtener_fecha_hora_santiago()
        assert isinstance(resultado, datetime)

    def test_fecha_es_reciente(self):
        """Verifica que la fecha retornada sea cercana a la actual."""
        resultado = obtener_fecha_hora_santiago()
        ahora = datetime.now()
        # La diferencia debería ser menor a 1 minuto
        diferencia = abs((ahora - resultado.replace(tzinfo=None)).total_seconds())
        assert diferencia < 60


class TestFormatearFechaHora:
    """Tests para la función formatear_fecha_hora."""

    def test_formato_correcto(self):
        """Verifica que el formato de salida sea correcto."""
        fecha_test = datetime(2024, 3, 15, 14, 30, 45)
        resultado = formatear_fecha_hora(fecha_test)

        assert "15/03/2024" in resultado
        assert "14:30:45" in resultado
        assert "Fecha:" in resultado
        assert "Hora:" in resultado

    def test_formato_con_ceros(self):
        """Verifica el formato con fechas que incluyen ceros."""
        fecha_test = datetime(2024, 1, 5, 9, 5, 3)
        resultado = formatear_fecha_hora(fecha_test)

        assert "05/01/2024" in resultado
        assert "09:05:03" in resultado


class TestGenerarSaludo:
    """Tests para la función generar_saludo."""

    def test_saludo_con_nombre(self):
        """Verifica que el saludo incluya el nombre proporcionado."""
        nombre = "Juan"
        resultado = generar_saludo(nombre)

        assert "Juan" in resultado
        assert "Hola" in resultado
        assert "Bienvenido" in resultado

    def test_saludo_sin_nombre(self):
        """Verifica que funcione sin nombre."""
        resultado = generar_saludo()

        assert "Hola" in resultado
        assert "Bienvenido" in resultado

    def test_saludo_con_nombre_vacio(self):
        """Verifica el comportamiento con nombre vacío."""
        resultado = generar_saludo("")

        # Con string vacío, debería dar saludo genérico
        assert "Hola" in resultado

    def test_saludo_con_nombre_largo(self):
        """Verifica que funcione con nombres largos."""
        nombre = "María José Fernández González"
        resultado = generar_saludo(nombre)

        assert nombre in resultado


class TestSolicitarNombre:
    """Tests para la función solicitar_nombre."""

    @patch('builtins.input', return_value='Carlos')
    def test_solicita_y_retorna_nombre(self, mock_input):
        """Verifica que solicite y retorne el nombre correctamente."""
        resultado = solicitar_nombre()

        assert resultado == 'Carlos'
        mock_input.assert_called_once()

    @patch('builtins.input', return_value='  Ana  ')
    def test_elimina_espacios(self, mock_input):
        """Verifica que elimine espacios al inicio y final."""
        resultado = solicitar_nombre()

        assert resultado == 'Ana'

    @patch('builtins.input', return_value='')
    def test_nombre_vacio(self, mock_input):
        """Verifica el manejo de entrada vacía."""
        resultado = solicitar_nombre()

        assert resultado == ''


class TestEjecutarPrograma:
    """Tests para la función ejecutar_programa."""

    @patch('src.hello.solicitar_nombre', return_value='Pedro')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_flujo_completo_con_nombre(self, mock_print, mock_fecha, mock_solicitar):
        """Verifica el flujo completo del programa con nombre."""
        # Configurar mock de fecha
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock

        # Ejecutar programa
        ejecutar_programa()

        # Verificar que se llamaron las funciones
        mock_solicitar.assert_called_once()
        mock_fecha.assert_called_once()

        # Verificar que se imprimió algo
        assert mock_print.call_count > 0

        # Verificar que se imprimió el nombre
        llamadas = [str(call) for call in mock_print.call_args_list]
        contiene_nombre = any('Pedro' in str(llamada) for llamada in llamadas)
        assert contiene_nombre

    @patch('src.hello.solicitar_nombre', return_value='')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_flujo_completo_sin_nombre(self, mock_print, mock_fecha, mock_solicitar):
        """Verifica el flujo completo del programa sin nombre."""
        # Configurar mock de fecha
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock

        # Ejecutar programa
        ejecutar_programa()

        # Verificar que se llamaron las funciones
        mock_solicitar.assert_called_once()
        mock_fecha.assert_called_once()

        # Verificar que se imprimió algo
        assert mock_print.call_count > 0


class TestIntegracion:
    """Tests de integración para verificar el comportamiento completo."""

    @patch('builtins.input', return_value='María')
    @patch('builtins.print')
    def test_integracion_completa(self, mock_print, mock_input):
        """Test de integración del flujo completo."""
        ejecutar_programa()

        # Verificar que se imprimieron mensajes
        assert mock_print.call_count > 0

        # Verificar que se solicitó el nombre
        mock_input.assert_called_once()

        # Verificar que se imprimieron los elementos clave
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'Hola' in llamadas_str or 'hola' in llamadas_str.lower()
        assert 'María' in llamadas_str
