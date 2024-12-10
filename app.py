from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Necesario para manejar sesiones

# Simulación de base de datos
productos = []
movimientos = []

# Página de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        # Credenciales básicas
        if usuario == "admin" and contraseña == "password":
            session["usuario"] = usuario
            return redirect(url_for("gestion_productos"))
        else:
            return "Credenciales incorrectas", 401
    return render_template("login.html")

# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# Gestión de productos
@app.route("/productos")
def gestion_productos():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", productos=productos)

@app.route("/agregar", methods=["POST"])
def agregar_producto():
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Obtener datos del formulario
    codigo = request.form.get("codigo")
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    stock = request.form.get("stock")
    precio = request.form.get("precio")
    proveedor = request.form.get("proveedor")
    descripcion = request.form.get("descripcion")

    # Validar datos y agregar a la lista
    if codigo and nombre and stock and precio:
        producto = {
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "stock": int(stock),
            "precio": float(precio),
            "proveedor": proveedor,
            "descripcion": descripcion,
        }
        productos.append(producto)
        return redirect(url_for("gestion_productos"))
    else:
        return "Error: Faltan campos obligatorios", 400

@app.route("/eliminar/<codigo>")
def eliminar_producto(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    global productos
    productos = [p for p in productos if p["codigo"] != codigo]
    return redirect(url_for("gestion_productos"))

@app.route("/editar/<codigo>")
def editar_producto(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    producto = next((p for p in productos if p["codigo"] == codigo), None)
    if producto:
        return render_template("editar.html", producto=producto)
    else:
        return "Producto no encontrado", 404

@app.route("/actualizar/<codigo>", methods=["POST"])
def actualizar_producto(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    for producto in productos:
        if producto["codigo"] == codigo:
            producto["nombre"] = request.form.get("nombre")
            producto["categoria"] = request.form.get("categoria")
            producto["stock"] = int(request.form.get("stock"))
            producto["precio"] = float(request.form.get("precio"))
            producto["proveedor"] = request.form.get("proveedor")
            producto["descripcion"] = request.form.get("descripcion")
            break
    return redirect(url_for("gestion_productos"))

# Gestión de movimientos
@app.route("/movements", methods=["GET", "POST"])
def manage_movements():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Recibir datos del formulario
        product_id = request.form.get("product_id")
        movement_type = request.form.get("movement_type")
        quantity = int(request.form.get("quantity"))

        # Validar producto existente
        producto = next((p for p in productos if p["codigo"] == product_id), None)
        if not producto:
            return "Producto no encontrado", 404

        # Actualizar stock según el movimiento
        if movement_type == "entrada":
            producto["stock"] += quantity
        elif movement_type == "salida":
            if producto["stock"] >= quantity:
                producto["stock"] -= quantity
            else:
                return "Error: Stock insuficiente", 400

        # Registrar el movimiento
        movimiento = {
            "product_name": producto["nombre"],
            "movement_type": movement_type,
            "quantity": quantity,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        movimientos.append(movimiento)
        return redirect(url_for("manage_movements"))

    return render_template("movements.html", products=productos, movements=movimientos)

if __name__ == "__main__":
    app.run(debug=True)
