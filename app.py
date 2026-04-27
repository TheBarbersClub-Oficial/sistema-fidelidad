from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# CONFIGURACIÓN DE TU BASE DE DATOS
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Admin123", # <--- CAMBIA ESTO
        database="barberia_db"
    )

@app.route('/')
def home():
    return render_template('registro.html')

# ESTA RUTA GUARDA AL CLIENTE NUEVO
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Insertamos al cliente con su primer sello (1)
    cursor.execute("INSERT INTO clientes (nombre, telefono, sellos) VALUES (%s, %s, 0)", (nombre, telefono))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('confirmacion.html', nombre=nombre, sellos=0)
# ESTA RUTA ES PARA TI (EL ADMINISTRADOR)
@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    todos_los_clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', clientes=todos_los_clientes)

# ESTA RUTA SUMA SELLOS CUANDO LE DAS CLIC AL BOTÓN
@app.route('/sumar_sello/<int:id>')
def sumar_sello(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET sellos = sellos + 1 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')
@app.route('/restar_sello/<int:id>')
def restar_sello(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Resta un sello pero solo si tiene más de 0
    cursor.execute("UPDATE clientes SET sellos = sellos - 1 WHERE id = %s AND sellos > 0", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

@app.route('/canjear_premio/<int:id>')
def canjear_premio(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Esta es la orden que pone los sellos en 0 de nuevo
    cursor.execute("UPDATE clientes SET sellos = 0 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    # Te regresa al panel de administrador
    return redirect('/admin')
@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if request.method == 'POST':
        telefono = request.form['telefono']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Buscamos al cliente por su número de teléfono
        cursor.execute("SELECT * FROM clientes WHERE telefono = %s", (telefono,))
        cliente = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if cliente:
            # Si lo encuentra, lo manda a ver sus sellos
            return render_template('confirmacion.html', nombre=cliente['nombre'], sellos=cliente['sellos'])
        else:
            # Si no existe el número
            return "<h1>Cliente no encontrado</h1><br><a href='/consulta'>Intentar de nuevo</a>"
    
    return render_template('consulta.html')
if __name__ == '__main__':
    app.run(debug=True)