"""
Ejemplos de uso del endpoint request_ants desde un cliente web
"""

import requests
import json

# URL base del servidor (ajustar según tu configuración)
BASE_URL = "http://localhost:8000"


def ejemplo_solicitud_exitosa():
    """Ejemplo de solicitud exitosa de múltiples hormigas"""
    print("\n=== Ejemplo 1: Solicitud exitosa ===")

    # Datos de la solicitud
    payload = {
        "subsystem_name": "Defense",
        "quantity": 5,
        "priority": 1,
        "estimated_duration_seconds": 120
    }

    # Hacer la solicitud POST
    response = requests.post(
        f"{BASE_URL}/ants/request-multiple",
        json=payload
    )

    # Procesar respuesta
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Éxito: {result['message']}")
        print(f"   Hormigas asignadas: {len(result['ants'])}")
        print(f"   - Usadas existentes: {result['ants_used']}")
        print(f"   - Nuevas creadas: {result['ants_created']}")

        # Mostrar IDs de las hormigas asignadas
        for ant in result['ants']:
            print(f"   - Hormiga {ant['id']} asignada a {ant['assigned_to']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())


def ejemplo_solicitud_fallida():
    """Ejemplo de solicitud que falla por recursos insuficientes"""
    print("\n=== Ejemplo 2: Solicitud con recursos insuficientes ===")

    # Solicitar muchas hormigas
    payload = {
        "subsystem_name": "Communication",
        "quantity": 100,  # Cantidad muy alta
        "priority": 2
    }

    response = requests.post(
        f"{BASE_URL}/ants/request-multiple",
        json=payload
    )

    result = response.json()
    if not result['success']:
        print(f"❌ Fallo: {result['message']}")
        print(f"   Disponibles: {result['available']}")
        print(f"   Se pueden crear: {result['can_create']}")
        print(f"   Solicitadas: {result['requested']}")


def ejemplo_con_manejo_inteligente():
    """Ejemplo con manejo inteligente de respuestas"""
    print("\n=== Ejemplo 3: Manejo inteligente ===")

    def solicitar_hormigas_inteligente(subsystem, cantidad_deseada):
        payload = {
            "subsystem_name": subsystem,
            "quantity": cantidad_deseada,
            "priority": 1,
            "estimated_duration_seconds": 60
        }

        response = requests.post(
            f"{BASE_URL}/ants/request-multiple",
            json=payload
        )

        result = response.json()

        if result['success']:
            print(f"✅ Asignadas {len(result['ants'])} hormigas a {subsystem}")
            return result['ants']
        else:
            # Si falla, intentar con las disponibles
            disponibles = result['available'] + result['can_create']

            if disponibles > 0:
                print(f"⚠️ No hay {cantidad_deseada} hormigas, intentando con {disponibles}...")

                # Reintentar con cantidad ajustada
                payload['quantity'] = disponibles
                retry_response = requests.post(
                    f"{BASE_URL}/ants/request-multiple",
                    json=payload
                )

                retry_result = retry_response.json()
                if retry_result['success']:
                    print(f"✅ Asignadas {len(retry_result['ants'])} hormigas a {subsystem}")
                    return retry_result['ants']

            print(f"❌ No hay hormigas disponibles para {subsystem}")
            return []

    # Usar la función
    hormigas = solicitar_hormigas_inteligente("Collection", 10)
    print(f"Total obtenidas: {len(hormigas)}")


def ejemplo_asignacion_multiple_subsistemas():
    """Ejemplo de asignación a múltiples subsistemas"""
    print("\n=== Ejemplo 4: Asignación a múltiples subsistemas ===")

    asignaciones = [
        ("Defense", 3, 1),      # subsistema, cantidad, prioridad
        ("Communication", 2, 2),
        ("Collection", 4, 3)
    ]

    resultados = []

    for subsistema, cantidad, prioridad in asignaciones:
        payload = {
            "subsystem_name": subsistema,
            "quantity": cantidad,
            "priority": prioridad,
            "estimated_duration_seconds": 90
        }

        response = requests.post(
            f"{BASE_URL}/ants/request-multiple",
            json=payload
        )

        result = response.json()
        resultados.append({
            'subsistema': subsistema,
            'solicitadas': cantidad,
            'asignadas': len(result['ants']) if result['success'] else 0,
            'exito': result['success']
        })

    # Mostrar resumen
    print("\n📊 Resumen de asignaciones:")
    for r in resultados:
        estado = "✅" if r['exito'] else "❌"
        print(f"{estado} {r['subsistema']}: {r['asignadas']}/{r['solicitadas']} hormigas")


def ejemplo_con_async():
    """Ejemplo usando requests asíncronas (requiere httpx)"""
    print("\n=== Ejemplo 5: Solicitudes asíncronas ===")

    try:
        import httpx
        import asyncio

        async def solicitar_async():
            async with httpx.AsyncClient() as client:
                # Hacer múltiples solicitudes en paralelo
                tasks = []

                for i in range(3):
                    payload = {
                        "subsystem_name": "Defense",
                        "quantity": 2,
                        "priority": 1
                    }
                    task = client.post(f"{BASE_URL}/ants/request-multiple", json=payload)
                    tasks.append(task)

                # Esperar todas las respuestas
                responses = await asyncio.gather(*tasks)

                for i, response in enumerate(responses):
                    result = response.json()
                    print(f"Solicitud {i+1}: {'✅' if result['success'] else '❌'} - {result['message']}")

        # Ejecutar
        asyncio.run(solicitar_async())

    except ImportError:
        print("httpx no está instalado. Instalar con: pip install httpx")


def verificar_estado_colonia():
    """Verificar el estado de la colonia antes de hacer solicitudes"""
    print("\n=== Estado de la Colonia ===")

    response = requests.get(f"{BASE_URL}/colony/status/comprehensive")

    if response.status_code == 200:
        status = response.json()
        print(f"📊 Estado actual:")
        print(f"   Hormigas vivas: {status['alive_ants']}")
        print(f"   Hormigas libres: {status['free_ants']}")
        print(f"   Hormigas asignadas: {status['assigned_ants']}")
        print(f"   Stock de comida: {status['food_stock']}")
        print(f"   Puede crear más: {status['can_create_more']}")

        # Mostrar distribución por subsistema
        print(f"\n   Distribución por subsistema:")
        for subsystem, count in status['ants_by_subsystem'].items():
            if count > 0:
                print(f"   - {subsystem}: {count} hormigas")


if __name__ == "__main__":
    print("🐜 Ejemplos de uso del endpoint request-multiple")
    print("=" * 50)

    # Verificar estado inicial
    verificar_estado_colonia()

    # Ejecutar ejemplos
    ejemplo_solicitud_exitosa()
    ejemplo_solicitud_fallida()
    ejemplo_con_manejo_inteligente()
    ejemplo_asignacion_multiple_subsistemas()
    ejemplo_con_async()

    # Verificar estado final
    print("\n" + "=" * 50)
    verificar_estado_colonia()