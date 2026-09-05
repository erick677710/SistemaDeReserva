
function prepararFormularioProducto() {
    const formulario = document.querySelector('#form-nuevo-producto');

    if (!formulario) return;

    formulario.addEventListener('submit', (evento) => {
        if (!validarFormulario(formulario)) {
            evento.preventDefault();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    prepararFormularioProducto();
});
