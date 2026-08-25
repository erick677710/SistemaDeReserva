
const minimarketId =
    Number(localStorage.getItem("minimarketid"));
const selectorProducto =
    document.getElementById("producto");

const cantidadInput =
    document.getElementById("cantidad");

const botonAgregar =
    document.getElementById("agregar");

const botonReservar =
    document.getElementById("reservar");

const pedidoHTML =
    document.getElementById("pedido");

const nombreMinimarket =
    document.getElementById("nombreMinimarket");

const mensaje =
    document.getElementById("mensaje");

if (!minimarketId) {

    alert(
        "Primero debes seleccionar un minimarket."
    );

    window.location.href =
        "/seleccionar-minimarket";
}

let productos = [];

let pedido = [];
//cargar datos
async function cargarDatos() {
// obtener minimarket

    const responseMinimarkets =
        await fetch("/api/minimarkets");

    const minimarkets =
        await responseMinimarkets.json();


    const minimarket =
        minimarkets.find(function(m) {

            return m.id === minimarketId;

        });


    if (!minimarket) {

        alert(
            "El minimarket no existe."
        );

        window.location.href =
            "/seleccionar-minimarket";

        return;
    }


    nombreMinimarket.textContent =
        `Minimarket: ${minimarket.nombre}`;


    // obtener productos del minimarket
    const responseProductos =
        await fetch(
            `/api/minimarkets/${minimarketId}/productos`
        );


    productos =
        await responseProductos.json();


    productos.forEach(function(producto) {

        const opcion =
            document.createElement("option");

        opcion.value =
            producto.id;

        opcion.textContent =
            producto.nombre;

        selectorProducto.appendChild(
            opcion
        );

    });

}


cargarDatos();

//agregar producto

botonAgregar.addEventListener(
    "click",
    function() {

        const productoId =
            Number(selectorProducto.value);


        const cantidad =
            Number(cantidadInput.value);


        if (!productoId) {

            alert(
                "Selecciona un producto."
            );

            return;
        }


        if (cantidad <= 0) {

            alert(
                "La cantidad debe ser mayor a 0."
            );

            return;
        }


        const producto =
            productos.find(function(p) {

                return p.id === productoId;

            });


        // Agregar al pedido

        pedido.push({

            producto_id: producto.id,

            nombre: producto.nombre,

            cantidad: cantidad

        });


        mostrarPedido();


        cantidadInput.value = 1;

    }
);
// mostrar pedido
function mostrarPedido() {

    if (pedido.length === 0) {

        pedidoHTML.textContent =
            "Todavía no hay productos.";

        return;
    }


    pedidoHTML.textContent =
        pedido.map(function(item) {

            return `${item.cantidad} x ${item.nombre}`;

        }).join("\n");

}
// confirmar reserva
botonReservar.addEventListener(
    "click",
    async function() {

        if (pedido.length === 0) {

            alert(
                "Agrega al menos un producto."
            );

            return;
        }


        // conectar con el backend
        const response =
            await fetch("/api/pedidos", {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    minimarket_id:
                        minimarketId,

                    items:
                        pedido.map(function(item) {

                            return {

                                producto_id:
                                    item.producto_id,

                                cantidad:
                                    item.cantidad

                            };

                        })

                })

            });


        const data =
            await response.json();


        if (!response.ok) {

            mensaje.textContent =
                data.error ||
                "No se pudo guardar la reserva.";

            return;
        }
        //mensaje
        let texto =
            `Reserva #${data.pedido_id}\n\n`;


        pedido.forEach(function(item) {

            texto +=
                `${item.cantidad} x ${item.nombre}\n`;

        });


        const enlace =
            `https://wa.me/${data.telefono}?text=${
                encodeURIComponent(texto)
            }`;

        window.location.href =
            enlace;

    }
);