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
    C1 --> C2[Crear reserva]
    C1 --> C3[Mis reservas]
    C1 --> C4[Perfil]
    C1 --> C5[Cerrar sesión]

    %% Crear reserva
    C2 --> C6[Seleccionar minimarket]
    C6 --> C7[Productos del minimarket]

    C7 --> C8[Seleccionar productos]
    C8 --> C9[Revisar pedido]
    C9 --> C10[Crear reserva]
    C10 --> C11[Reserva creada]

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
