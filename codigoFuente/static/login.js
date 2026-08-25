const botonLogin = document.getElementById("login");

botonLogin.addEventListener("click", async function () {
    const usuario = document.getElementById("usuario").value.trim();
    const password = document.getElementById("password").value;
    const mensaje = document.getElementById("mensaje");

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                usuario: usuario,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            mensaje.textContent = data.error;
            return;
        }

        if (data.rol === "cliente") {
            window.location.href = "/cliente";
        } else if (data.rol === "dependiente") {
            window.location.href = "/dependiente";
        }
    } catch (error) {
        mensaje.textContent = "No se pudo conectar con el servidor.";
        console.error(error);
    }
});
