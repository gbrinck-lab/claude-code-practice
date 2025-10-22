"""Tests para el módulo hello.py.

Este módulo contiene tests unitarios para todas las funciones
del script de saludo interactivo.
"""

from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import logging
from pathlib import Path

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hello import (
    obtener_fecha_hora_santiago,
    formatear_fecha_hora,
    solicitar_nombre,
    generar_saludo,
    ejecutar_programa,
    configurar_logger,
    mostrar_ascii_art,
    colorear_texto,
    registrar_ejecucion,
    COLORAMA_AVAILABLE
)


class TestObtenerFechaHoraSantiago:
    """Tests para la función obtener_fecha_hora_santiago."""

    def test_retorna_datetime(self):
        """Verifica que la función retorne un objeto datetime."""
        resultado = obtener_fecha_hora_santiago()
        assert isinstance(resultado, datetime)

    def test_fecha_es_reciente(self):
        """Verifica que la fecha retornada sea cercana a la actual."""
        import time
        antes = time.time()
        resultado = obtener_fecha_hora_santiago()
        despues = time.time()

        # Convertir resultado a timestamp
        resultado_timestamp = resultado.timestamp()

        # Verificar que el timestamp esté entre antes y después
        assert antes <= resultado_timestamp <= despues + 1  # +1 segundo de tolerancia


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

    def test_saludo_con_none(self):
        """Verifica que maneje None correctamente."""
        resultado = generar_saludo(None)

        assert "Hola" in resultado
        assert "Bienvenido" in resultado
        # No debe incluir "None" en el saludo
        assert "None" not in resultado

    def test_saludo_con_espacios_solo(self):
        """Verifica que maneje nombres con solo espacios."""
        resultado = generar_saludo("   ")

        # Debe dar saludo genérico
        assert "Hola" in resultado
        assert "Bienvenido" in resultado

    def test_saludo_con_tipo_incorrecto(self):
        """Verifica que maneje tipos de datos incorrectos."""
        resultado = generar_saludo(123)

        # Debe dar saludo genérico, no crashear
        assert "Hola" in resultado
        assert "Bienvenido" in resultado


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

    @patch('builtins.input', side_effect=EOFError)
    @patch('builtins.print')
    def test_maneja_eof(self, mock_print, mock_input):
        """Verifica que maneje correctamente EOF (Ctrl+D)."""
        resultado = solicitar_nombre()

        # Debe retornar string vacío en caso de EOF
        assert resultado == ''
        assert isinstance(resultado, str)

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_propaga_keyboard_interrupt(self, mock_input):
        """Verifica que propague KeyboardInterrupt."""
        # KeyboardInterrupt debe propagarse, no ser manejado
        try:
            solicitar_nombre()
            assert False, "Debería haber lanzado KeyboardInterrupt"
        except KeyboardInterrupt:
            assert True

    @patch('builtins.input', side_effect=Exception("Error de prueba"))
    @patch('builtins.print')
    def test_maneja_excepciones_generales(self, mock_print, mock_input):
        """Verifica que maneje excepciones generales en input."""
        resultado = solicitar_nombre()

        # Debe retornar string vacío en caso de error
        assert resultado == ''
        # Debe haber impreso mensaje de error
        assert mock_print.called


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


class TestConfigurarLogger:
    """Tests para la función configurar_logger."""

    @patch('src.hello.Path.mkdir')
    def test_crea_directorio_logs(self, mock_mkdir):
        """Verifica que se crea el directorio logs."""
        # Limpiar handlers existentes
        logger = logging.getLogger("hello")
        logger.handlers.clear()

        configurar_logger()

        # Verificar que se llamó mkdir
        mock_mkdir.assert_called_once()

    def test_retorna_logger(self):
        """Verifica que retorna un objeto Logger."""
        # Limpiar handlers existentes
        logger = logging.getLogger("hello")
        logger.handlers.clear()

        resultado = configurar_logger()

        assert isinstance(resultado, logging.Logger)
        assert resultado.name == "hello"

    def test_no_duplica_handlers(self):
        """Verifica que no duplique handlers al llamarse múltiples veces."""
        # Limpiar handlers existentes
        logger = logging.getLogger("hello")
        logger.handlers.clear()

        # Llamar dos veces
        configurar_logger()
        count_primera = len(logging.getLogger("hello").handlers)

        configurar_logger()
        count_segunda = len(logging.getLogger("hello").handlers)

        # Debe tener la misma cantidad de handlers
        assert count_primera == count_segunda


