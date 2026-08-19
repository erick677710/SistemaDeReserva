const minimarkets = [
    {
        id: 1,
        nombre: "Minimarket Central",
        productos: [
            {
                id: 1,
                nombre: "Papas"
            },
            {
                id: 2,
                nombre: "Cebollas"
            },
            {
                id: 3,
                nombre: "Peras"
            },
            {
                id: 4,
                nombre: "Tomates"
            }
        ]
    },
    {
        id: 2,
        nombre: "Minimarket La Plaza",
        productos: [
            {
                id: 5,
                nombre: "Arroz"
            },
            {
                id: 6,
                nombre: "Leche"
            },
            {
                id: 7,
                nombre: "Pan"
            },
            {
                id: 8,
                nombre: "Huevos"
            }
        ]
    },
    {
        id: 3,
        nombre: "Minimarket Norte",
        productos: [
            {
                id: 9,
                nombre: "Zanahorias"
            },
            {
                id: 10,
                nombre: "Manzanas"
            },
            {
                id: 11,
                nombre: "Plátanos"
            }
        ]
    }

];
const selectorMinimarket = document.getElementById("Minimarket");
const selectorProducto   = document.getElementById("Producto");
const cantidad           = document.getElementById("Cantidad");
const botonAgregar       = document.getElementById("Agregar");
const mensaje            = document.getElementById("Mensaje");
const botonWhatsApp      = document.getElementById("Whatsapp");

// perdido es un string que contiene el pedido completo que redundante
// tambien es el mensaje que se mandara al dependiente
let pedido = "";

minimarkets.forEach(function(minimarket) {
    const opcion = document.createElement("option");
    opcion.value = minimarket.id;
    opcion.textContent = minimarket.nombre;
    selectorMinimarket.appendChild(opcion);
});

selectorMinimarket.addEventListener("change", function() {
    
    const idMinimarket =
        Number(selectorMinimarket.value);
    selectorProducto.innerHTML = "";

    if (!idMinimarket) {
        const opcion = document.createElement("option");
        opcion.textContent =
            "-- Selecciona primero un minimarket --";
        selectorProducto.appendChild(opcion);
        return;
    }

    const minimarketSeleccionado =
        minimarkets.find(function(minimarket) {
            return minimarket.id === idMinimarket;
        });

    minimarketSeleccionado.productos.forEach(function(producto) {

        const opcion = document.createElement("option");
        opcion.value = producto.id;
        opcion.textContent = producto.nombre;
        selectorProducto.appendChild(opcion);

    });

});

botonAgregar.addEventListener("click", function() {
    // aqui estan las alertas 
    // falta validar que no reserves mas de un producto del mismo minimarket
    if (selectorMinimarket.value === "") {
        alert("Selecciona un minimarket");
        return;
    }

    const productoSeleccionado =
        selectorProducto.options[
            selectorProducto.selectedIndex
        ];

    if (!productoSeleccionado) {
        alert("Selecciona un producto");
        return;
    }

    const cantidadProducto =
        Number(cantidad.value);

    if (cantidadProducto <= 0) {
        alert("La cantidad debe ser mayor a 0");
        return;
    }

    const minimarketSeleccionado =
        selectorMinimarket.options[
            selectorMinimarket.selectedIndex
        ].text;

    const nombreProducto =
        productoSeleccionado.text;

    if (pedido === "") {
        pedido =
            `Pedido para: ${minimarketSeleccionado}\n\n`;
    }
    pedido +=
        `${cantidadProducto} ${nombreProducto}\n`;


    mensaje.textContent = pedido;

    cantidad.value = 1;

});

botonWhatsApp.addEventListener("click", function() {

    if (pedido === "") {
        alert("Primero agrega algún producto");
        return;
    }
    const numero = "59167771092";
    const enlace = `https://wa.me/${numero}?text=${encodeURIComponent(pedido)}`;
    window.location.href = enlace;
});