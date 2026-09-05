from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-por-una-secreta"
BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "database.db"

ESTADOS = ["Pendiente", "Aceptada", "Rechazada", "En preparación", "Lista", "Entregada"]
TRANSICIONES = {
    "Pendiente": ["Aceptada", "Rechazada"],
    "Aceptada": ["En preparación"],
    "En preparación": ["Lista"],
    "Lista": ["Entregada"],
    "Rechazada": [],
    "Entregada": [],
}


def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    con = get_db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK (rol IN ('cliente','dependiente'))
    );

    CREATE TABLE IF NOT EXISTS minimarkets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT NOT NULL,
        horario TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL CHECK(precio >= 0),
        stock INTEGER NOT NULL CHECK(stock >= 0),
        minimarket_id INTEGER NOT NULL,
        FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id)
    );

    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        minimarket_id INTEGER NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id)
    );

    CREATE TABLE IF NOT EXISTS detalle_reserva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reserva_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL CHECK(cantidad > 0),
        precio_unitario REAL NOT NULL,
        FOREIGN KEY(reserva_id) REFERENCES reservas(id) ON DELETE CASCADE,
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    );
    """)

    if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        con.execute(
            "INSERT INTO usuarios(nombre,email,password,rol) VALUES(?,?,?,?)",
            ("Dependiente Demo", "dependiente@demo.com", generate_password_hash("123456"), "dependiente")
        )

    if con.execute("SELECT COUNT(*) FROM minimarkets").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO minimarkets(nombre,direccion,horario) VALUES(?,?,?)",
            [
                ("Minimarket Central", "Av. Principal #123", "08:00 - 22:00"),
                ("Minimarket Don Pedro", "Calle Comercio #456", "09:00 - 21:00"),
            ]
        )
        markets = con.execute("SELECT id FROM minimarkets ORDER BY id").fetchall()
        m1, m2 = markets[0]["id"], markets[1]["id"]
        con.executemany(
            "INSERT INTO productos(nombre,precio,stock,minimarket_id) VALUES(?,?,?,?)",
            [
                ("Papas", 5.00, 30, m1),
                ("Cebollas", 3.00, 25, m1),
                ("Tomates", 4.00, 20, m1),
                ("Arroz", 8.50, 40, m2),
                ("Leche", 7.00, 25, m2),
                ("Pan", 2.50, 50, m2),
            ]
        )
    con.commit()
    con.close()


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session:
                return redirect(url_for("login"))
            if session.get("rol") != role:
                flash("No tienes permiso para acceder a esa sección.")
                return redirect(url_for("inicio"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def global_data():
    return {"estados": ESTADOS}


@app.route("/")
def inicio():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("cliente_inicio") if session["rol"] == "cliente" else url_for("panel_dependiente"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        email_valido = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)

        if not nombre :
            #or not email_valido or len(password) < 6
            flash("Completa los campos correctamente. La contraseña debe tener al menos 6 caracteres y el correo debe ser válido.")
            return redirect(url_for("registro"))
        con = get_db()
        try:
            con.execute(
                "INSERT INTO usuarios(nombre,email,password,rol) VALUES(?,?,?,?)",
                (nombre, email, generate_password_hash(password), "cliente")
            )
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            flash("Ese correo ya está registrado.")
            return redirect(url_for("registro"))
        con.close()
        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for("login"))
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        con = get_db()
        usuario = con.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
        con.close()
        if usuario and check_password_hash(usuario["password"], password):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            return redirect(url_for("inicio"))
        flash("Correo o contraseña incorrectos.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for("login"))


# ========================= CLIENTE =========================

@app.route("/cliente")
@role_required("cliente")
def cliente_inicio():
    return render_template("cliente/inicio.html", nombre=session["nombre"])


@app.route("/minimarkets")
@role_required("cliente")
def minimarkets():
    con = get_db()
    markets = con.execute("SELECT * FROM minimarkets ORDER BY nombre").fetchall()
    con.close()
    return render_template("cliente/minimarkets.html", minimarkets=markets)


@app.route("/minimarket/<int:minimarket_id>")
@role_required("cliente")
def minimarket_detalle(minimarket_id):
    con = get_db()
    market = con.execute("SELECT * FROM minimarkets WHERE id=?", (minimarket_id,)).fetchone()
    products = con.execute("SELECT * FROM productos WHERE minimarket_id=? ORDER BY nombre", (minimarket_id,)).fetchall()
    con.close()
    if not market:
        abort(404)
    return render_template("cliente/minimarket_detalle.html", minimarket=market, productos=products)


@app.route("/minimarket/<int:minimarket_id>/productos")
@role_required("cliente")
def productos(minimarket_id):
    return redirect(url_for("minimarket_detalle", minimarket_id=minimarket_id))


@app.route("/pedido/revisar", methods=["POST"])
@role_required("cliente")
def revisar_pedido():
    try:
        minimarket_id = int(request.form["minimarket_id"])
    except (ValueError, KeyError):
        flash("Minimarket inválido.")
        return redirect(url_for("minimarkets"))

    cantidades = request.form.getlist("cantidad")
    producto_ids = request.form.getlist("producto_id")
    seleccionados = []
    con = get_db()

    for pid, cantidad_raw in zip(producto_ids, cantidades):
        try:
            cantidad = int(cantidad_raw)
            producto_id = int(pid)
        except ValueError:
            continue
        if cantidad > 0:
            producto = con.execute(
                "SELECT * FROM productos WHERE id=? AND minimarket_id=?",
                (producto_id, minimarket_id)
            ).fetchone()
            if not producto or cantidad > producto["stock"]:
                con.close()
                flash(f"Cantidad inválida o stock insuficiente para el producto #{producto_id}.")
                return redirect(url_for("minimarket_detalle", minimarket_id=minimarket_id))
            seleccionados.append((producto, cantidad))

    market = con.execute("SELECT * FROM minimarkets WHERE id=?", (minimarket_id,)).fetchone()
    con.close()

    if not market:
        flash("Minimarket no encontrado.")
        return redirect(url_for("minimarkets"))
    if not seleccionados:
        flash("Selecciona al menos un producto.")
        return redirect(url_for("minimarket_detalle", minimarket_id=minimarket_id))

    items = [{"id": p["id"], "nombre": p["nombre"], "precio": p["precio"], "cantidad": c, "subtotal": p["precio"] * c} for p, c in seleccionados]
    return render_template("cliente/revisar_pedido.html", minimarket=market, items=items, total=sum(i["subtotal"] for i in items))


@app.route("/reserva/crear", methods=["POST"])
@role_required("cliente")
def crear_reserva():
    try:
        minimarket_id = int(request.form["minimarket_id"])
    except (ValueError, KeyError):
        flash("Minimarket inválido.")
        return redirect(url_for("minimarkets"))

    producto_ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    con = get_db()
    market = con.execute("SELECT * FROM minimarkets WHERE id=?", (minimarket_id,)).fetchone()
    if not market:
        con.close()
        abort(404)

    items = []
    for pid, raw_qty in zip(producto_ids, cantidades):
        try:
            pid, qty = int(pid), int(raw_qty)
        except ValueError:
            continue
        if qty <= 0:
            continue
        product = con.execute("SELECT * FROM productos WHERE id=? AND minimarket_id=?", (pid, minimarket_id)).fetchone()
        if not product or qty > product["stock"]:
            con.close()
            flash("El pedido cambió o ya no hay suficiente stock. Revisa nuevamente.")
            return redirect(url_for("minimarket_detalle", minimarket_id=minimarket_id))
        items.append((product, qty))

    if not items:
        con.close()
        flash("No hay productos seleccionados.")
        return redirect(url_for("minimarket_detalle", minimarket_id=minimarket_id))

    cur = con.execute(
        "INSERT INTO reservas(usuario_id,minimarket_id,estado) VALUES(?,?,?)",
        (session["usuario_id"], minimarket_id, "Pendiente")
    )
    reserva_id = cur.lastrowid

    for product, qty in items:
        con.execute(
            "INSERT INTO detalle_reserva(reserva_id,producto_id,cantidad,precio_unitario) VALUES(?,?,?,?)",
            (reserva_id, product["id"], qty, product["precio"])
        )
        con.execute("UPDATE productos SET stock=stock-? WHERE id=?", (qty, product["id"]))

    con.commit()
    con.close()
    return redirect(url_for("reserva_creada", reserva_id=reserva_id))


@app.route("/reserva/<int:reserva_id>/confirmacion")
@role_required("cliente")
def reserva_creada(reserva_id):
    reserva = obtener_reserva(reserva_id)
    verificar_cliente_reserva(reserva)
    return render_template("cliente/reserva_creada.html", reserva=reserva)


@app.route("/reservas")
@role_required("cliente")
def reservas_cliente():
    con = get_db()
    rows = con.execute("""
        SELECT r.*, m.nombre AS minimarket
        FROM reservas r JOIN minimarkets m ON m.id=r.minimarket_id
        WHERE r.usuario_id=? ORDER BY r.id DESC
    """, (session["usuario_id"],)).fetchall()
    con.close()
    return render_template("cliente/reservas.html", reservas=rows)


@app.route("/reserva/<int:reserva_id>")
@role_required("cliente")
def detalle_reserva_cliente(reserva_id):
    reserva = obtener_reserva(reserva_id)
    verificar_cliente_reserva(reserva)
    return render_template("cliente/detalle_reserva.html", reserva=reserva, detalles=obtener_detalles(reserva_id), transiciones=TRANSICIONES[reserva["estado"]])


@app.route("/perfil", methods=["GET", "POST"])
@role_required("cliente")
def perfil():
    con = get_db()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        email_valido = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)

        if not nombre or not email_valido:
            con.close()
            flash("Nombre y correo son obligatorios y el correo debe tener un formato válido.")
            return redirect(url_for("perfil"))
        try:
            con.execute("UPDATE usuarios SET nombre=?, email=? WHERE id=?", (nombre, email, session["usuario_id"]))
            con.commit()
            session["nombre"] = nombre
            flash("Datos actualizados.")
        except sqlite3.IntegrityError:
            flash("Ese correo ya está en uso.")
        con.close()
        return redirect(url_for("perfil"))
    user = con.execute("SELECT id,nombre,email,rol FROM usuarios WHERE id=?", (session["usuario_id"],)).fetchone()
    con.close()
    return render_template("cliente/perfil.html", usuario=user)


# ======================= DEPENDIENTE ========================

@app.route("/dependiente")
@role_required("dependiente")
def panel_dependiente():
    con = get_db()
    stats = {
        "pendientes": con.execute("SELECT COUNT(*) FROM reservas WHERE estado='Pendiente'").fetchone()[0],
        "preparacion": con.execute("SELECT COUNT(*) FROM reservas WHERE estado='En preparación'").fetchone()[0],
        "listas": con.execute("SELECT COUNT(*) FROM reservas WHERE estado='Lista'").fetchone()[0],
        "entregadas": con.execute("SELECT COUNT(*) FROM reservas WHERE estado='Entregada'").fetchone()[0],
    }
    con.close()
    return render_template("dependiente/panel.html", stats=stats)


@app.route("/dependiente/reservas")
@role_required("dependiente")
def reservas_dependiente():
    estado = request.args.get("estado", "").strip()
    con = get_db()
    if estado in ESTADOS:
        rows = con.execute("""
            SELECT r.*,u.nombre AS cliente,m.nombre AS minimarket
            FROM reservas r JOIN usuarios u ON u.id=r.usuario_id JOIN minimarkets m ON m.id=r.minimarket_id
            WHERE r.estado=? ORDER BY r.id DESC
        """, (estado,)).fetchall()
    else:
        rows = con.execute("""
            SELECT r.*,u.nombre AS cliente,m.nombre AS minimarket
            FROM reservas r JOIN usuarios u ON u.id=r.usuario_id JOIN minimarkets m ON m.id=r.minimarket_id
            ORDER BY r.id DESC
        """).fetchall()
    con.close()
    return render_template("dependiente/reservas.html", reservas=rows, filtro=estado)


@app.route("/dependiente/reserva/<int:reserva_id>")
@role_required("dependiente")
def detalle_reserva_dependiente(reserva_id):
    reserva = obtener_reserva(reserva_id)
    if not reserva:
        abort(404)
    return render_template("dependiente/detalle_reserva.html", reserva=reserva, detalles=obtener_detalles(reserva_id), transiciones=TRANSICIONES[reserva["estado"]])


@app.route("/dependiente/reserva/<int:reserva_id>/estado", methods=["POST"])
@role_required("dependiente")
def cambiar_estado(reserva_id):
    nuevo = request.form.get("estado", "")
    reserva = obtener_reserva(reserva_id)
    if not reserva:
        abort(404)
    if nuevo not in TRANSICIONES[reserva["estado"]]:
        flash(f"No se puede pasar de {reserva['estado']} a {nuevo}.")
        return redirect(url_for("detalle_reserva_dependiente", reserva_id=reserva_id))
    con = get_db()
    con.execute("UPDATE reservas SET estado=? WHERE id=?", (nuevo, reserva_id))
    con.commit()
    con.close()
    flash(f"Reserva #{reserva_id} actualizada a: {nuevo}.")
    return redirect(url_for("detalle_reserva_dependiente", reserva_id=reserva_id))


# Atajos para que el código refleje literalmente el flujo del diagrama.
@app.post("/dependiente/reserva/<int:reserva_id>/aceptar")
@role_required("dependiente")
def aceptar_reserva(reserva_id):
    return cambiar_estado_directo(reserva_id, "Aceptada")

@app.post("/dependiente/reserva/<int:reserva_id>/rechazar")
@role_required("dependiente")
def rechazar_reserva(reserva_id):
    return cambiar_estado_directo(reserva_id, "Rechazada")

@app.post("/dependiente/reserva/<int:reserva_id>/preparar")
@role_required("dependiente")
def preparar_reserva(reserva_id):
    return cambiar_estado_directo(reserva_id, "En preparación")

@app.post("/dependiente/reserva/<int:reserva_id>/lista")
@role_required("dependiente")
def marcar_lista(reserva_id):
    return cambiar_estado_directo(reserva_id, "Lista")

@app.post("/dependiente/reserva/<int:reserva_id>/entregar")
@role_required("dependiente")
def entregar_reserva(reserva_id):
    return cambiar_estado_directo(reserva_id, "Entregada")


def cambiar_estado_directo(reserva_id, nuevo):
    reserva = obtener_reserva(reserva_id)
    if not reserva:
        abort(404)
    if nuevo not in TRANSICIONES[reserva["estado"]]:
        flash(f"Transición no permitida: {reserva['estado']} → {nuevo}.")
        return redirect(url_for("detalle_reserva_dependiente", reserva_id=reserva_id))
    con = get_db()
    con.execute("UPDATE reservas SET estado=? WHERE id=?", (nuevo, reserva_id))
    con.commit()
    con.close()
    flash(f"Reserva #{reserva_id}: {nuevo}.")
    return redirect(url_for("detalle_reserva_dependiente", reserva_id=reserva_id))


@app.route("/dependiente/productos")
@role_required("dependiente")
def productos_dependiente():
    con = get_db()
    products = con.execute("""
        SELECT p.*,m.nombre AS minimarket
        FROM productos p JOIN minimarkets m ON m.id=p.minimarket_id
        ORDER BY m.nombre,p.nombre
    """).fetchall()
    markets = con.execute("SELECT * FROM minimarkets ORDER BY nombre").fetchall()
    con.close()
    return render_template("dependiente/productos.html", productos=products, minimarkets=markets)


@app.post("/dependiente/producto/nuevo")
@role_required("dependiente")
def nuevo_producto():
    try:
        nombre = request.form["nombre"].strip()
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        minimarket_id = int(request.form["minimarket_id"])
        if not nombre or precio < 0 or stock < 0:
            raise ValueError
    except (ValueError, KeyError):
        flash("Datos de producto inválidos.")
        return redirect(url_for("productos_dependiente"))
    con = get_db()
    if not con.execute("SELECT 1 FROM minimarkets WHERE id=?", (minimarket_id,)).fetchone():
        con.close()
        flash("Minimarket inválido.")
        return redirect(url_for("productos_dependiente"))
    con.execute("INSERT INTO productos(nombre,precio,stock,minimarket_id) VALUES(?,?,?,?)", (nombre, precio, stock, minimarket_id))
    con.commit(); con.close()
    flash("Producto añadido.")
    return redirect(url_for("productos_dependiente"))


@app.post("/dependiente/producto/<int:producto_id>/editar")
@role_required("dependiente")
def editar_producto(producto_id):
    try:
        nombre = request.form["nombre"].strip()
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        if not nombre or precio < 0 or stock < 0:
            raise ValueError
    except (ValueError, KeyError):
        flash("Datos de producto inválidos.")
        return redirect(url_for("productos_dependiente"))
    con = get_db()
    con.execute("UPDATE productos SET nombre=?,precio=?,stock=? WHERE id=?", (nombre, precio, stock, producto_id))
    con.commit(); con.close()
    flash("Producto actualizado.")
    return redirect(url_for("productos_dependiente"))


@app.post("/dependiente/producto/<int:producto_id>/eliminar")
@role_required("dependiente")
def eliminar_producto(producto_id):
    con = get_db()
    try:
        con.execute("DELETE FROM productos WHERE id=?", (producto_id,))
        con.commit()
        flash("Producto eliminado.")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar un producto que ya aparece en una reserva.")
    finally:
        con.close()
    return redirect(url_for("productos_dependiente"))


# =========================== HELPERS =========================

def obtener_reserva(reserva_id):
    con = get_db()
    reserva = con.execute("""
        SELECT r.*, m.nombre AS minimarket, m.direccion, m.horario,
               u.nombre AS cliente, u.email AS cliente_email
        FROM reservas r
        JOIN minimarkets m ON m.id=r.minimarket_id
        JOIN usuarios u ON u.id=r.usuario_id
        WHERE r.id=?
    """, (reserva_id,)).fetchone()
    con.close()
    return reserva


def obtener_detalles(reserva_id):
    con = get_db()
    detalles = con.execute("""
        SELECT d.*, p.nombre, d.precio_unitario,
               d.cantidad * d.precio_unitario AS subtotal
        FROM detalle_reserva d JOIN productos p ON p.id=d.producto_id
        WHERE d.reserva_id=? ORDER BY d.id
    """, (reserva_id,)).fetchall()
    con.close()
    return detalles


def verificar_cliente_reserva(reserva):
    if not reserva:
        abort(404)
    if reserva["usuario_id"] != session["usuario_id"]:
        abort(403)


@app.errorhandler(404)
def no_encontrado(error):
    return render_template("error.html", codigo=404, mensaje="Página o recurso no encontrado."), 404


@app.errorhandler(403)
def prohibido(error):
    return render_template("error.html", codigo=403, mensaje="No tienes permiso para acceder a este recurso."), 403


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
