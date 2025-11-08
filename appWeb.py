from flask import Flask, request, render_template_string, redirect, session, make_response
import sqlite3
import os

app = Flask(__name__)

# Base de datos vulnerable
def crear_bd():
    conn = sqlite3.connect("BDvulnerable.db")
    sql = conn.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                (id interger primary key, username varchar(50) not null,
                pass varchar(50) not null, role TEXT not null)
                ''')
    sql.execute("insert or ignore INTO usuarios Values ('1','admin', 'admin1234', 'admin')")
    sql.execute("insert or ignore INTO usuarios Values ('1','admin', 'admin1234', 'admin')")

crear_bd()

#pagina de inicio 
Pagina_principal= '''
<!DOCTYPE html>
<html>
<head>
    <title>Aplicación Vulnerable - Lab de Seguridad Informatica</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: auto; }
        h1 { color: #d9534f; }
        .warning { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }
        .vuln-list { background: #f8f9fa; padding: 20px; border-radius: 5px; }
        a { color: #007bff; text-decoration: none; display: block; margin: 10px 0; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1> Laboratorio de Seguridad Web</h1>
        <div class="warning">
            <strong> ADVERTENCIA:</strong> Esta aplicación contiene vulnerabilidades intencionales 
            para propósitos educativos.
        </div>
                
        <h2>Páginas de Prueba:</h2>
        <a href="/login"> Inicio de Sesion</a>
    </div>
</body>
</html>
'''

Login= '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 400px; margin: auto; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .hint { background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h2> Login</h2>
        <div class="hint">
            Prueba SQL Injection: admin' OR '1'='1
        </div>
        <form method="POST">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        <p>{{ message }}</p>
        <a href="/">← Volver</a>
    </div>
</body>
</html>

'''

@app.route('/')
def home():
    return Pagina_principal

@app.route('/login')
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vulnerable a SQL Injection
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        conn = sqlite3.connect('vulnerable.db')
        c = conn.cursor()
        try:
            c.execute(query)
            user = c.fetchone()
            if user:
                session['user'] = user[1]
                session['role'] = user[3]
                message = f'¡Bienvenido {user[1]}! <a href="/admin">Ir al panel</a>'
            else:
                message = 'Credenciales incorrectas'
        except Exception as e:
            message = f'Error SQL: {str(e)}'
        conn.close()
    
    return render_template_string(Login, message=message)    


if __name__ == '__main__':
    # Debug habilitado - Vulnerabilidad
    app.run(host='0.0.0.0', port=5000, debug=True)
