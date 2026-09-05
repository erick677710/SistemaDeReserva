# Sistema de Reservas - versión organizada

Aplicación educativa hecha con **Flask + SQLite + HTML + CSS + JavaScript**.

## Idea de la organización

Los archivos HTML contienen principalmente la **estructura y el contenido de la página**.

JavaScript contiene la **interactividad del navegador**, por ejemplo:

- Validaciones del formulario antes de enviarlo.
- Confirmaciones antes de eliminar o cambiar estados.
- Comprobaciones de selección de productos.

Python/Flask sigue encargado de:

- Login y sesiones.
- Roles y permisos.
- Validaciones de seguridad en el servidor.
- Consultas y cambios en SQLite.
- Creación y actualización de reservas.
- Gestión de productos.

> JavaScript no reemplaza las validaciones de Flask. El navegador puede ser manipulado, por lo que las reglas importantes también se comprueban en el servidor.

## Estructura

```text
SistemaDeReservaCompleto/
├── app.py
├── requirements.txt
├── README.md
├── run.bat
├── .gitignore
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── registro.html
│   ├── error.html
│   ├── cliente/
│   │   ├── inicio.html
│   │   ├── minimarkets.html
│   │   ├── minimarket_detalle.html
│   │   ├── revisar_pedido.html
│   │   ├── reserva_creada.html
│   │   ├── reservas.html
│   │   ├── detalle_reserva.html
│   │   └── perfil.html
│   └── dependiente/
│       ├── panel.html
│       ├── reservas.html
│       ├── detalle_reserva.html
│       └── productos.html
└── static/
    ├── styles.css
    └── js/
        ├── app.js
        ├── cliente.js
        └── dependiente.js
```

## Ejecutar

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Luego abrir:

```text
http://127.0.0.1:5000
```

## Usuario dependiente de prueba

```text
Correo: dependiente@demo.com
Contraseña: 123456
```

La base de datos `database.db` se crea automáticamente al ejecutar `app.py`.
