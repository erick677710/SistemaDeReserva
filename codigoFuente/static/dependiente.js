async function cargarInfo() {
    const response = await fetch("/api/me");
    const data = await response.json();

    if (!data.autenticado || data.rol !== "dependiente") {
        window.location.href = "/";
        return;
    }

    document.getElementById("info").textContent =
        `Usuario: ${data.usuario} | Minimarket ID: ${data.minimarket_id}`;

    cargarProductos(data.minimarket_id);
    cargarPedidos();
}

async function cargarProductos(minimarketId) {
    const response = await fetch(
        `/api/minimarkets/${minimarketId}/productos`
    );

    const productos = await response.json();
    const lista = document.getElementById("productos");

    lista.innerHTML = "";

    productos.forEach(producto => {
        const li = document.createElement("li");
        li.textContent = producto.nombre + " ";

        const boton = document.createElement("button");
        boton.textContent = "Eliminar";

        boton.addEventListener("click", async function () {
            const response = await fetch(
                `/api/productos/${producto.id}`,
                { method: "DELETE" }
            );

            if (response.ok) {
                cargarProductos(minimarketId);
            }
        });

        li.appendChild(boton);
        lista.appendChild(li);
    });
}

document.getElementById("agregarProducto").addEventListener(
    "click",
    async function () {
        const input = document.getElementById("nuevoProducto");
        const nombre = input.value.trim();

        if (!nombre) {
            alert("Escribe un nombre.");
            return;
        }

        const response = await fetch("/api/productos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ nombre })
        });

        if (response.ok) {
            input.value = "";
            cargarInfo();
        } else {
            alert("No se pudo agregar.");
        }
    }
);

async function cargarPedidos() {
    const response = await fetch("/api/pedidos");

    if (!response.ok) {
        return;
    }

    const pedidos = await response.json();
    const lista = document.getElementById("pedidos");

    lista.innerHTML = "";

    pedidos.forEach(pedido => {
        const li = document.createElement("li");

        li.textContent =
            `Pedido #${pedido.pedido_id} | ` +
            `Cliente: ${pedido.usuario} | ` +
            `${pedido.productos} | ` +
            `Estado: ${pedido.estado}`;

        lista.appendChild(li);
    });
}

document.getElementById("actualizarPedidos")
    .addEventListener("click", cargarPedidos);

document.getElementById("logout")
    .addEventListener("click", async function () {
        await fetch("/api/logout", { method: "POST" });
        window.location.href = "/";
    });

cargarInfo();
