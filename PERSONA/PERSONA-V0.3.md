# Persona V0.1
Nombre: Carlos 40 años
Situacion: Es una persona organizada y previsora que realiza compras de abastecimiento o reposición para su hogar. Planifica sus salidas con antelación revisando lo que le falta en casa para no hacer compras improvisadas.
Objetivo: Hacer sus compras en un solo lugar, de forma rápida y eficiente, sin perder tiempo buscando productos en los pasillos ni haciendo filas.
Dificultad: Le molesta perder tiempo dando vueltas en la tienda para no encontrar lo que busca, tener que ir a varios locales para completar su lista, o quedarse atascado en cajas lentas.
Necesidad: Garantizar que los productos que busca estén disponibles en el local al que va y poder agilizar el proceso de recolección y pago antes de salir de casa.


# app map
```mermaid
flowchart TD
    A[Aplicación] --> B[Inicio de sesión]

    B --> C[Cliente]
    B --> D[Dependiente]

    %% Flujo del Cliente
    C --> C1[Inicio]
    C1 --> C2[Crear reserva]
    C1 --> C3[Cerrar sesión]

    C2 --> C4[Seleccionar minimarket]
    C4 --> C5[Productos del minimarket]
    
    C5 --> C6[Seleccionar productos]
    C5 --> C7[Enviar mensaje al dependiente]
    C5 --> C8[Volver a seleccionar minimarket]

    C2 --> C9[Volver a página anterior]

    %% Flujo del Dependiente
    D --> D1[Gestionar productos]
    D --> D2[Ver reservas por confirmar]
    D --> D3[Cerrar sesión]

    D1 --> D4[Añadir productos]
    D1 --> D5[Eliminar productos]
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
* **Enviar un mensaje al dependiente**.
* Volver a la selección de minimarkets.

### Dependiente

Al ingresar como **Dependiente**, puede administrar el minimarket y gestionar las reservas.

Sus principales funciones son:

* **Añadir productos** al minimarket.
* **Eliminar productos** del minimarket.
* **Ver las reservas pendientes de confirmación.**
* **Cerrar sesión.**
# MVP

El Producto Mínimo Viable del sistema es desarrollar una versión funcional que permita realizar el proceso básico de reserva de productos en un minimarket.

El sistema tendra dos tipos de usuarios: **Cliente** y **Dependiente**.

El **Cliente** podrá iniciar sesión, seleccionar un minimarket, consultar los productos disponibles, seleccionar los productos que desea y crear una reserva. Una vez creada, la reserva quedará registrada y se enviara un mensaje al dependiente.

El **Dependiente** podrá iniciar sesión, administrar los productos disponibles en su minimarket mediante las opciones de añadir y eliminar productos, además de consultar las reservas pendientes y confirmarlas.

Flujo principal del sistema: **selección de minimarket → selección de productos → creación de reserva → revisión y confirmación por parte del dependiente**.

```
                    SISTEMA DE RESERVAS
                            │
                    ┌───────┴───────┐
                    │               │
                 CLIENTE         DEPENDIENTE
                    │               │
              ┌─────┴─────┐    ┌────┴
              │           │    │              
          Iniciar      Crear   Gestionar     
           sesión     reserva  productos     
              │           │       │            
              │           │       ├─ Añadir       
              │           │       │  producto    
              │           │       ├─ Ver              
              │           │       │  reservas
              |           |       |
              │           │       └─ Eliminar 
              │           │          producto
              │       Seleccionar
              │       minimarket
              │           │
              │       Ver productos
              │           │
              │       Seleccionar
              │        productos
              │           │
              │       Crear reserva
              │
           Cerrar sesión
```
