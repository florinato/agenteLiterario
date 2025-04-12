import os

HISTORIAS_DIR = r"C:\\proyecto\\historias"

# Lista de comandos de prueba (simulando entradas del agente)
comandos_de_prueba = [
    "#accion: leer ReGenesis\\intro.txt",
    "#accion: listar ReGenesis",
    "#accion: arbol ReGenesis",
    "#accion: leer ..\\fuera.txt",
    "#accion: leer",
    "#accion: leer ReGenesis\\capitulo2\\escena1.txt",
    "#accion: buscar ReGenesis\\capitulo2\\escena1.txt \"Ana entra al hospital\"",
    "#accion: buscar algo.txt \"peligro\"",
    "#accion: crear ReGenesis\\nuevo_archivo.txt" # Nuevo comando de prueba
]
def generar_comando_ps(accion):
    try:
        base = accion[len("#accion: "):].strip()
        metodo, ruta, *resto = base.split(" ", 2)
        ruta_abs = os.path.join(HISTORIAS_DIR, ruta)

        if metodo == "leer":
            return f'type "{ruta_abs}"'
        elif metodo == "listar":
            return f'Get-ChildItem "{ruta_abs}"'
        elif metodo == "arbol":
            return f'tree "{ruta_abs}"'
        elif metodo == "buscar":
            if not resto:
                return f"❌ Falta el texto a buscar"
            texto = resto[0].strip('"')
            return f'Select-String -Path "{ruta_abs}" -Pattern "{texto}"'
        else:
            return f"❌ Método no reconocido: {metodo}"
    except Exception as e:
        return f"❌ Error procesando: {accion}"

# Mostrar comando PowerShell generado
for comando in comandos_de_prueba:
    comando_ps = generar_comando_ps(comando)
    print(f">> {comando}\n{comando_ps}\n")
