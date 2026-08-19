# Persona V0.1
Nombre: Carlos
Situacion: 
Objetivo:
Dificultal:
Necesidad:


# app map
                    APLICACIÓN
                         │
          ┌──────────────┴──────────────┐
          │                             │
       AUTENTICACIÓN                 CLIENTE
          │                             │
     ┌────┴────┐                 ┌─────┼──────────┐
     │         │                 │     │          │
 Registrarse Iniciar          Inicio Reservas   Perfil
              sesión            │       │          │
                                │       │          ├─ Datos personales
                                │       │          ├─ Historial
                                │       │          └─ Cerrar sesión
                                │       │
                                │       ├─ Mis reservas
                                │       │    ├─ Pendientes
                                │       │    ├─ Confirmadas
                                │       │    ├─ Completadas
                                │       │    └─ Canceladas
                                │       │
                                │       └─ Detalle de reserva
                                │
                                ├─ Buscar minimarket
                                │    │
                                │    └─ Detalle minimarket
                                │         ├─ Información
                                │         ├─ Productos
                                │         ├─ Horarios
                                │         └─ Reservar
                                │
                                └─ Notificaciones
                                     ├─ Reserva confirmada
                                     ├─ Reserva rechazada
                                     └─ Reserva lista
# Flujo
Cliente
  ↓
Inicia sesión
  ↓
Busca minimarket
  ↓
Selecciona minimarket
  ↓
Consulta productos
  ↓
Selecciona productos
  ↓
Elige fecha/hora para recoger
  ↓
Confirma reserva
  ↓
Minimarket recibe solicitud
  ↓
¿Acepta la reserva?
 ├── NO → Notificar al cliente → FIN
 │
 └── SÍ
       ↓
   Preparar pedido
       ↓
   Cliente recibe notificación
       ↓
   Cliente recoge pedido
       ↓
   Reserva completada