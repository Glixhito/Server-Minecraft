#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de Servidor Minecraft
============================

Este módulo permite iniciar, detener y monitorear el servidor de Minecraft.
Proporciona funciones para controlar el proceso del servidor, enviar comandos
y monitorear su estado.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
from datetime import datetime

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("minecraft_server_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ServerManager")

# Configuración por defecto
SERVER_JAR = "server.jar"
MIN_RAM = "1G"
MAX_RAM = "4G"
JAVA_PATH = "java"
SERVER_PORT = 25565

class MinecraftServer:
    """Clase para gestionar el servidor de Minecraft."""
    
    def __init__(self, server_jar=SERVER_JAR, min_ram=MIN_RAM, max_ram=MAX_RAM, 
                 java_path=JAVA_PATH, server_port=SERVER_PORT):
        """
        Inicializa el gestor del servidor.
        
        Args:
            server_jar (str): Ruta al archivo JAR del servidor.
            min_ram (str): Memoria RAM mínima (ej. "1G").
            max_ram (str): Memoria RAM máxima (ej. "4G").
            java_path (str): Ruta al ejecutable de Java.
            server_port (int): Puerto del servidor.
        """
        self.server_jar = server_jar
        self.min_ram = min_ram
        self.max_ram = max_ram
        self.java_path = java_path
        self.server_port = server_port
        self.process = None
        self.is_running = False
        self.output_thread = None
        self.console_log = []
        self.max_console_lines = 1000
        
        # Verificar si el archivo JAR existe
        if not os.path.exists(server_jar):
            logger.error(f"No se encuentra el archivo del servidor: {server_jar}")
    
    def start(self):
        """
        Inicia el servidor de Minecraft.
        
        Returns:
            bool: True si el servidor se inició correctamente, False en caso contrario.
        """
        if self.is_running:
            logger.warning("El servidor ya está en ejecución.")
            return True
        
        try:
            # Comando para iniciar el servidor
            command = [
                self.java_path,
                f"-Xms{self.min_ram}",
                f"-Xmx{self.max_ram}",
                "-jar",
                self.server_jar,
                "nogui"
            ]
            
            logger.info(f"Iniciando servidor con comando: {' '.join(command)}")
            
            # Iniciar el proceso
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            
            # Iniciar hilo para capturar la salida
            self.output_thread = threading.Thread(target=self._capture_output)
            self.output_thread.daemon = True
            self.output_thread.start()
            
            logger.info("Servidor iniciado. Esperando a que esté listo...")
            
            # Esperar a que el servidor esté completamente cargado
            max_wait_time = 60  # segundos
            server_ready = False
            
            for _ in range(max_wait_time):
                if not self.is_running:
                    logger.error("El servidor se detuvo durante el inicio.")
                    return False
                
                # Verificar si el servidor está listo (buscando mensajes en la consola)
                for line in self.console_log:
                    if "Done" in line and "For help, type" in line:
                        server_ready = True
                        break
                
                if server_ready:
                    break
                    
                time.sleep(1)
            
            if server_ready:
                logger.info("¡Servidor completamente cargado y listo!")
                return True
            else:
                logger.warning("El servidor se está iniciando, pero está tardando más de lo esperado.")
                return True
                
        except Exception as e:
            logger.error(f"Error al iniciar el servidor: {e}")
            self.is_running = False
            return False
    
    def stop(self, timeout=30):
        """
        Detiene el servidor de Minecraft de forma segura.
        
        Args:
            timeout (int): Tiempo máximo de espera en segundos.
            
        Returns:
            bool: True si el servidor se detuvo correctamente, False en caso contrario.
        """
        if not self.is_running or not self.process:
            logger.warning("El servidor no está en ejecución.")
            return True
        
        try:
            # Enviar comandos para guardar el mundo y detener el servidor
            logger.info("Guardando mundo...")
            self.send_command("save-all")
            time.sleep(2)  # Esperar a que se guarde el mundo
            
            logger.info("Enviando comando de detención...")
            self.send_command("stop")
            
            # Esperar a que el proceso termine
            for _ in range(timeout):
                if self.process.poll() is not None:
                    self.is_running = False
                    logger.info("Servidor detenido correctamente.")
                    return True
                time.sleep(1)
            
            # Si el servidor no se detiene, forzar la terminación
            logger.warning("El servidor no responde. Forzando la terminación...")
            if self.process:
                self.process.terminate()
                time.sleep(2)
                if self.process.poll() is None:
                    self.process.kill()
            
            self.is_running = False
            logger.info("Servidor detenido forzosamente.")
            return True
            
        except Exception as e:
            logger.error(f"Error al detener el servidor: {e}")
            return False
    
    def send_command(self, command):
        """
        Envía un comando al servidor.
        
        Args:
            command (str): Comando a enviar.
            
        Returns:
            bool: True si el comando se envió correctamente, False en caso contrario.
        """
        if not self.is_running or not self.process:
            logger.error("No se puede enviar comando: el servidor no está en ejecución.")
            return False
        
        try:
            # Enviar el comando al proceso
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            logger.info(f"Comando enviado: {command}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar comando: {e}")
            return False
    
    def _capture_output(self):
        """Captura la salida del servidor en un hilo separado."""
        try:
            while self.is_running and self.process and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    # Guardar la línea en el registro de consola
                    self.console_log.append(line.strip())
                    # Limitar el tamaño del registro
                    if len(self.console_log) > self.max_console_lines:
                        self.console_log.pop(0)
                    
                    # También escribir en el log
                    logger.debug(f"SERVER: {line.strip()}")
            
            # Si llegamos aquí, el proceso ha terminado
            self.is_running = False
            logger.info("El servidor se ha detenido.")
            
        except Exception as e:
            logger.error(f"Error al capturar la salida del servidor: {e}")
            self.is_running = False
    
    def get_console_output(self, lines=50):
        """
        Obtiene las últimas líneas de la salida de la consola.
        
        Args:
            lines (int): Número de líneas a obtener.
            
        Returns:
            list: Lista con las últimas líneas del registro de consola.
        """
        return self.console_log[-lines:] if self.console_log else []
    
    def is_server_running(self):
        """
        Verifica si el servidor está en ejecución.
        
        Returns:
            bool: True si el servidor está en ejecución, False en caso contrario.
        """
        # Verificar el estado interno
        if not self.is_running or not self.process:
            return False
        
        # Verificar si el proceso sigue vivo
        if self.process.poll() is not None:
            self.is_running = False
            return False
        
        return True
    
    def restart(self, timeout=30):
        """
        Reinicia el servidor.
        
        Args:
            timeout (int): Tiempo máximo de espera para detener el servidor.
            
        Returns:
            bool: True si el servidor se reinició correctamente, False en caso contrario.
        """
        logger.info("Reiniciando servidor...")
        
        # Detener el servidor
        if not self.stop(timeout):
            logger.error("Error al detener el servidor durante el reinicio.")
            return False
        
        # Esperar un momento antes de iniciar de nuevo
        time.sleep(5)
        
        # Iniciar el servidor
        return self.start()
    
    def backup_world(self, backup_dir="backups"):
        """
        Realiza una copia de seguridad del mundo.
        
        Args:
            backup_dir (str): Directorio donde guardar la copia.
            
        Returns:
            str: Ruta al archivo de respaldo, o None si hubo un error.
        """
        import shutil
        import zipfile
        
        if not os.path.exists("world"):
            logger.error("No se encuentra el directorio del mundo para hacer respaldo.")
            return None
        
        # Crear directorio de respaldos si no existe
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            # Fecha y hora para el nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"world_backup_{timestamp}.zip")
            
            # Si el servidor está en ejecución, guardar el mundo primero
            if self.is_running:
                logger.info("Guardando el mundo antes de hacer respaldo...")
                self.send_command("save-all")
                time.sleep(5)  # Esperar a que se guarde el mundo
            
            # Crear archivo ZIP con el mundo
            logger.info(f"Creando respaldo del mundo en: {backup_file}")
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk("world"):
                    for file in files:
                        filepath = os.path.join(root, file)
                        zipf.write(filepath, os.path.relpath(filepath, start="."))
            
            logger.info(f"Respaldo completado: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Error al hacer respaldo del mundo: {e}")
            return None

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Gestor de Servidor Minecraft ===")
    print("Este script permite controlar el servidor de Minecraft.")
    print()
    
    # Crear una instancia del servidor
    server = MinecraftServer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            print("Iniciando servidor...")
            server.start()
        elif command == "stop":
            print("Deteniendo servidor...")
            server.stop()
        elif command == "restart":
            print("Reiniciando servidor...")
            server.restart()
        elif command == "backup":
            print("Haciendo respaldo del mundo...")
            server.backup_world()
        elif command == "status":
            if server.is_server_running():
                print("El servidor está en ejecución.")
            else:
                print("El servidor está detenido.")
        else:
            print(f"Comando desconocido: {command}")
            print("Comandos disponibles: start, stop, restart, backup, status")
    else:
        print("Uso: python server_manager.py [comando]")
        print("Comandos disponibles: start, stop, restart, backup, status")

