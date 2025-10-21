"""Script de saludo interactivo con fecha y hora de Santiago de Chile.

Este módulo proporciona funciones para saludar al usuario en español,
mostrar la fecha y hora actual de Santiago de Chile, y personalizar
el saludo con el nombre del usuario.
"""

from datetime import datetime
try:
    import pytz
except ImportError:
    pytz = None


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

    Examples:
        >>> # Esta función requiere interacción del usuario
        >>> # En tests se puede simular con mock
        pass
    """
    nombre = input("Por favor, ingresa tu nombre: ").strip()
    return nombre


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
    if nombre:
        return f"¡Hola, {nombre}! Bienvenido/a."
    else:
        return "¡Hola! Bienvenido/a."


def ejecutar_programa():
    """Función principal que ejecuta el programa completo.

    Coordina todas las funciones para:
    1. Mostrar saludo inicial
    2. Mostrar fecha y hora de Santiago
    3. Solicitar nombre del usuario
    4. Mostrar saludo personalizado
    """
    # Saludo inicial
    print(generar_saludo())
    print()

    # Obtener y mostrar fecha y hora de Santiago
    fecha_hora = obtener_fecha_hora_santiago()
    print("Fecha y hora actual en Santiago de Chile:")
    print(formatear_fecha_hora(fecha_hora))
    print()

    # Solicitar nombre y generar saludo personalizado
    nombre_usuario = solicitar_nombre()

    # Validar que el nombre no esté vacío
    if nombre_usuario:
        print()
        print(generar_saludo(nombre_usuario))
    else:
        print()
        print("No ingresaste un nombre, pero igual es un placer saludarte.")


def main():
    """Punto de entrada principal del programa."""
    try:
        ejecutar_programa()
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego!")
    except Exception as e:
        print(f"\nOcurrió un error: {e}")


if __name__ == "__main__":
    main()
