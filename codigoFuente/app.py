from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "CAMBIA_ESTA_CLAVE_EN_PRODUCCION"

DB = "sistema.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('cliente', 'dependiente')),
            minimarket_id INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS minimarkets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            minimarket_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            minimarket_id INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)

    # Datos iniciales
    if cur.execute("SELECT COUNT(*) FROM minimarkets").fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO minimarkets (nombre, telefono) VALUES (?, ?)",
            ("Minimarket Central", "59167771092")
        )
        cur.execute(
            "INSERT INTO minimarkets (nombre, telefono) VALUES (?, ?)",
            ("Minimarket La Plaza", "59167771092")
        )
        cur.execute(
            "INSERT INTO minimarkets (nombre, telefono) VALUES (?, ?)",
            ("Minimarket Norte", "59167771092")
        )

    if cur.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0:
        productos = [
            (1, "Papas"), (1, "Cebollas"), (1, "Peras"), (1, "Tomates"),
            (2, "Arroz"), (2, "Leche"), (2, "Pan"), (2, "Huevos"),
            (3, "Zanahorias"), (3, "Manzanas"), (3, "Plátanos")
        ]
        cur.executemany(
            "INSERT INTO productos (minimarket_id, nombre) VALUES (?, ?)",
            productos
        )

    # Usuarios de demostración
    if cur.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        cur.execute(
            """INSERT INTO usuarios (usuario, password_hash, rol, minimarket_id)
               VALUES (?, ?, ?, ?)""",
            ("cliente", generate_password_hash("1234"), "cliente", None)
        )
        cur.execute(
            """INSERT INTO usuarios (usuario, password_hash, rol, minimarket_id)
               VALUES (?, ?, ?, ?)""",
            ("dependiente", generate_password_hash("1234"), "dependiente", 1)
        )

    conn.commit()
    conn.close()


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session:
                return jsonify({"error": "No has iniciado sesión"}), 401

            if role and session.get("rol") != role:
                return jsonify({"error": "No tienes permiso"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cliente")
def cliente():
    if session.get("rol") != "cliente":
        return redirect(url_for("index"))
    return render_template("cliente.html")


@app.route("/seleccionar-minimarket")
def seleccionar_minimarket():
    if session.get("rol") != "cliente":
        return redirect(url_for("index"))

    return render_template("seleccionar_minimarket.html")


@app.route("/seleccionar-productos")
def seleccionar_productos():
    if session.get("rol") != "cliente":
        return redirect(url_for("index"))

    return render_template("seleccionar_productos.html")


@app.route("/dependiente")
def dependiente():
    if session.get("rol") != "dependiente":
        return redirect(url_for("index"))
    return render_template("dependiente.html")


@app.post("/api/login")
def api_login():
    data = request.get_json() or {}
    usuario = data.get("usuario", "").strip()
    password = data.get("password", "")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    session["usuario_id"] = user["id"]
    session["usuario"] = user["usuario"]
    session["rol"] = user["rol"]
    session["minimarket_id"] = user["minimarket_id"]

    destino = "cliente" if user["rol"] == "cliente" else "dependiente"
    return jsonify({"ok": True, "rol": user["rol"], "destino": destino})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    if "usuario_id" not in session:
        return jsonify({"autenticado": False})

    return jsonify({
        "autenticado": True,
        "usuario": session["usuario"],
        "rol": session["rol"],
        "minimarket_id": session.get("minimarket_id")
    })


@app.get("/api/minimarkets")
def get_minimarkets():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nombre FROM minimarkets ORDER BY nombre"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.get("/api/minimarkets/<int:minimarket_id>/productos")
def get_productos(minimarket_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT id, nombre
           FROM productos
           WHERE minimarket_id = ?
           ORDER BY nombre""",
        (minimarket_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.post("/api/pedidos")
@login_required("cliente")
def crear_pedido():
    data = request.get_json() or {}
    minimarket_id = data.get("minimarket_id")
    items = data.get("items", [])

    if not minimarket_id or not items:
        return jsonify({"error": "Pedido incompleto"}), 400

    conn = get_db()

    minimarket = conn.execute(
        "SELECT * FROM minimarkets WHERE id = ?", (minimarket_id,)
    ).fetchone()

    if not minimarket:
        conn.close()
        return jsonify({"error": "Minimarket no encontrado"}), 404

    # Validar que todos los productos pertenecen al minimarket
    for item in items:
        producto = conn.execute(
            """SELECT id FROM productos
               WHERE id = ? AND minimarket_id = ?""",
            (item.get("producto_id"), minimarket_id)
        ).fetchone()

        if not producto or int(item.get("cantidad", 0)) <= 0:
            conn.close()
            return jsonify({"error": "Producto o cantidad inválida"}), 400

    cur = conn.cursor()
    cur.execute(
        """INSERT INTO pedidos (usuario_id, minimarket_id)
           VALUES (?, ?)""",
        (session["usuario_id"], minimarket_id)
    )
    pedido_id = cur.lastrowid

    for item in items:
        cur.execute(
            """INSERT INTO detalle_pedido
               (pedido_id, producto_id, cantidad)
               VALUES (?, ?, ?)""",
            (pedido_id, item["producto_id"], int(item["cantidad"]))
        )

    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "pedido_id": pedido_id,
        "telefono": minimarket["telefono"]
    })


@app.get("/api/pedidos")
@login_required("dependiente")
def listar_pedidos():
    minimarket_id = session.get("minimarket_id")

    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            p.id AS pedido_id,
            u.usuario,
            m.nombre AS minimarket,
            p.estado,
            p.creado_en,
            GROUP_CONCAT(dp.cantidad || ' x ' || pr.nombre, ', ') AS productos
        FROM pedidos p
        JOIN usuarios u ON u.id = p.usuario_id
        JOIN minimarkets m ON m.id = p.minimarket_id
        JOIN detalle_pedido dp ON dp.pedido_id = p.id
        JOIN productos pr ON pr.id = dp.producto_id
        WHERE p.minimarket_id = ?
        GROUP BY p.id
        ORDER BY p.id DESC
        """,
        (minimarket_id,)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.post("/api/productos")
@login_required("dependiente")
def crear_producto():
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    minimarket_id = session.get("minimarket_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO productos (minimarket_id, nombre)
           VALUES (?, ?)""",
        (minimarket_id, nombre)
    )
    conn.commit()
    producto_id = cur.lastrowid
    conn.close()

    return jsonify({
        "ok": True,
        "id": producto_id,
        "nombre": nombre
    })


@app.delete("/api/productos/<int:producto_id>")
@login_required("dependiente")
def eliminar_producto(producto_id):
    minimarket_id = session.get("minimarket_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """DELETE FROM productos
           WHERE id = ? AND minimarket_id = ?""",
        (producto_id, minimarket_id)
    )
    conn.commit()
    eliminado = cur.rowcount > 0
    conn.close()

    if not eliminado:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
