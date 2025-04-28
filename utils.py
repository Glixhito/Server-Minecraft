#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades para Servidor Minecraft
=================================

Este módulo proporciona funciones de utilidad comunes para la gestión del servidor Minecraft,
incluyendo verificación de conexión, manejo de logs, respaldos y utilidades de red.
"""

import os
import socket
import logging
import shutil
import zipfile
import time
import subprocess
import platform
import re
from datetime import datetime

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("minecraft_utils.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MinecraftUtils")

# Funciones de verificación de conexión

def check_port_open(host="127.0.0.1", port=25565, timeout=3):
    """
    Verifica si un puerto está abierto en un host.
    
    Args:
        host (str): Dirección IP o hostname.
        port (int): Número de puerto a verificar.
        timeout (int): Tiempo de espera en segundos.
        
    Returns:
        bool: True si el puerto está abierto, False si está cerrado.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Error al verificar puerto {port} en {host}: {e}")
        return False

def check_server_online(host="127.0.0.1", port=25565, timeout=3):
    """
    Verifica si el servidor de Minecraft está en línea.
    
    Args:
        host (str): Dirección IP o hostname.
        port (int): Puerto del servidor.
        timeout (int): Tiempo de espera en segundos.
        
    Returns:
        bool: True si el servidor está en línea, False en caso contrario.
    """
    return check_port_open(host, port, timeout)

def get_external_ip():
    """
    Obtiene la dirección IP pública (externa) del servidor.
    
    Returns:
        str: Dirección IP pública, o None si hay error.
    """
    try:
        # Utilizamos un servicio externo para obtener la IP pública
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except Exception as e:
        logger.error(f"Error al obtener dirección IP externa: {e}")
        return None

def get_local_ip():
    """
    Obtiene la dirección IP local (interna) del servidor.
    
    Returns:
        str: Dirección IP local, o None si hay error.
    """
    try:
        # Creamos un socket y conectamos a un servidor externo
        # para determinar qué interfaz de red usar
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.error(f"Error al obtener dirección IP local: {e}")
        # Alternativa usando el hostname
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return None

# Funciones de manejo de logs

def parse_server_log(log_path="server.log", max_lines=100):
    """
    Analiza el archivo de log del servidor.
    
    Args:
        log_path (str): Ruta al archivo de log.
        max_lines (int): Número máximo de líneas a analizar.
        
    Returns:
        list: Lista de entradas de log.
    """
    entries = []
    
    try:
        if not os.path.exists(log_path):
            return entries
        
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Leer las últimas max_lines líneas
            lines = f.readlines()
            for line in lines[-max_lines:]:
                line = line.strip()
                if line:
                    entries.append(line)
        
        return entries
    except Exception as e:
        logger.error(f"Error al leer archivo de log {log_path}: {e}")
        return []

def extract_player_activity(log_entries):
    """
    Extrae la actividad de los jugadores desde las entradas de log.
    
    Args:
        log_entries (list): Lista de entradas de log.
        
    Returns:
        dict: Diccionario con la actividad de los jugadores.
    """
    players = {}
    
    # Patrones para identificar actividad de jugadores
    join_pattern = re.compile(r"(\w+)\[.+\] logged in")
    left_pattern = re.compile(r"(\w+) left the game")
    
    try:
        for entry in log_entries:
            # Buscar cuando un jugador se une
            join_match = join_pattern.search(entry)
            if join_match:
                player_name = join_match.group(1)
                if player_name not in players:
                    players[player_name] = []
                players[player_name].append({"action": "join", "timestamp": entry.split("[", 1)[0].strip()})
                continue
            
            # Buscar cuando un jugador se va
            left_match = left_pattern.search(entry)
            if left_match:
                player_name = left_match.group(1)
                if player_name not in players:
                    players[player_name] = []
                players[player_name].append({"action": "left", "timestamp": entry.split("[", 1)[0].strip()})
        
        return players
    except Exception as e:
        logger.error(f"Error al extraer actividad de jugadores: {e}")
        return {}

# Funciones de respaldo

def create_backup(source_dir, backup_name=None, backup_dir="backups"):
    """
    Crea un respaldo de un directorio.
    
    Args:
        source_dir (str): Directorio a respaldar.
        backup_name (str, optional): Nombre del archivo de respaldo.
        backup_dir (str): Directorio donde guardar el respaldo.
        
    Returns:
        str: Ruta al archivo de respaldo, o None si hay error.
    """
    try:
        # Crear directorio de respaldos si no existe
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generar nombre de archivo si no se proporciona
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_base = os.path.basename(os.path.normpath(source_dir))
            backup_name = f"{source_base}_backup_{timestamp}.zip"
        
        # Ruta completa al archivo de respaldo
        backup_path = os.path.join(backup_dir, backup_name)
        
        logger.info(f"Creando respaldo de {source_dir} en {backup_path}...")
        
        # Crear el archivo ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Respaldo creado correctamente: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Error al crear respaldo de {source_dir}: {e}")
        return None

