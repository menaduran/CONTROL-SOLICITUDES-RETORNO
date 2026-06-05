import Motor

def mostrar_menu():
    print("\n========================================")
    print("  SISTEMA DE CONTROL DE PRODUCCIÓN CNC")
    print("========================================")
    print("1. Ver resumen actual de producción")
    print("2. Ingresar nueva solicitud al torno")
    print("3. Salir del sistema")
    print("========================================")

def iniciar_sistema():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una acción (1-3): ")

        if opcion == '1':
            Motor.resumen_produccion()
            
        elif opcion == '2':
            print("\n--- NUEVA ORDEN DE TRABAJO ---")
            solicitante = input("Solicitante (ej. Las Americas, CEDI): ")
            prioridad = input("Prioridad (ALTA, MEDIA, BAJA): ")
            pieza = input("Nombre de la pieza (ej. EJE DE PELDAÑO): ")
            material = input("Material (ej. Acero Plata, Bronce - viruta de mecanizado): ")
            cantidad = input("Cantidad a fabricar: ")
            
            # Enviamos los datos al motor para que los guarde
            Motor.agregar_solicitud(solicitante, prioridad, pieza, material, cantidad)
            
        elif opcion == '3':
            print("Cerrando el sistema... ¡Buen turno!")
            break
            
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    iniciar_sistema()