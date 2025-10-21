"""Script de saludo interactivo con fecha y hora de Santiago de Chile.

Este módulo proporciona funciones para saludar al usuario en español,
mostrar la fecha y hora actual de Santiago de Chile, y personalizar
el saludo con el nombre del usuario. Incluye output con colores,
ASCII art de bienvenida y logging de ejecuciones.
"""

import os
import logging
from datetime import datetime
from pathlib import Path

try:
    import pytz
except ImportError:
    pytz = None

try:
    from colorama import Fore, Back, Style, init
    # Inicializar colorama para compatibilidad con Windows
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def configurar_logger():
    """Configura el sistema de logging para guardar ejecuciones.

    Crea el directorio logs/ si no existe y configura el logger
    para escribir en logs/greetings.log.

    Returns:
        logging.Logger: Logger configurado.
    """
    # Crear directorio logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configurar logger
    logger = logging.getLogger("hello")
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si ya están configurados
    if not logger.handlers:
        # Handler para archivo
        file_handler = logging.FileHandler(log_dir / "greetings.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


def mostrar_ascii_art():
    """Muestra un ASCII art de bienvenida con colores.

    Returns:
        str: ASCII art de bienvenida.
    """
    # ASCII art de bienvenida
    art = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ██╗███████╗███╗   ██╗██╗   ██╗███████╗███╗   ██║
║   ██╔══██╗██║██╔════╝████╗  ██║██║   ██║██╔════╝████╗  ██║
║   ██████╔╝██║█████╗  ██╔██╗ ██║██║   ██║█████╗  ██╔██╗ ██║
║   ██╔══██╗██║██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║
║   ██████╔╝██║███████╗██║ ╚████║ ╚████╔╝ ███████╗██║ ╚████║
║   ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """

    if COLORAMA_AVAILABLE:
        # Retornar con colores si colorama está disponible
        return f"{Fore.CYAN}{Style.BRIGHT}{art}{Style.RESET_ALL}"
    else:
        # Retornar sin colores
        return art


def colorear_texto(texto, color="blanco", negrita=False):
    """Aplica color a un texto usando colorama.

    Args:
        texto (str): Texto a colorear.
        color (str): Color a aplicar (cyan, verde, amarillo, rojo, blanco, magenta).
        negrita (bool): Si aplicar estilo negrita.

    Returns:
        str: Texto con colores aplicados o texto original si colorama no está disponible.

    Examples:
        >>> resultado = colorear_texto("Hola", "cyan")
        >>> isinstance(resultado, str)
        True
    """
    if not COLORAMA_AVAILABLE:
        return texto

    # Mapeo de colores
    colores = {
        "cyan": Fore.CYAN,
        "verde": Fore.GREEN,
        "amarillo": Fore.YELLOW,
        "rojo": Fore.RED,
        "blanco": Fore.WHITE,
        "magenta": Fore.MAGENTA,
    }

    color_code = colores.get(color.lower(), Fore.WHITE)
    estilo = Style.BRIGHT if negrita else ""

    return f"{estilo}{color_code}{texto}{Style.RESET_ALL}"


def registrar_ejecucion(logger, nombre, fecha_hora):
    """Registra una ejecución del programa en el log.

    Args:
        logger (logging.Logger): Logger configurado.
        nombre (str): Nombre del usuario (puede ser None o vacío).
        fecha_hora (datetime): Fecha y hora de la ejecución.

    Raises:
        ValueError: Si logger o fecha_hora son None.
    """
    # Validar parámetros obligatorios
    if logger is None:
        raise ValueError("Logger no puede ser None")
    if fecha_hora is None:
        raise ValueError("fecha_hora no puede ser None")

    try:
        # Formatear fecha_hora
        fecha_str = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')

        # Registrar con o sin nombre
        if nombre and isinstance(nombre, str) and nombre.strip():
            logger.info(f"Saludo a: {nombre.strip()} - {fecha_str}")
        else:
            logger.info(f"Saludo sin nombre - {fecha_str}")
    except Exception as e:
        # Si falla el logging, no queremos crashear el programa
        logger.error(f"Error al registrar ejecución: {e}")


def obtener_fecha_hora_santiago():
    """Obtiene la fecha y hora actual de Santiago de Chile.

    Returns:
        datetime: Objeto datetime con la fecha y hora de Santiago.
        Si pytz no está disponible, retorna la hora local del sistema.

    Examples:
        >>> fecha = obtener_fecha_hora_santiago()
        >>> isinstance(fecha, datetime)
        True
    """
    if pytz is not None:
        # Obtener la zona horaria de Santiago
        zona_santiago = pytz.timezone('America/Santiago')
        fecha_hora = datetime.now(zona_santiago)
    else:
        # Si pytz no está disponible, usar hora local
        fecha_hora = datetime.now()

    return fecha_hora


def formatear_fecha_hora(fecha_hora):
    """Formatea la fecha y hora en un formato legible en español.

    Args:
        fecha_hora (datetime): Objeto datetime a formatear.

    Returns:
        str: Fecha y hora formateada en español.

    Examples:
        >>> from datetime import datetime
        >>> fecha = datetime(2024, 3, 15, 14, 30)
        >>> resultado = formatear_fecha_hora(fecha)
        >>> '15/03/2024' in resultado
        True
    """
    # Formatear la fecha y hora en español
    fecha_formateada = fecha_hora.strftime("%d/%m/%Y")
    hora_formateada = fecha_hora.strftime("%H:%M:%S")

    return f"Fecha: {fecha_formateada} - Hora: {hora_formateada}"


def solicitar_nombre():
    """Solicita el nombre del usuario mediante input.

    Returns:
        str: Nombre del usuario ingresado (sin espacios al inicio/final).
             Retorna string vacío si hay EOF o error de entrada.

    Examples:
        >>> # Esta función requiere interacción del usuario
        >>> # En tests se puede simular con mock
        pass
    """
    try:
        prompt = colorear_texto("Por favor, ingresa tu nombre: ", "amarillo", negrita=True)
        nombre = input(prompt)

        # Validar que nombre no sea None
        if nombre is None:
            return ""

        # Limpiar espacios y retornar
        return nombre.strip()
    except EOFError:
        # Manejar EOF (Ctrl+D o cierre de stdin)
        print()  # Nueva línea para mejor formato
        return ""
    except KeyboardInterrupt:
        # Re-lanzar KeyboardInterrupt para que main() lo maneje
        raise
    except Exception as e:
        # Manejar otros errores de input
        print(f"\nError al leer entrada: {e}")
        return ""


def generar_saludo(nombre=None):
    """Genera un saludo personalizado en español.

    Args:
        nombre (str, optional): Nombre del usuario. Si no se proporciona,
            genera un saludo genérico.

    Returns:
        str: Mensaje de saludo personalizado o genérico.

    Examples:
        >>> generar_saludo("Juan")
        '¡Hola, Juan! Bienvenido/a.'
        >>> generar_saludo()
        '¡Hola! Bienvenido/a.'
    """
    # Validar que nombre sea un string no vacío
    if nombre and isinstance(nombre, str) and nombre.strip():
        return f"¡Hola, {nombre.strip()}! Bienvenido/a."
    else:
        return "¡Hola! Bienvenido/a."


def ejecutar_programa():
    """Función principal que ejecuta el programa completo.

    Coordina todas las funciones para:
    1. Mostrar ASCII art de bienvenida
    2. Mostrar saludo inicial
    3. Mostrar fecha y hora de Santiago
    4. Solicitar nombre del usuario
    5. Mostrar saludo personalizado
    6. Registrar la ejecución en el log
    """
    # Configurar logger
    logger = configurar_logger()

    # Mostrar ASCII art de bienvenida
    print(mostrar_ascii_art())
    print()

    # Saludo inicial con color
    saludo_inicial = generar_saludo()
    print(colorear_texto(saludo_inicial, "verde", negrita=True))
    print()

    # Obtener y mostrar fecha y hora de Santiago
    fecha_hora = obtener_fecha_hora_santiago()
    titulo_fecha = colorear_texto(
        "Fecha y hora actual en Santiago de Chile:",
        "cyan",
        negrita=True
    )
    print(titulo_fecha)
    fecha_formateada = formatear_fecha_hora(fecha_hora)
    print(colorear_texto(fecha_formateada, "magenta"))
    print()

    # Solicitar nombre y generar saludo personalizado
    nombre_usuario = solicitar_nombre()

    # Asegurar que nombre_usuario nunca sea None
    if nombre_usuario is None:
        nombre_usuario = ""

    # Validar que el nombre no esté vacío
    if nombre_usuario and nombre_usuario.strip():
        print()
        saludo_personalizado = generar_saludo(nombre_usuario)
        print(colorear_texto(saludo_personalizado, "verde", negrita=True))
    else:
        print()
        mensaje = "No ingresaste un nombre, pero igual es un placer saludarte."
        print(colorear_texto(mensaje, "amarillo"))

    # Registrar ejecución en el log
    try:
        registrar_ejecucion(logger, nombre_usuario, fecha_hora)
    except Exception as e:
        # Si falla el logging, continuar pero mostrar advertencia
        print(colorear_texto(f"\nAdvertencia: No se pudo guardar el log: {e}", "amarillo"))


def main():
    """Punto de entrada principal del programa.

    Maneja excepciones globales y proporciona mensajes de error claros.
    """
    try:
        ejecutar_programa()
    except KeyboardInterrupt:
        # Usuario presionó Ctrl+C
        print("\n\n¡Hasta luego!")
    except EOFError:
        # EOF inesperado (aunque debería manejarse en solicitar_nombre)
        print("\n\nEntrada cerrada inesperadamente. ¡Hasta luego!")
    except ValueError as e:
        # Errores de validación
        print(f"\n{colorear_texto(f'Error de validación: {e}', 'rojo', negrita=True)}")
    except Exception as e:
        # Otros errores inesperados
        print(f"\n{colorear_texto(f'Ocurrió un error inesperado: {e}', 'rojo', negrita=True)}")
        print(colorear_texto("Por favor reporta este error.", "amarillo"))


if __name__ == "__main__":
    main()
