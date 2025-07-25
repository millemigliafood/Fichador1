from datetime import datetime
import json, os
import time
import shutil

RUTA = "datos/fichajes.json"
BACKUP_DIR = "datos/backups"

def crear_backup_fichajes():
    """Crear una copia de seguridad validada del archivo fichajes.json"""
    if not os.path.exists(RUTA):
        print(f"ADVERTENCIA: El archivo {RUTA} no existe para hacer backup")
        return False
    
    # Asegurar que existe el directorio de backups
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Primero validar que el archivo contiene JSON válido
    try:
        with open(RUTA, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Crear backup con marca de tiempo
        marca_tiempo = time.strftime("%Y%m%d%H%M%S")
        nombre_backup = f"fichajes_backup_{marca_tiempo}.json"
        ruta_backup = os.path.join(BACKUP_DIR, nombre_backup)
        
        # Usar shutil para copiar el archivo (preserva atributos del archivo)
        shutil.copy2(RUTA, ruta_backup)
        
        print(f"Copia de seguridad creada: {ruta_backup}")
        return True
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido en {RUTA}: {e}")
        
        # Buscar último backup válido
        try:
            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("fichajes_backup_")])
            if backups:
                ultimo_backup = os.path.join(BACKUP_DIR, backups[-1])
                print(f"Restaurando desde backup: {ultimo_backup}")
                shutil.copy2(ultimo_backup, RUTA)
                print(f"Restauración completada desde: {ultimo_backup}")
                return True
        except Exception as ex:
            print(f"Error al restaurar backup: {ex}")
        
        return False

def leer_fichajes():
    if os.path.exists(RUTA):
        try:
            with open(RUTA, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR al leer fichajes: {e}")
            # Intentar restaurar desde backup
            if crear_backup_fichajes():  # Esta función ya restaura si es necesario
                # Intentar leer de nuevo
                try:
                    with open(RUTA, "r", encoding="utf-8") as f:
                        return json.load(f)
                except:
                    pass
            return []
    return []

def guardar_fichajes(data):
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    
    # Crear backup antes de modificar
    crear_backup_fichajes()
    
    try:
        # Validar que data sea serializable a JSON
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Escribir al archivo
        with open(RUTA, "w", encoding="utf-8") as f:
            f.write(json_data)
        
        return True
    except Exception as e:
        print(f"ERROR al guardar fichajes: {e}")
        return False

def registrar_fichaje_manual(user_id, nombre, tipo="entrada"):
    datos = leer_fichajes()
    ahora = datetime.now()
    if tipo == "entrada":
        datos.append({
            "id": str(user_id),
            "nombre": nombre,
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora_entrada": ahora.strftime("%H:%M:%S"),
            "hora_salida": None,
            "ubicacion": None
        })
    elif tipo == "salida":
        for f in reversed(datos):
            if f["id"] == str(user_id) and f["hora_salida"] is None:
                f["hora_salida"] = ahora.strftime("%H:%M:%S")
                break
    return guardar_fichajes(datos)

# Crear backup inicial al importar el módulo
if os.path.exists(RUTA):
    crear_backup_fichajes()
