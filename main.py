import asyncio
from workflows.flujo_soporte import ejecutar_flujo_soporte

if __name__ == "__main__":
    print("=" * 55)
    print("  SISTEMA DE SOPORTE — google-adk-agents-poc")
    print("  Patrón: Orquestador + Sub-agentes + Tools")
    print("=" * 55)
    print("Ingrese el ticket del cliente (o 'salir' para terminar).\n")

    while True:
        ticket_usuario = input("📋 Ticket: ").strip()

        if not ticket_usuario:
            print("[AVISO] El ticket no puede estar vacío.\n")
            continue

        if ticket_usuario.lower() == "salir":
            print("\nSistema cerrado. Hasta luego.")
            break

        try:
            resultado = asyncio.run(ejecutar_flujo_soporte(ticket_usuario))
            print("\n" + "=" * 55)
            print("  RESPUESTA FINAL AL CLIENTE")
            print("=" * 55)
            print(resultado)
        except Exception as e:
            print(f"\n[ERROR CRÍTICO]: {e}")

        print()
        continuar = input("¿Procesar otro ticket? (si/no): ").lower().strip()
        if continuar != "si":
            print("\nSistema cerrado. Hasta luego.")
            break
        print()