"""
FLUJO BÁSICO
Navegador
   |
   | GET / POST
   v
Ruta Flask (@app.route)
   |
   v
Consulta o modifica SQLite
   |
   v
render_template(...)
   |
   v
HTML/Jinja
   |
   v
Página mostrada al usuario

CONCEPTOS IMPORTANTES
- request: información que viene del navegador.
- session: información temporal asociada al usuario que ha iniciado sesión.
- g: objeto temporal de Flask usado aquí para guardar la conexión a SQLite.
- url_for(): genera URLs usando el nombre de una función Flask.
- redirect(): manda al navegador a otra ruta.
- render_template(): abre un HTML y le entrega datos.
- fetchone(): obtiene una fila de la base de datos.
- fetchall(): obtiene varias filas.
- commit(): confirma cambios realizados en la base de datos.
- @login_required: obliga a iniciar sesión antes de entrar a una ruta.
- @admin_required: obliga a tener rol "admin".
"""

from datetime import datetime
from functools import wraps
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-esta-clave-en-produccion"
DATABASE = "minimarket.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('cliente','admin'))
    );

    CREATE TABLE IF NOT EXISTS minimarkets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        mon TEXT NOT NULL DEFAULT '7:00 - 22:00',
        tue TEXT NOT NULL DEFAULT '7:00 - 22:00',
        wed TEXT NOT NULL DEFAULT '7:00 - 22:00',
        thu TEXT NOT NULL DEFAULT '7:00 - 22:00',
        fri TEXT NOT NULL DEFAULT '8:00 - 20:00'
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        minimarket_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        minimarket_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDIENTE'
            CHECK(status IN ('PENDIENTE','ACEPTADA','RECHAZADA','CANCELADA')),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(minimarket_id) REFERENCES minimarkets(id)
    );

    CREATE TABLE IF NOT EXISTS reservation_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        price REAL NOT NULL,
        FOREIGN KEY(reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            [
                ("cliente", "cliente123", "cliente"),
                ("admin", "admin123", "admin"),
            ],
        )

    if db.execute("SELECT COUNT(*) FROM minimarkets").fetchone()[0] == 0:
        markets = [
            ("MINIMARKET X", "Sucursal Central"),
            ("MINIMARKET Y", "Sucursal Norte"),
            ("MINIMARKET Z", "Sucursal Sur"),
        ]
        db.executemany(
            "INSERT INTO minimarkets(name,location) VALUES(?,?)", markets
        )

    if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        market_ids = [r["id"] for r in db.execute("SELECT id FROM minimarkets ORDER BY id")]
        names = ["PAPAS", "PERAS", "MANZANAS", "BANANAS", "COCOS"]
        for market_id in market_ids:
            for i, name in enumerate(names):
                db.execute(
                    "INSERT INTO products(minimarket_id,name,price,stock) VALUES(?,?,?,?)",
                    (market_id, name, 2.50 + i * 0.75, 20),
                )
    db.commit()

@app.before_request
def ensure_db():
    init_db()
# decoradores
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped
# decoradores
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def globals_for_templates():
    return {"session_user": session.get("username")}

