# Sistema de Reserva - Flask + SQLite

## Requisitos

- Python 3.10 o superior recomendado
- pip

## Instalar

En la carpeta del proyecto:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Abrir:

http://127.0.0.1:5000

## Usuarios de prueba

Cliente:

- usuario: cliente
- contraseña: 1234

Dependiente:

- usuario: dependiente
- contraseña: 1234

## Qué incluye

- Login con roles cliente/dependiente.
- Sesión en Flask.
- Contraseñas almacenadas como hash.
- SQLite.
- Lista de minimarkets.
- Productos por minimarket.
- Cliente puede crear un pedido.
- El pedido se guarda en la base de datos.
- El pedido se puede enviar por WhatsApp.
- Dependiente puede ver pedidos.
- Dependiente puede agregar/eliminar productos.

## Importante

La clave `app.secret_key` de `app.py` es solo para desarrollo. En producción debe cambiarse y almacenarse como variable de entorno.

Los datos iniciales se crean automáticamente en `sistema.db`.