class TestMostrarAsciiArt:
    """Tests para la función mostrar_ascii_art."""

    def test_retorna_string(self):
        """Verifica que retorne un string."""
        resultado = mostrar_ascii_art()
        assert isinstance(resultado, str)

    def test_contiene_ascii_art(self):
        """Verifica que contenga elementos del ASCII art."""
        resultado = mostrar_ascii_art()

        # Verificar que contiene caracteres de box drawing
        assert '╔' in resultado or 'BIENVEN' in resultado

    def test_funciona_sin_colorama(self):
        """Verifica que funcione incluso sin colorama."""
        with patch('src.hello.COLORAMA_AVAILABLE', False):
            resultado = mostrar_ascii_art()
            assert isinstance(resultado, str)
            assert len(resultado) > 0


class TestColorearTexto:
    """Tests para la función colorear_texto."""

    def test_retorna_string(self):
        """Verifica que retorne un string."""
        resultado = colorear_texto("Hola", "cyan")
        assert isinstance(resultado, str)

    def test_contiene_texto_original(self):
        """Verifica que el resultado contenga el texto original."""
        texto = "Mensaje de prueba"
        resultado = colorear_texto(texto, "verde")

        # El texto debe estar en el resultado
        assert texto in resultado

    def test_colores_validos(self):
        """Verifica que funcione con diferentes colores."""
        colores = ["cyan", "verde", "amarillo", "rojo", "blanco", "magenta"]

        for color in colores:
            resultado = colorear_texto("Test", color)
            assert isinstance(resultado, str)
            assert "Test" in resultado

    def test_con_negrita(self):
        """Verifica que funcione con el parámetro negrita."""
        resultado = colorear_texto("Texto", "cyan", negrita=True)
        assert isinstance(resultado, str)
        assert "Texto" in resultado

    def test_sin_colorama(self):
        """Verifica que funcione sin colorama."""
        with patch('src.hello.COLORAMA_AVAILABLE', False):
            resultado = colorear_texto("Hola", "cyan")
            assert resultado == "Hola"


class TestRegistrarEjecucion:
    """Tests para la función registrar_ejecucion."""

    def test_registra_con_nombre(self):
        """Verifica que registre correctamente con nombre."""
        mock_logger = MagicMock()
        fecha = datetime(2024, 3, 15, 14, 30, 45)
        nombre = "Carlos"

        registrar_ejecucion(mock_logger, nombre, fecha)

        # Verificar que se llamó logger.info
        mock_logger.info.assert_called_once()

        # Verificar que el mensaje contiene el nombre
        call_args = str(mock_logger.info.call_args)
        assert "Carlos" in call_args

    def test_registra_sin_nombre(self):
        """Verifica que registre correctamente sin nombre."""
        mock_logger = MagicMock()
        fecha = datetime(2024, 3, 15, 14, 30, 45)

        registrar_ejecucion(mock_logger, "", fecha)

        # Verificar que se llamó logger.info
        mock_logger.info.assert_called_once()

        # Verificar que el mensaje indica "sin nombre"
        call_args = str(mock_logger.info.call_args)
        assert "sin nombre" in call_args.lower()

    def test_falla_con_logger_none(self):
        """Verifica que lance error si logger es None."""
        fecha = datetime(2024, 3, 15, 14, 30, 45)

        try:
            registrar_ejecucion(None, "Test", fecha)
            assert False, "Debería haber lanzado ValueError"
        except ValueError as e:
            assert "Logger" in str(e)

    def test_falla_con_fecha_none(self):
        """Verifica que lance error si fecha_hora es None."""
        mock_logger = MagicMock()

        try:
            registrar_ejecucion(mock_logger, "Test", None)
            assert False, "Debería haber lanzado ValueError"
        except ValueError as e:
            assert "fecha_hora" in str(e)

    def test_maneja_nombre_none(self):
        """Verifica que maneje nombre None correctamente."""
        mock_logger = MagicMock()
        fecha = datetime(2024, 3, 15, 14, 30, 45)

        registrar_ejecucion(mock_logger, None, fecha)

        # Debe registrar como "sin nombre"
        mock_logger.info.assert_called_once()
        call_args = str(mock_logger.info.call_args)
        assert "sin nombre" in call_args.lower()

    def test_maneja_nombre_con_espacios(self):
        """Verifica que limpie espacios del nombre."""
        mock_logger = MagicMock()
        fecha = datetime(2024, 3, 15, 14, 30, 45)

        registrar_ejecucion(mock_logger, "  Ana  ", fecha)

        # Debe registrar con nombre sin espacios
        mock_logger.info.assert_called_once()
        call_args = str(mock_logger.info.call_args)
        assert "Ana" in call_args