@app.route("/")
def index():
    if session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("admin_panel"))
        return redirect(url_for("inicio"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not user or not password:
            error = "CONTRASEÑA INCORRECTA O FALTANTE"
        elif user["password"] != password:
            error = "CONTRASEÑA INCORRECTA O FALTANTE"
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("admin_panel" if user["role"] == "admin" else "inicio"))
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/inicio")
@login_required
def inicio():
    return render_template("inicio.html")


@app.route("/markets")
@login_required
def markets():

    db = get_db()

    markets = db.execute(
        "SELECT * FROM minimarkets ORDER BY id"
    ).fetchall()

    return render_template(
        "markets.html",
        markets=markets
    )

@app.route("/horario/<int:market_id>")
@login_required
def horario(market_id):

    db = get_db()

    market = db.execute(
        "SELECT * FROM minimarkets WHERE id = ?",
        (market_id,)
    ).fetchone()

    if not market:
        return redirect(url_for("markets"))

    return render_template(
        "horario.html",
        market=market
    )
    db = get_db()

    # Buscar el minimarket correspondiente
    market = db.execute(
        "SELECT * FROM minimarkets WHERE id = ?",
        (market_id,)
    ).fetchone()


    # Si no existe
    if not market:

        return redirect(
            url_for("markets")
        )


    return render_template(
        "horario.html",
        market=market
    )

@app.route("/reservation", methods=["GET", "POST"])
@login_required
def reservation():

    db = get_db()

    # Obtener el ID del minimarket
    market_id = (
        request.args.get("market_id", type=int)
        or request.form.get("market_id", type=int)
    )

    # Buscar el minimarket
    market = None

    if market_id:
        market = db.execute(
            "SELECT * FROM minimarkets WHERE id = ?",
            (market_id,)
        ).fetchone()

    # Si no existe, volver a markets
    if not market:
        return redirect(url_for("markets"))


    # Obtener productos de ESTE minimarket
    products = db.execute(
        """
        SELECT *
        FROM products
        WHERE minimarket_id = ?
        ORDER BY id
        """,
        (market_id,)
    ).fetchall()


    error = None


    # Obtener carrito
    cart = session.get("cart", {})

    cart = {
        str(k): int(v)
        for k, v in cart.items()
    }


    # Procesar formulario
    if request.method == "POST":

        product_id = request.form.get("product_id")

        quantity_raw = request.form.get(
            "quantity",
            ""
        ).strip()


        # No seleccionó producto
        if not product_id:

            error = "SELECCIONA UN PRODUCTO"


        # No seleccionó cantidad
        elif not quantity_raw:

            error = "SELECCIONA UNA CANTIDAD"


        else:

            try:
                quantity = int(quantity_raw)

            except ValueError:
                quantity = 0


            # Cantidad inválida
            if quantity <= 0:

                error = "SELECCIONA UNA CANTIDAD"


            else:

                # Buscar producto dentro del minimarket
                product = db.execute(
                    """
                    SELECT *
                    FROM products
                    WHERE id = ?
                    AND minimarket_id = ?
                    """,
                    (product_id, market_id)
                ).fetchone()


                # Producto inexistente
                if not product:

                    error = "SELECCIONA UN PRODUCTO"


                # Stock insuficiente
                elif quantity > product["stock"]:

                    error = "CANTIDAD NO DISPONIBLE"


                else:

                    # Guardar producto en carrito
                    cart[str(product_id)] = quantity

                    session["cart"] = cart

                    session["cart_market"] = market_id


    # Construir carrito
    cart_rows = []

    total = 0


    for product in products:

        quantity = cart.get(
            str(product["id"]),
            0
        )


        if quantity:

            subtotal = quantity * product["price"]

            total += subtotal

            cart_rows.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })


    # Limpiar carrito
    if request.args.get("clear_cart"):

        session.pop("cart", None)
        session.pop("cart_market", None)

        cart_rows = []
        total = 0


    return render_template(
        "reservation.html",
        market=market,
        products=products,
        cart_rows=cart_rows,
        total=total,
        error=error
    )


@app.post("/reservation/create")
@login_required
def create_reservation():
    db = get_db()
    market_id = request.form.get("market_id", type=int)
    cart = session.get("cart", {})
    if not cart or session.get("cart_market") != market_id:
        return redirect(url_for("reservation", market_id=market_id))
    reservation = db.execute(
        "INSERT INTO reservations(user_id,minimarket_id,created_at,status) VALUES(?,?,?,?)",
        (session["user_id"], market_id, datetime.now().strftime("%Y-%m-%d %H:%M"), "PENDIENTE"),
    )
    reservation_id = reservation.lastrowid
    for product_id, quantity in cart.items():
        product = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        if product:
            db.execute(
                "INSERT INTO reservation_items(reservation_id,product_id,quantity,price) VALUES(?,?,?,?)",
                (reservation_id, product["id"], int(quantity), product["price"]),
            )
    db.commit()
    session.pop("cart", None)
    session.pop("cart_market", None)
    session["last_reservation_id"] = reservation_id
    return redirect(url_for("reservation_success"))

@app.route("/reservation/success")
@login_required
def reservation_success():
    rid = session.get("last_reservation_id")
    reservation = get_reservation(rid) if rid else None
    return render_template("success.html", reservation=reservation)

def get_reservation(rid):
    db = get_db()
    r = db.execute("""
        SELECT r.*, m.name market_name, m.location
        FROM reservations r JOIN minimarkets m ON m.id=r.minimarket_id
        WHERE r.id=?
    """, (rid,)).fetchone()
    if not r:
        return None
    items = db.execute("""
        SELECT ri.*, p.name product_name
        FROM reservation_items ri JOIN products p ON p.id=ri.product_id
        WHERE ri.reservation_id=? ORDER BY ri.id
    """, (rid,)).fetchall()
    total = sum(i["quantity"] * i["price"] for i in items)
    return {"row": r, "items": items, "total": total}

@app.route("/reservations")
@login_required
def reservations():
    db = get_db()
    rows = db.execute("""
        SELECT r.*, m.name market_name, m.location
        FROM reservations r JOIN minimarkets m ON m.id=r.minimarket_id
        WHERE r.user_id=? ORDER BY r.id DESC
    """, (session["user_id"],)).fetchall()
    result = []
    for r in rows:
        detail = get_reservation(r["id"])
        result.append({"row": r, "items": detail["items"], "total": detail["total"]})
    return render_template("reservations.html", reservations=result)

@app.route("/reservations/<int:rid>")
@login_required
def reservation_detail(rid):
    detail = get_reservation(rid)
    if not detail or detail["row"]["user_id"] != session["user_id"]:
        return redirect(url_for("reservations"))
    return render_template("reservation_detail.html", reservation=detail)

