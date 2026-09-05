

function confirmarAccion(mensaje) {
    return window.confirm(mensaje);
}

function mostrarConfirmacionAntesDeEnviar() {
    const formularios = document.querySelectorAll('[data-confirm]');

    formularios.forEach((formulario) => {
        formulario.addEventListener('submit', (evento) => {
            const mensaje = formulario.dataset.confirm;

            if (!confirmarAccion(mensaje)) {
                evento.preventDefault();
            }
        });
    });
}

function validarFormulario(formulario) {
    if (!formulario.checkValidity()) {
        formulario.reportValidity();
        return false;
    }

    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    mostrarConfirmacionAntesDeEnviar();
});
