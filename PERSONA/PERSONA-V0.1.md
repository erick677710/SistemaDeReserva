# Persona V0.1
Nombre: Carlos 40 años
Situacion: Es una persona organizada y previsora que realiza compras de abastecimiento o reposición para su hogar. Planifica sus salidas con antelación revisando lo que le falta en casa para no hacer compras improvisadas.
Objetivo: Hacer sus compras en un solo lugar, de forma rápida y eficiente, sin perder tiempo buscando productos en los pasillos ni haciendo filas.
Dificultad: Le molesta perder tiempo dando vueltas en la tienda para no encontrar lo que busca, tener que ir a varios locales para completar su lista, o quedarse atascado en cajas lentas.
Necesidad: Garantizar que los productos que busca estén disponibles en el local al que va y poder agilizar el proceso de recolección y pago antes de salir de casa.


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
                                │       │          └─ Datos personales
                                │       │        
                                │       │         
                                │       │
                                │       └─ Mis reservas  
                                │           └─ Detalle de reserva
                                │
                                └─ Buscar minimarket
                                     │
                                     └─ Detalle minimarket
                                          ├─ Información
                                          ├─ Productos
                                          ├─ Horarios
                                          └─ Reservar
                                
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
