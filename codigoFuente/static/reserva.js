let productos = [];
let carrito = [];
let minimarketSeleccionado = null;

const minimarketSelect = document.getElementById("minimarket");
const productoSelect = document.getElementById("producto");
const cantidadInput = document.getElementById("cantidad");
const pedidoPre = document.getElementById("pedido");
const mensaje = document.getElementById("mensaje");

async function cargarMinimarkets() {
    const response = await fetch("/api/minimarkets");
    const data = await response.json();

    data.forEach(minimarket => {
        const option = document.createElement("option");
        option.value = minimarket.id;
        option.textContent = minimarket.nombre;
        minimarketSelect.appendChild(option);
    });
}

minimarketSelect.addEventListener("change", async function () {
    minimarketSeleccionado = Number(this.value);

    productoSelect.innerHTML = "";

    if (!minimarketSeleccionado) {
        productoSelect.innerHTML =
            '<option value="">-- Selecciona un minimarket --</option>';
        return;
    }

    const response = await fetch(
        `/api/minimarkets/${minimarketSeleccionado}/productos`
    );

    productos = await response.json();

    productos.forEach(producto => {
        const option = document.createElement("option");
        option.value = producto.id;
        option.textContent = producto.nombre;
        productoSelect.appendChild(option);
    });
});

document.getElementById("agregar").addEventListener("click", function () {
    if (!minimarketSeleccionado) {
        alert("Selecciona un minimarket.");
        return;
    }

    const productoId = Number(productoSelect.value);
    const cantidad = Number(cantidadInput.value);

    if (!productoId) {
        alert("Selecciona un producto.");
        return;
    }

    if (cantidad <= 0) {
        alert("La cantidad debe ser mayor que 0.");
        return;
    }

    const producto = productos.find(p => p.id === productoId);

    carrito.push({
        producto_id: producto.id,
        nombre: producto.nombre,
        cantidad: cantidad
    });

    mostrarPedido();
    cantidadInput.value = 1;
});

function mostrarPedido() {
    if (carrito.length === 0) {
        pedidoPre.textContent = "Todavía no hay productos.";
        return;
    }

    pedidoPre.textContent = carrito
        .map(item => `${item.cantidad} x ${item.nombre}`)
        .join("\n");
}

document.getElementById("enviar").addEventListener("click", async function () {
    if (!minimarketSeleccionado || carrito.length === 0) {
        alert("Selecciona un minimarket y agrega productos.");
        return;
    }

    const response = await fetch("/api/pedidos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            minimarket_id: minimarketSeleccionado,
            items: carrito.map(item => ({
                producto_id: item.producto_id,
                cantidad: item.cantidad
            }))
        })
    });

    const data = await response.json();

    if (!response.ok) {
        mensaje.textContent = data.error || "No se pudo guardar el pedido.";
        return;
    }

    const texto = `Pedido #${data.pedido_id}\n\n` +
        carrito
            .map(item => `${item.cantidad} x ${item.nombre}`)
            .join("\n");

    const enlace = `https://wa.me/${data.telefono}?text=${encodeURIComponent(texto)}`;

    window.location.href = enlace;
});

cargarMinimarkets();