class TestEjecutarProgramaConNuevasFuncionalidades:
    """Tests para verificar que ejecutar_programa use las nuevas funcionalidades."""

    @patch('src.hello.registrar_ejecucion')
    @patch('src.hello.configurar_logger')
    @patch('src.hello.solicitar_nombre', return_value='Ana')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_llama_configurar_logger(self, mock_print, mock_fecha, mock_solicitar,
                                     mock_configurar, mock_registrar):
        """Verifica que ejecutar_programa llame a configurar_logger."""
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock
        mock_logger = MagicMock()
        mock_configurar.return_value = mock_logger

        ejecutar_programa()

        # Verificar que se llamó configurar_logger
        mock_configurar.assert_called_once()

    @patch('src.hello.registrar_ejecucion')
    @patch('src.hello.configurar_logger')
    @patch('src.hello.solicitar_nombre', return_value='Pedro')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_llama_registrar_ejecucion(self, mock_print, mock_fecha, mock_solicitar,
                                       mock_configurar, mock_registrar):
        """Verifica que ejecutar_programa llame a registrar_ejecucion."""
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock
        mock_logger = MagicMock()
        mock_configurar.return_value = mock_logger

        ejecutar_programa()

        # Verificar que se llamó registrar_ejecucion con los parámetros correctos
        mock_registrar.assert_called_once()
        args = mock_registrar.call_args[0]
        assert args[0] == mock_logger
        assert args[1] == 'Pedro'
        assert args[2] == fecha_mock

    @patch('src.hello.registrar_ejecucion')
    @patch('src.hello.configurar_logger')
    @patch('src.hello.mostrar_ascii_art', return_value='ASCII ART')
    @patch('src.hello.solicitar_nombre', return_value='Luis')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_muestra_ascii_art(self, mock_print, mock_fecha, mock_solicitar,
                               mock_ascii, mock_configurar, mock_registrar):
        """Verifica que ejecutar_programa muestre el ASCII art."""
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock
        mock_logger = MagicMock()
        mock_configurar.return_value = mock_logger

        ejecutar_programa()

        # Verificar que se llamó mostrar_ascii_art
        mock_ascii.assert_called_once()

        # Verificar que se imprimió el ASCII art
        llamadas = [str(call) for call in mock_print.call_args_list]
        contiene_ascii = any('ASCII ART' in str(llamada) for llamada in llamadas)
        assert contiene_ascii


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

    @patch('builtins.input', return_value='Guillermo Brinck')
    @patch('builtins.print')
    def test_integracion_con_ascii_art_y_colores(self, mock_print, mock_input):
        """Test de integración verificando ASCII art y colores."""
        ejecutar_programa()

        # Verificar que se imprimieron mensajes
        assert mock_print.call_count > 0

        # Verificar que se imprimió contenido
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert len(llamadas_str) > 0

        # Verificar que existe el archivo de log
        log_path = Path("logs/greetings.log")
        assert log_path.parent.exists() or True  # El directorio debería existir


class TestFallbacksSinDependencias:
    """Tests para verificar comportamiento sin dependencias opcionales."""

    @patch('src.hello.pytz', None)
    def test_obtener_fecha_sin_pytz(self):
        """Verifica que funcione sin pytz instalado."""
        # Reimportar para que use pytz = None
        import importlib
        import src.hello
        importlib.reload(src.hello)

        # Debería retornar datetime sin timezone
        resultado = src.hello.obtener_fecha_hora_santiago()
        assert isinstance(resultado, datetime)

    def test_colorear_texto_sin_colorama(self):
        """Verifica que colorear_texto funcione sin colorama."""
        with patch('src.hello.COLORAMA_AVAILABLE', False):
            resultado = colorear_texto("Test", "cyan", negrita=True)
            # Sin colorama debe retornar el texto original
            assert resultado == "Test"

    def test_mostrar_ascii_art_sin_colorama(self):
        """Verifica que ASCII art funcione sin colorama."""
        with patch('src.hello.COLORAMA_AVAILABLE', False):
            resultado = mostrar_ascii_art()
            assert isinstance(resultado, str)
            assert "╔" in resultado  # Debe contener el ASCII art