@app.route("/reservations/<int:rid>/edit", methods=["GET", "POST"])
@login_required
def edit_reservation(rid):
    db = get_db()
    detail = get_reservation(rid)
    if not detail or detail["row"]["user_id"] != session["user_id"]:
        return redirect(url_for("reservations"))
    if detail["row"]["status"] != "PENDIENTE":
        return redirect(url_for("reservations"))

    products = db.execute(
        "SELECT * FROM products WHERE minimarket_id=? ORDER BY id",
        (detail["row"]["minimarket_id"],),
    ).fetchall()
    error = None

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity_raw = request.form.get("quantity", "").strip()
        if not product_id:
            error = "SELECCIONA UN PRODUCTO PORFAVOR"
        elif not quantity_raw:
            error = "INGRESA UNA CANTIDAD MAYOR A 0 PORFAVOR"
        else:
            try:
                quantity = int(quantity_raw)
            except ValueError:
                quantity = 0
            if quantity <= 0:
                error = "INGRESA UNA CANTIDAD MAYOR A 0 PORFAVOR"
            else:
                product = db.execute(
                    "SELECT * FROM products WHERE id=? AND minimarket_id=?",
                    (product_id, detail["row"]["minimarket_id"]),
                ).fetchone()
                if not product:
                    error = "SELECCIONA UN PRODUCTO PORFAVOR"
                elif quantity > product["stock"]:
                    error = "CANTIDAD NO DISPONIBLE"
                else:
                    db.execute("DELETE FROM reservation_items WHERE reservation_id=?", (rid,))
                    db.execute(
                        "INSERT INTO reservation_items(reservation_id,product_id,quantity,price) VALUES(?,?,?,?)",
                        (rid, product["id"], quantity, product["price"]),
                    )
                    db.commit()
                    return redirect(url_for("edit_saved"))

    detail = get_reservation(rid)
    return render_template("edit_reservation.html", reservation=detail, products=products, error=error)


@app.route("/reservations/<int:rid>/cancel", methods=["GET", "POST"])
@login_required
def cancel_reservation(rid):
    detail = get_reservation(rid)
    if not detail or detail["row"]["user_id"] != session["user_id"]:
        return redirect(url_for("reservations"))
    if request.method == "POST":
        if request.form.get("confirm") == "SI":
            get_db().execute(
                "UPDATE reservations SET status='CANCELADA' WHERE id=?",
                (rid,)
            )
            get_db().commit()
        return redirect(url_for("cancelled"))
    return render_template(
        "cancel.html",
        reservation=detail
    )


@app.route("/reservation/cancelled")
@login_required
def cancelled():
    return render_template("cancelled.html")

@app.route("/reservation/edit-saved")
@login_required
def edit_saved():
    return render_template("edit_saved.html")

# cositas del admin
@app.route("/admin")
@admin_required
def admin_panel():
    market = get_db().execute("SELECT * FROM minimarkets ORDER BY id LIMIT 1").fetchone()
    return render_template("admin_panel.html", market=market)

@app.route("/admin/reservations")
@admin_required
def admin_reservations():
    db = get_db()
    rows = db.execute("""
        SELECT r.*, u.username, m.name market_name
        FROM reservations r
        JOIN users u ON u.id=r.user_id
        JOIN minimarkets m ON m.id=r.minimarket_id
        ORDER BY r.id DESC
    """).fetchall()
    result = []
    for r in rows:
        d = get_reservation(r["id"])
        result.append({"row": r, "items": d["items"], "total": d["total"]})
    return render_template("admin_reservations.html", reservations=result)

@app.post("/admin/reservations/<int:rid>/<action>")
@admin_required
def admin_reservation_action(rid, action):
    status = {"accept": "ACEPTADA", "reject": "RECHAZADA"}.get(action)
    if status:
        get_db().execute("UPDATE reservations SET status=? WHERE id=?", (status, rid))
        get_db().commit()
    return redirect(url_for("admin_action_result", action=action))

@app.route("/admin/result/<action>")
@admin_required
def admin_action_result(action):
    return render_template("admin_result.html", action=action)

@app.route("/admin/products", methods=["GET", "POST"])
@admin_required
def admin_products():
    db = get_db()
    market_id = request.args.get("market_id", type=int) or 1
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("price_"):
                pid = int(key.split("_")[1])
                try:
                    price = float(value)
                    db.execute("UPDATE products SET price=? WHERE id=?", (price, pid))
                except ValueError:
                    pass
            if key.startswith("stock_"):
                pid = int(key.split("_")[1])
                try:
                    stock = max(0, int(value))
                    db.execute("UPDATE products SET stock=? WHERE id=?", (stock, pid))
                except ValueError:
                    pass
        db.commit()
        return redirect(url_for("products_saved"))
    market = db.execute("SELECT * FROM minimarkets WHERE id=?", (market_id,)).fetchone()
    products = db.execute("SELECT * FROM products WHERE minimarket_id=? ORDER BY id", (market_id,)).fetchall()
    return render_template("admin_products.html", market=market, products=products)

@app.route("/admin/products/saved")
@admin_required
def products_saved():
    return render_template("products_saved.html")

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
