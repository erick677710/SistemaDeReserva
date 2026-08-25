const selector =
    document.getElementById("minimarket");

const boton =
    document.getElementById("seleccionar");

const mensaje =
    document.getElementById("mensaje");


// ========================================
// CARGAR MINIMARKETS
// ========================================

async function cargarMinimarkets() {

    const response =
        await fetch("/api/minimarkets");

    const minimarkets =
        await response.json();


    minimarkets.forEach(function(minimarket) {

        const opcion =
            document.createElement("option");

        opcion.value =
            minimarket.id;

        opcion.textContent =
            minimarket.nombre;

        selector.appendChild(opcion);

    });

}


cargarMinimarkets();


// ========================================
// SELECCIONAR MINIMARKET
// ========================================

boton.addEventListener(
    "click",
    function() {

        const id =
            Number(selector.value);


        if (!id) {

            mensaje.textContent =
                "Selecciona un minimarket.";

            return;
        }


        // Guardamos el ID temporalmente

        localStorage.setItem(
            "minimarketid",
            id
        );


        // Ir a la segunda página

        window.location.href =
            "/seleccionar-productos";

    }
);