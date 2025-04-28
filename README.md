# Herramientas de Gestión para Servidor Minecraft

Un conjunto completo de herramientas en Python para administrar y gestionar servidores de Minecraft, especialmente diseñado para servidores en versión 1.12.2 y superiores.

## Descripción del Proyecto

Este proyecto proporciona un conjunto de herramientas para administrar todos los aspectos de un servidor de Minecraft:

- **Gestión del Servidor**: Iniciar, detener, reiniciar y monitorear el servidor.
- **Gestión de Jugadores**: Administrar whitelist, bans, ops, y más.
- **Gestión de Configuración**: Editar fácilmente server.properties y otras configuraciones.
- **Utilidades**: Respaldos, análisis de logs, verificación de conexión, entre otros.

Todo está desarrollado en Python, es fácil de usar, y cuenta con documentación completa en español.

## Requisitos del Sistema

### Requisitos Mínimos

- **Python**: 3.7 o superior
- **Java**: Java 8 o superior (para el servidor Minecraft)
- **Sistema Operativo**: Windows, Linux o macOS
- **Conexión a Internet**: Para características como verificación de IP externa

### Dependencias de Python

- `requests`: Para comunicación con servicios web
- Bibliotecas estándar: `os`, `socket`, `logging`, `shutil`, `zipfile`, `subprocess`, etc.

## Instalación

1. **Asegúrate de tener Python instalado**:
   ```
   python --version
   ```
   Si no lo tienes, descárgalo de [python.org](https://www.python.org/downloads/)

2. **Instala las dependencias**:
   ```
   pip install requests
   ```

3. **Coloca los archivos en tu servidor**:
   Copia la carpeta `codigo_fuente` a tu servidor de Minecraft.

4. **Verifica la instalación**:
   ```
   cd codigo_fuente
   python admin_panel.py
   ```

## Guía de Uso

### Panel de Administración (admin_panel.py)

Este es el módulo principal que integra todas las funcionalidades y proporciona una interfaz de consola fácil de usar.

```
python admin_panel.py
```

Desde el panel de administración podrás:
- Iniciar/detener el servidor
- Gestionar jugadores (whitelist, bans, ops)
- Configurar el servidor (server.properties)
- Hacer respaldos
- Ver logs y estadísticas
- Y más...

### Gestor del Servidor (server_manager.py)

Este módulo se encarga de controlar el proceso del servidor Minecraft.

```
python server_manager.py [comando]
```

Comandos disponibles:
- `start`: Inicia el servidor
- `stop`: Detiene el servidor
- `restart`: Reinicia el servidor
- `status`: Muestra el estado del servidor
- `backup`: Crea un respaldo del mundo

Ejemplo:
```
python server_manager.py start
```

### Gestor de Jugadores (player_manager.py)

Este módulo maneja todo lo relacionado con los jugadores del servidor.

```
python player_manager.py [acción] [tipo] [nombre] [--opciones]
```

Acciones disponibles:
- `whitelist`: Administra la lista blanca
- `ban`: Banea jugadores o IPs
- `unban`: Quita baneos
- `op`: Añade operadores
- `deop`: Quita operadores
- `listar`: Muestra listas de jugadores

Ejemplos:
```
python player_manager.py whitelist player Notch
python player_manager.py ban player Griefer --razon "Destruir construcciones"
python player_manager.py listar
```

### Gestor de Configuración (config_manager.py)

Este módulo permite editar fácilmente la configuración del servidor.

```
python config_manager.py [acción] [propiedad] [valor]
```

Acciones disponibles:
- `get`: Obtiene el valor de una propiedad
- `set`: Establece el valor de una propiedad
- `listar`: Muestra todas las propiedades

Ejemplos:
```
python config_manager.py get gamemode
python config_manager.py set difficulty hard
python config_manager.py listar
```

### Utilidades (utils.py)

Este módulo proporciona funciones útiles que pueden ser usadas independientemente.

```
python utils.py
```

Este comando ejecutará una demostración de las utilidades disponibles.

## Ejemplos Prácticos

### Ejemplo 1: Configurar y Ejecutar el Servidor

```python
# Importar los módulos necesarios
from server_manager import MinecraftServer
from config_manager import ConfigManager

# Crear instancias
server = MinecraftServer()
config = ConfigManager()

# Configurar el servidor
config.set_gamemode("survival")
config.set_difficulty("normal")
config.set_max_players(20)
config.set_motd("¡Mi Servidor de Minecraft!")
config.save_properties()

# Iniciar el servidor
server.start()
```

### Ejemplo 2: Gestionar Jugadores

```python
# Importar el módulo necesario
from player_manager import PlayerManager

# Crear instancia
player_mgr = PlayerManager()

# Añadir jugadores a la whitelist
player_mgr.add_to_whitelist("Jugador1")
player_mgr.add_to_whitelist("Jugador2")

# Hacer a un jugador operador
player_mgr.add_op("Jugador1", level=4)

# Banear a un jugador
player_mgr.ban_player("Griefer", reason="Griefing")
```

### Ejemplo 3: Hacer un Respaldo del Mundo

```python
# Importar el módulo necesario
from utils import create_backup

# Hacer respaldo del mundo
backup_path = create_backup("world", backup_dir="mis_respaldos")
print(f"Respaldo creado en: {backup_path}")
```

## Solución de Problemas Comunes

### El servidor no inicia

1. **Verifica la versión de Java**:
   ```
   python utils.py
   ```
   Comprueba la sección "Información de Java".

2. **Verifica el archivo server.jar**:
   Asegúrate de que el archivo server.jar existe y no está dañado.

3. **Revisa los logs**:
   ```
   python server_manager.py logs
   ```

### Problemas de conexión

1. **Verifica si el servidor está en ejecución**:
   ```
   python server_manager.py status
   ```

2. **Comprueba la redirección de puertos**:
   ```
   python utils.py
   ```
   Verifica la sección "Puerto correctamente redirigido".

3. **Comprueba el firewall**:
   Asegúrate de que el puerto 25565 (o el que hayas configurado) está abierto en tu firewall.

### Errores de Permisos

En sistemas Linux o macOS, puede ser necesario hacer los scripts ejecutables:
```
chmod +x *.py
```

Si tienes problemas con permisos al acceder a archivos del servidor, asegúrate de que el usuario que ejecuta los scripts tiene permisos adecuados en la carpeta del servidor.

## Contribuir al Proyecto

¡Las contribuciones son bienvenidas! Si deseas mejorar estas herramientas:

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b mi-nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -am 'Añade alguna característica'`)
4. Push a la rama (`git push origin mi-nueva-caracteristica`)
5. Crea un nuevo Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## Contacto

Si tienes preguntas o sugerencias, no dudes en contactarnos:

- Email: [xxxx]
- GitHub: [@Glixhito]

---

Desarrollado con ❤ para la comunidad de Minecraft y mis amigos.

