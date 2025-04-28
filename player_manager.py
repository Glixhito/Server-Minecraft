#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de Jugadores para Servidor Minecraft
===========================================

Este módulo permite administrar los jugadores del servidor de Minecraft.
Proporciona funciones para gestionar la lista blanca (whitelist), jugadores baneados
y operadores (administradores) del servidor.
"""

import os
import json
import logging
from datetime import datetime

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("minecraft_player_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PlayerManager")

# Rutas de los archivos
WHITELIST_FILE = "whitelist.json"
BANNED_PLAYERS_FILE = "banned-players.json"
BANNED_IPS_FILE = "banned-ips.json"
OPS_FILE = "ops.json"

class PlayerManager:
    """Clase para gestionar jugadores en el servidor de Minecraft."""
    
    def __init__(self, server_dir="."):
        """
        Inicializa el gestor de jugadores.
        
        Args:
            server_dir (str): Directorio donde se encuentran los archivos del servidor.
        """
        self.server_dir = server_dir
        self.whitelist_path = os.path.join(server_dir, WHITELIST_FILE)
        self.banned_players_path = os.path.join(server_dir, BANNED_PLAYERS_FILE)
        self.banned_ips_path = os.path.join(server_dir, BANNED_IPS_FILE)
        self.ops_path = os.path.join(server_dir, OPS_FILE)
    
    def _load_json_file(self, file_path):
        """
        Carga un archivo JSON.
        
        Args:
            file_path (str): Ruta al archivo JSON.
            
        Returns:
            list/dict: Contenido del archivo JSON, o una lista vacía si hay error.
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error al cargar archivo {file_path}: {e}")
            return []
    
    def _save_json_file(self, file_path, data):
        """
        Guarda datos en un archivo JSON.
        
        Args:
            file_path (str): Ruta al archivo JSON.
            data (list/dict): Datos a guardar.
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error al guardar archivo {file_path}: {e}")
            return False
    
    # Funciones para gestionar la whitelist
    
    def get_whitelist(self):
        """
        Obtiene la lista de jugadores en la whitelist.
        
        Returns:
            list: Lista de jugadores en la whitelist.
        """
        return self._load_json_file(self.whitelist_path)
    
    def add_to_whitelist(self, player_name, uuid=None):
        """
        Añade un jugador a la whitelist.
        
        Args:
            player_name (str): Nombre del jugador.
            uuid (str, optional): UUID del jugador. Si no se proporciona, se deja vacío.
            
        Returns:
            bool: True si se añadió correctamente, False en caso contrario.
        """
        whitelist = self.get_whitelist()
        
        # Verificar si el jugador ya está en la whitelist
        for player in whitelist:
            if player.get('name').lower() == player_name.lower():
                logger.warning(f"El jugador {player_name} ya está en la whitelist.")
                return False
        
        # Añadir el jugador a la whitelist
        whitelist.append({
            'name': player_name,
            'uuid': uuid or ""
        })
        
        # Guardar la whitelist
        result = self._save_json_file(self.whitelist_path, whitelist)
        if result:
            logger.info(f"Jugador {player_name} añadido a la whitelist.")
        return result
    
    def remove_from_whitelist(self, player_name):
        """
        Elimina un jugador de la whitelist.
        
        Args:
            player_name (str): Nombre del jugador a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        whitelist = self.get_whitelist()
        
        # Buscar y eliminar el jugador de la whitelist
        for i, player in enumerate(whitelist):
            if player.get('name').lower() == player_name.lower():
                del whitelist[i]
                
                # Guardar la whitelist
                result = self._save_json_file(self.whitelist_path, whitelist)
                if result:
                    logger.info(f"Jugador {player_name} eliminado de la whitelist.")
                return result
        
        logger.warning(f"El jugador {player_name} no está en la whitelist.")
        return False
    
    # Funciones para gestionar jugadores baneados
    
    def get_banned_players(self):
        """
        Obtiene la lista de jugadores baneados.
        
        Returns:
            list: Lista de jugadores baneados.
        """
        return self._load_json_file(self.banned_players_path)
    
    def ban_player(self, player_name, reason="Banned by an operator", expires=None):
        """
        Banea a un jugador.
        
        Args:
            player_name (str): Nombre del jugador a banear.
            reason (str): Razón del baneo.
            expires (str, optional): Fecha de expiración del baneo en formato ISO.
            
        Returns:
            bool: True si se baneó correctamente, False en caso contrario.
        """
        banned_players = self.get_banned_players()
        
        # Verificar si el jugador ya está baneado
        for player in banned_players:
            if player.get('name').lower() == player_name.lower():
                logger.warning(f"El jugador {player_name} ya está baneado.")
                return False
        
        # Crear entrada de baneo
        ban_entry = {
            'name': player_name,
            'created': datetime.now().isoformat(),
            'source': "Server",
            'expires': expires or "forever",
            'reason': reason
        }
        
        # Añadir el jugador a la lista de baneados
        banned_players.append(ban_entry)
        
        # Guardar la lista de baneados
        result = self._save_json_file(self.banned_players_path, banned_players)
        if result:
            logger.info(f"Jugador {player_name} baneado. Razón: {reason}")
        return result
    
    def unban_player(self, player_name):
        """
        Quita el baneo a un jugador.
        
        Args:
            player_name (str): Nombre del jugador a desbanear.
            
        Returns:
            bool: True si se desbaneó correctamente, False en caso contrario.
        """
        banned_players = self.get_banned_players()
        
        # Buscar y eliminar el jugador de la lista de baneados
        for i, player in enumerate(banned_players):
            if player.get('name').lower() == player_name.lower():
                del banned_players[i]
                
                # Guardar la lista de baneados
                result = self._save_json_file(self.banned_players_path, banned_players)
                if result:
                    logger.info(f"Jugador {player_name} desbaneado.")
                return result
        
        logger.warning(f"El jugador {player_name} no está baneado.")
        return False
    
    # Funciones para gestionar IPs baneadas
    
    def get_banned_ips(self):
        """
        Obtiene la lista de IPs baneadas.
        
        Returns:
            list: Lista de IPs baneadas.
        """
        return self._load_json_file(self.banned_ips_path)
    
    def ban_ip(self, ip, reason="Banned by an operator", expires=None):
        """
        Banea una dirección IP.
        
        Args:
            ip (str): Dirección IP a banear.
            reason (str): Razón del baneo.
            expires (str, optional): Fecha de expiración del baneo en formato ISO.
            
        Returns:
            bool: True si se baneó correctamente, False en caso contrario.
        """
        banned_ips = self.get_banned_ips()
        
        # Verificar si la IP ya está baneada
        for banned_ip in banned_ips:
            if banned_ip.get('ip') == ip:
                logger.warning(f"La IP {ip} ya está baneada.")
                return False
        
        # Crear entrada de baneo
        ban_entry = {
            'ip': ip,
            'created': datetime.now().isoformat(),
            'source': "Server",
            'expires': expires or "forever",
            'reason': reason
        }
        
        # Añadir la IP a la lista de baneadas
        banned_ips.append(ban_entry)
        
        # Guardar la lista de IPs baneadas
        result = self._save_json_file(self.banned_ips_path, banned_ips)
        if result:
            logger.info(f"IP {ip} baneada. Razón: {reason}")
        return result
    
    def unban_ip(self, ip):
        """
        Quita el baneo a una dirección IP.
        
        Args:
            ip (str): Dirección IP a desbanear.
            
        Returns:
            bool: True si se desbaneó correctamente, False en caso contrario.
        """
        banned_ips = self.get_banned_ips()
        
        # Buscar y eliminar la IP de la lista de baneadas
        for i, banned_ip in enumerate(banned_ips):
            if banned_ip.get('ip') == ip:
                del banned_ips[i]
                
                # Guardar la lista de IPs baneadas
                result = self._save_json_file(self.banned_ips_path, banned_ips)
                if result:
                    logger.info(f"IP {ip} desbaneada.")
                return result
        
        logger.warning(f"La IP {ip} no está baneada.")
        return False
    
    # Funciones para gestionar operadores (ops)
    
    def get_ops(self):
        """
        Obtiene la lista de operadores (administradores) del servidor.
        
        Returns:
            list: Lista de operadores.
        """
        return self._load_json_file(self.ops_path)
    
    def add_op(self, player_name, level=4, bypassesPlayerLimit=False):
        """
        Añade un jugador como operador (administrador) del servidor.
        
        Args:
            player_name (str): Nombre del jugador.
            level (int): Nivel de permisos (1-4).
            bypassesPlayerLimit (bool): Si puede entrar cuando el servidor está lleno.
            
        Returns:
            bool: True si se añadió correctamente, False en caso contrario.
        """
        ops = self.get_ops()
        
        # Verificar si el jugador ya es operador
        for op in ops:
            if op.get('name').lower() == player_name.lower():
                logger.warning(f"El jugador {player_name} ya es operador.")
                return False
        
        # Añadir el jugador como operador
        ops.append({
            'name': player_name,
            'level': level,
            'bypassesPlayerLimit': bypassesPlayerLimit
        })
        
        # Guardar la lista de operadores
        result = self._save_json_file(self.ops_path, ops)
        if result:
            logger.info(f"Jugador {player_name} añadido como operador (nivel {level}).")
        return result
    
    def remove_op(self, player_name):
        """
        Elimina a un jugador como operador (administrador) del servidor.
        
        Args:
            player_name (str): Nombre del jugador a eliminar como operador.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        ops = self.get_ops()
        
        # Buscar y eliminar el jugador de la lista de operadores
        for i, op in enumerate(ops):
            if op.get('name').lower() == player_name.lower():
                del ops[i]
                
                # Guardar la lista de operadores
                result = self._save_json_file(self.ops_path, ops)
                if result:
                    logger.info(f"Jugador {player_name} eliminado como operador.")
                return result
        
        logger.warning(f"El jugador {player_name} no es operador.")
        return False

# Ejemplo de uso
if __name__ == "__main__":
    import argparse
    
    # Crear el parser de argumentos
    parser = argparse.ArgumentParser(description="Gestor de jugadores para servidor Minecraft")
    parser.add_argument("accion", choices=["whitelist", "ban", "unban", "op", "deop", "listar"], 
                        help="Acción a realizar")
    parser.add_argument("tipo", nargs="?", choices=["player", "ip"], 
                        help="Tipo de elemento (jugador o IP)")
    parser.add_argument("nombre", nargs="?", help="Nombre del jugador o dirección IP")
    parser.add_argument("--razon", help="Razón del baneo")
    parser.add_argument("--nivel", type=int, choices=[1, 2, 3, 4], default=4, 
                        help="Nivel de permisos para operadores (1-4)")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Crear instancia del gestor de jugadores
    player_manager = PlayerManager()
    
    # Ejecutar la acción correspondiente
    if args.accion == "listar":
        if not args.tipo or args.tipo == "player":
            print("=== Jugadores en whitelist ===")
            whitelist = player_manager.get_whitelist()
            for player in whitelist:
                print(f"- {player.get('name')}")
            
            print("\n=== Jugadores baneados ===")

