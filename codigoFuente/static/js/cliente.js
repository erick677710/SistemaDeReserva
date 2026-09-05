

function prepararFormularioRegistro() {
    const formulario = document.querySelector('#form-registro');

    if (!formulario) return;

    formulario.addEventListener('submit', (evento) => {
        if (!validarFormulario(formulario)) {
            evento.preventDefault();
        }
    });
}

function prepararFormularioLogin() {
    const formulario = document.querySelector('#form-login');

    if (!formulario) return;

    formulario.addEventListener('submit', (evento) => {
        if (!validarFormulario(formulario)) {
            evento.preventDefault();
        }
    });
}

function prepararSeleccionProductos() {
    const formulario = document.querySelector('#form-productos');
    const cantidades = document.querySelectorAll('.cantidad-producto');

    if (!formulario) return;

    formulario.addEventListener('submit', (evento) => {
        const hayProductos = Array.from(cantidades).some(
            (input) => Number(input.value) > 0
        );

        if (!hayProductos) {
            evento.preventDefault();
            alert('Selecciona al menos un producto.');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    prepararFormularioRegistro();
    prepararFormularioLogin();
    prepararSeleccionProductos();
});