def list_backups(backup_dir="backups", pattern=None):
    """
    Lista los respaldos disponibles.
    
    Args:
        backup_dir (str): Directorio donde se encuentran los respaldos.
        pattern (str, optional): Patrón para filtrar los respaldos.
        
    Returns:
        list: Lista de respaldos disponibles.
    """
    backups = []
    
    try:
        if not os.path.exists(backup_dir):
            return backups
        
        for file in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file)
            
            # Verificar si es un archivo y si coincide con el patrón
            if os.path.isfile(file_path) and file.endswith(".zip"):
                if pattern is None or pattern in file:
                    # Obtener información del archivo
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Tamaño en MB
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        "name": file,
                        "path": file_path,
                        "size_mb": round(file_size, 2),
                        "date": file_date
                    })
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x["date"], reverse=True)
        return backups
        
    except Exception as e:
        logger.error(f"Error al listar respaldos en {backup_dir}: {e}")
        return []

def restore_backup(backup_path, restore_dir):
    """
    Restaura un respaldo.
    
    Args:
        backup_path (str): Ruta al archivo de respaldo.
        restore_dir (str): Directorio donde restaurar el respaldo.
        
    Returns:
        bool: True si se restauró correctamente, False en caso contrario.
    """
    try:
        if not os.path.exists(backup_path):
            logger.error(f"No se encontró el archivo de respaldo: {backup_path}")
            return False
        
        # Crear directorio de restauración si no existe
        os.makedirs(restore_dir, exist_ok=True)
        
        logger.info(f"Restaurando respaldo {backup_path} en {restore_dir}...")
        
        # Extraer el archivo ZIP
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_dir)
        
        logger.info(f"Respaldo restaurado correctamente en {restore_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error al restaurar respaldo {backup_path}: {e}")
        return False

# Funciones de sistema y redes

def get_system_info():
    """
    Obtiene información del sistema.
    
    Returns:
        dict: Información del sistema.
    """
    try:
        info = {
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname(),
            "local_ip": get_local_ip(),
            "external_ip": get_external_ip()
        }
        
        # Añadir información de memoria en sistemas compatibles
        if hasattr(os, "sysconf") and os.sysconf_names.get("SC_PHYS_PAGES", None) is not None:
            mem_bytes = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
            info["memory_total_gb"] = round(mem_bytes / (1024**3), 2)
        
        return info
        
    except Exception as e:
        logger.error(f"Error al obtener información del sistema: {e}")
        return {"error": str(e)}

def check_java_version():
    """
    Verifica la versión de Java instalada.
    
    Returns:
        dict: Información sobre la versión de Java, o None si hay error.
    """
    try:
        # Ejecutar comando java -version
        java_process = subprocess.Popen(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        _, stderr = java_process.communicate()
        
        # Buscar la versión en la salida
        version_line = stderr.splitlines()[0] if stderr else ""
        
        # Extraer versión usando expresiones regulares
        java_version = re.search(r'version "([^"]+)"', version_line)
        java_version = java_version.group(1) if java_version else "Desconocida"
        
        # Extraer implementación (OpenJDK, Oracle, etc.)
        java_impl = "Desconocida"
        if "OpenJDK" in version_line:
            java_impl = "OpenJDK"
        elif "Java(TM)" in version_line:
            java_impl = "Oracle Java"
        
        return {
            "version": java_version,
            "implementation": java_impl,
            "version_line": version_line.strip()
        }
        
    except Exception as e:
        logger.error(f"Error al verificar versión de Java: {e}")
        return None

def check_port_forwarding(port=25565):
    """
    Verifica si el puerto está correctamente redirigido (port forwarding).
    
    Args:
        port (int): Puerto a verificar.
        
    Returns:
        bool: True si el puerto está correctamente redirigido, False en caso contrario.
    """
    try:
        # Obtener IP pública
        external_ip = get_external_ip()
        if not external_ip:
            return False
        
        # Verificar si el puerto está abierto desde el exterior
        return check_port_open(external_ip, port, 5)
        
    except Exception as e:
        logger.error(f"Error al verificar port forwarding: {e}")
        return False

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Utilidades para Servidor Minecraft ===")
    
    # Mostrar información del sistema
    system_info = get_system_info()
    print("\nInformación del sistema:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # Verificar versión de Java
    java_info = check_java_version()
    if java_info:
        print("\nInformación de Java:")
        for key, value in java_info.items():
            print(f"{key}: {value}")
    
    # Verificar si el servidor está en línea
    server_online = check_server_online()
    print(f"\nServidor Minecraft en línea: {'Sí' if server_online else 'No'}")
    
    # Verificar port forwarding
    port_forwarded = check_port_forwarding()
    print(f"Puerto correctamente redirigido: {'Sí' if port_forwarded else 'No'}")
    
    print("\nEjemplo de uso completado.")