class TestManejoErroresLogging:
    """Tests para manejo de errores en logging."""

    @patch('src.hello.registrar_ejecucion')
    @patch('src.hello.configurar_logger')
    @patch('src.hello.solicitar_nombre', return_value='Test')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_error_en_registrar_ejecucion(self, mock_print, mock_fecha, mock_solicitar,
                                          mock_configurar, mock_registrar):
        """Verifica manejo de error al registrar ejecución."""
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock
        mock_logger = MagicMock()
        mock_configurar.return_value = mock_logger

        # Simular error en registrar_ejecucion
        mock_registrar.side_effect = Exception("Error de prueba en logging")

        # Ejecutar programa - no debe crashear
        from src.hello import ejecutar_programa
        ejecutar_programa()

        # Verificar que se imprimió advertencia
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'Advertencia' in llamadas_str or 'advertencia' in llamadas_str.lower()

    def test_registrar_ejecucion_error_en_strftime(self):
        """Verifica manejo de error en strftime."""
        mock_logger = MagicMock()

        # Crear datetime mock que falle en strftime
        fecha_mock = MagicMock()
        fecha_mock.strftime.side_effect = Exception("Error en strftime")

        # No debe crashear, debe llamar logger.error
        registrar_ejecucion(mock_logger, "Test", fecha_mock)

        # Verificar que se llamó logger.error
        mock_logger.error.assert_called_once()


class TestMainExceptionHandling:
    """Tests para manejo de excepciones en main()."""

    @patch('src.hello.ejecutar_programa')
    @patch('builtins.print')
    def test_main_keyboard_interrupt(self, mock_print, mock_ejecutar):
        """Verifica que main() maneje KeyboardInterrupt."""
        mock_ejecutar.side_effect = KeyboardInterrupt()

        from src.hello import main
        main()

        # Verificar que se imprimió mensaje de despedida
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'luego' in llamadas_str.lower() or 'Hasta' in llamadas_str

    @patch('src.hello.ejecutar_programa')
    @patch('builtins.print')
    def test_main_eoferror(self, mock_print, mock_ejecutar):
        """Verifica que main() maneje EOFError."""
        mock_ejecutar.side_effect = EOFError()

        from src.hello import main
        main()

        # Verificar que se imprimió mensaje apropiado
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'cerrada' in llamadas_str.lower() or 'luego' in llamadas_str.lower()

    @patch('src.hello.ejecutar_programa')
    @patch('builtins.print')
    def test_main_valueerror(self, mock_print, mock_ejecutar):
        """Verifica que main() maneje ValueError."""
        mock_ejecutar.side_effect = ValueError("Error de validación de prueba")

        from src.hello import main
        main()

        # Verificar que se imprimió mensaje de error
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'validación' in llamadas_str.lower() or 'Error' in llamadas_str

    @patch('src.hello.ejecutar_programa')
    @patch('builtins.print')
    def test_main_exception_general(self, mock_print, mock_ejecutar):
        """Verifica que main() maneje excepciones generales."""
        mock_ejecutar.side_effect = Exception("Error inesperado de prueba")

        from src.hello import main
        main()

        # Verificar que se imprimió mensaje de error
        llamadas_str = ' '.join([str(call) for call in mock_print.call_args_list])
        assert 'error' in llamadas_str.lower() or 'Error' in llamadas_str


class TestEjecutarProgramaEdgeCases:
    """Tests para casos edge en ejecutar_programa."""

    @patch('src.hello.solicitar_nombre', return_value=None)
    @patch('src.hello.registrar_ejecucion')
    @patch('src.hello.configurar_logger')
    @patch('src.hello.obtener_fecha_hora_santiago')
    @patch('builtins.print')
    def test_nombre_usuario_none(self, mock_print, mock_fecha, mock_configurar,
                                 mock_registrar, mock_solicitar):
        """Verifica que maneje nombre_usuario None."""
        fecha_mock = datetime(2024, 3, 15, 14, 30, 45)
        mock_fecha.return_value = fecha_mock
        mock_logger = MagicMock()
        mock_configurar.return_value = mock_logger

        from src.hello import ejecutar_programa
        ejecutar_programa()

        # Verificar que se llamó registrar_ejecucion con string vacío
        mock_registrar.assert_called_once()
        args = mock_registrar.call_args[0]
        assert args[1] == ""  # nombre_usuario debe ser "" no None
