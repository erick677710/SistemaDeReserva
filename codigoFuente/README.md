## Qué incluye
- Inicio de sesión de cliente y administrador.
- Pantalla de bienvenida.
- Selección de minimarket.
- Horarios de atención.
- Selección de productos y cantidad.
- lista de reserva.
- Creación de reserva.
- Listado y detalle de reservas.
- Edición y cancelación de reservas.
- Validaciones del flujo: credenciales, minimarket, producto y cantidad.
- Panel de gestión.
- Gestión de reservas: aceptar/rechazar.
- Gestión de productos: stock/precio.
- SQLite con datos iniciales.

## Credenciales de prueba

Cliente:
- usuario: `cliente`
- contraseña: `cliente123`

Administrador:
- usuario: `admin`
- contraseña: `admin123`

## Ejecutar

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`.

La base `minimarket.db` se crea automáticamente en el primer arranque.
 
enlace al fingma 
https://www.figma.com/design/rWg0s6S5XHL7o61Us0s8XC/Sin-t%C3%ADtulo?node-id=0-1&t=nWSbXY6jDG8hGo0t-1