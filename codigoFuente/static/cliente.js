async function cargarUsuario() {
    const response = await fetch("/api/me");
    const data = await response.json();

    if (!data.autenticado || data.rol !== "cliente") {
        window.location.href = "/";
        return;
    }

    document.getElementById("bienvenida").textContent =
        `Bienvenido, ${data.usuario}`;
}

document.getElementById("logout").addEventListener("click", async function () {
    await fetch("/api/logout", { method: "POST" });
    window.location.href = "/";
});

cargarUsuario();
