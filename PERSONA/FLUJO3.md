# app map
```mermaid
flowchart TD
    A[Aplicación] --> B[Inicio de sesión]

    B --> C[Cliente]
    B --> D[Dependiente]

    %% =========================
    %% FLUJO DEL CLIENTE
    %% =========================

    C --> C1[Inicio]
    C1 --> C6[Seleccionar minimarket]
    C1 --> C3[Mis reservas]
    C1 --> C4[Perfil]
    C1 --> C5[Cerrar sesión]

    %% Crear reserva
    C6 --> C7[Productos del minimarket]

    C7 --> C8[Seleccionar productos]
    C8 --> C2[Crear reserva]
    C2 --> C9[Revisar pedido]
    C9 --> C10[Reserva creada]

    %% Otras opciones del cliente
    C3 --> C12[Ver mis reservas]
    C12 --> C13[Detalle de reserva]

    C4 --> C14[Datos personales]

    %% =========================
    %% FLUJO DEL DEPENDIENTE
    %% =========================

    D --> D1[Panel]
    D1 --> D2[Gestionar productos]
    D1 --> D3[Ver reservas]
    D1 --> D4[Cerrar sesión]

    %% Gestión de productos
    D2 --> D5[Añadir productos]
    D2 --> D6[Editar productos]
    D2 --> D7[Eliminar productos]

    %% Gestión de reservas
    D3 --> D8[Ver reserva]
    D8 --> D9[Aceptar reserva]
    D8 --> D10[Rechazar reserva]

    D9 --> D11[En preparación]
    D11 --> D12[Lista para recoger]
    D12 --> D13[Entregada]

    D10 --> D14[Reserva rechazada]

    %% =========================
    %% CONEXIÓN CLIENTE-DEPENDIENTE
    %% =========================

    C11 --> D3
```

## Descripción del flujo

### Inicio de sesión

La aplicación comienza en la pantalla de **Inicio de sesión**. Una vez que el usuario inicia sesión, puede acceder a la aplicación como **Cliente** o **Dependiente**.

### Cliente

Al ingresar como **Cliente**, se muestra la pantalla de **Inicio**. Desde allí, el cliente puede:

* **Crear una reserva.**
* **Cerrar sesión.**

Al seleccionar **Crear reserva**, el cliente puede volver a la página anterior o seleccionar un **minimarket**.

Después de seleccionar un minimarket, se abre una página donde el cliente puede:

* Consultar los **productos disponibles**.
* Seleccionar los productos que desea reservar.
* **Enviar un mensaje al dependiente.**
* Volver a la selección de minimarkets.

Una vez seleccionados los productos, el cliente puede **crear la reserva**. La reserva queda registrada y pasa a estar disponible para que el dependiente pueda revisarla.

### Dependiente

Al ingresar como **Dependiente**, puede administrar los productos del minimarket y gestionar las reservas realizadas por los clientes.

Sus principales funciones son:

* **Añadir productos** al minimarket.
* **Eliminar productos** del minimarket.
* **Ver las reservas pendientes de confirmación.**
* **Aceptar o rechazar reservas.**
* **Cerrar sesión.**

Cuando el dependiente acepta una reserva, puede continuar gestionándola hasta que el pedido esté listo para ser recogido por el cliente.

### Flujo general

El flujo de la aplicación comienza con el **inicio de sesión** y se divide según el tipo de usuario:

* El **Cliente** selecciona un minimarket, consulta sus productos, selecciona los productos que desea y crea una reserva.
* El **Dependiente** recibe la reserva, la revisa y puede aceptarla o rechazarla.
* Si la reserva es aceptada, el dependiente puede gestionar su estado hasta que el pedido esté listo para ser entregado.
* Finalmente, ambos usuarios pueden **cerrar sesión**.


Flujo principal del sistema: **selección de minimarket → selección de productos → creación de reserva → revisión y confirmación por parte del dependiente**.

```
                         SISTEMA DE RESERVAS
                                  │
                         ┌────────┴────────┐
                         │                 │
                      CLIENTE          DEPENDIENTE
                         │                 │
              ┌──────────┼─────────┐       │
              │          │         │       │
           Iniciar     Crear     Mis      Panel
           sesión     reserva   reservas    │
              │          │         │        │
              │          │         │   ┌────┴──────────┐
              │          │         │   │               │
              │          │         │ Gestionar      Gestionar
              │          │         │ productos      reservas
              │          │         │   │               │
              │          │         │   ├─ Añadir       ├─ Ver reservas
              │          │         │   ├─ Editar       │
              │          │         │   └─ Eliminar     └─ Detalle reserva
              │          │         │                       │
              │          │         └─ Detalle               │
              │          │                                 │
              │       Seleccionar                           │
              │       minimarket                            │
              │          │                                  │
              │       Ver productos                         │
              │          │                                  │
              │       Seleccionar                           │
              │        productos                            │
              │          │                                  │
              │       Revisar pedido                         │
              │          │                                  │
              │       Crear reserva ────────────────────────┘
              │          │
              │       Reserva creada
              │
              │
           Cerrar sesión
```
