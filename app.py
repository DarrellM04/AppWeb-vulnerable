from flask import Flask, request, render_template_string, redirect, session, make_response
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_123'  # Vulnerabilidad: clave débil en código

# Crear base de datos vulnerable
def init_db():
    conn = sqlite3.connect('vulnerable.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'usuario', 'pass123', 'user')")
    conn.commit()
    conn.close()

init_db()

# Página principal
HOME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aplicación Vulnerable - Lab de Seguridad</title>
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
        <h1>🔓 Laboratorio de Seguridad Web</h1>
        <div class="warning">
            <strong>⚠️ ADVERTENCIA:</strong> Esta aplicación contiene vulnerabilidades intencionales 
            para propósitos educativos. NO usar en producción.
        </div>
        
        <h2>Vulnerabilidades Incluidas:</h2>
        <div class="vuln-list">
            <ul>
                <li><strong>SQL Injection</strong> - Login sin validación</li>
                <li><strong>XSS (Cross-Site Scripting)</strong> - Búsqueda sin sanitización</li>
                <li><strong>Command Injection</strong> - Ejecución de comandos</li>
                <li><strong>Path Traversal</strong> - Lectura de archivos</li>
                <li><strong>Credenciales débiles</strong> - admin/admin123</li>
                <li><strong>Session Fixation</strong> - Gestión insegura de sesiones</li>
                <li><strong>Información sensible expuesta</strong> - Debug habilitado</li>
            </ul>
        </div>
        
        <h2>Páginas de Prueba:</h2>
        <a href="/login">🔑 Login (SQL Injection)</a>
        <a href="/search">🔍 Búsqueda (XSS)</a>
        <a href="/ping">📡 Ping Tool (Command Injection)</a>
        <a href="/file">📄 Lector de Archivos (Path Traversal)</a>
        <a href="/info">ℹ️ Información del Sistema</a>
        <a href="/admin">👨‍💼 Panel de Administración</a>
    </div>
</body>
</html>
'''

# Login vulnerable a SQL Injection
LOGIN_PAGE = '''
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
        <h2>🔑 Login</h2>
        <div class="hint">
            💡 Prueba SQL Injection: admin' OR '1'='1
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

# Búsqueda vulnerable a XSS
SEARCH_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Búsqueda</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto; }
        input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer; }
        .hint { background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔍 Búsqueda</h2>
        <div class="hint">
            💡 Prueba XSS: &lt;script&gt;alert('XSS')&lt;/script&gt;
        </div>
        <form method="GET">
            <input type="text" name="q" placeholder="Buscar..." value="{{ query }}">
            <button type="submit">Buscar</button>
        </form>
        {% if query %}
        <h3>Resultados para: {{ query|safe }}</h3>
        <p>No se encontraron resultados.</p>
        {% endif %}
        <a href="/">← Volver</a>
    </div>
</body>
</html>
'''

# Ping tool vulnerable a Command Injection
PING_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ping Tool</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto; }
        input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #dc3545; color: white; border: none; cursor: pointer; }
        .hint { background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; }
        .output { background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📡 Ping Tool</h2>
        <div class="hint">
            💡 Prueba Command Injection: 127.0.0.1; cat /etc/passwd
        </div>
        <form method="POST">
            <input type="text" name="host" placeholder="IP o Hostname" value="{{ host }}">
            <button type="submit">Ping</button>
        </form>
        {% if output %}
        <div class="output">{{ output }}</div>
        {% endif %}
        <a href="/">← Volver</a>
    </div>
</body>
</html>
'''

# Lector de archivos vulnerable a Path Traversal
FILE_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Lector de Archivos</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto; }
        input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #ffc107; color: black; border: none; cursor: pointer; }
        .hint { background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; }
        .content { background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📄 Lector de Archivos</h2>
        <div class="hint">
            💡 Prueba Path Traversal: ../../../../etc/passwd
        </div>
        <form method="GET">
            <input type="text" name="file" placeholder="Nombre del archivo" value="{{ filename }}">
            <button type="submit">Leer</button>
        </form>
        {% if content %}
        <div class="content">{{ content }}</div>
        {% endif %}
        <a href="/">← Volver</a>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return HOME_PAGE

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vulnerable a SQL Injection - NO usar en producción
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
    
    return render_template_string(LOGIN_PAGE, message=message)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Vulnerable a XSS - NO sanitiza entrada
    return render_template_string(SEARCH_PAGE, query=query)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    output = ''
    host = ''
    if request.method == 'POST':
        host = request.form.get('host', '')
        # Vulnerable a Command Injection - NO usar en producción
        try:
            command = f'ping -c 2 {host}'
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5).decode()
        except Exception as e:
            output = str(e)
    
    return render_template_string(PING_PAGE, output=output, host=host)

@app.route('/file')
def read_file():
    filename = request.args.get('file', '')
    content = ''
    if filename:
        # Vulnerable a Path Traversal - NO usar en producción
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            content = f'Error: {str(e)}'
    
    return render_template_string(FILE_PAGE, filename=filename, content=content)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    
    return f'''
    <h1>Panel de Administración</h1>
    <p>Bienvenido {session['user']} - Role: {session['role']}</p>
    <p>Cookie de sesión: {request.cookies.get('session')}</p>
    <a href="/">Volver</a>
    '''

@app.route('/info')
def info():
    # Información sensible expuesta
    return f'''
    <h1>Información del Sistema</h1>
    <pre>
    Python Version: {os.sys.version}
    Current Path: {os.getcwd()}
    Environment Variables: {dict(os.environ)}
    </pre>
    <a href="/">Volver</a>
    '''

if __name__ == '__main__':
    # Debug habilitado - Vulnerabilidad
    app.run(host='0.0.0.0', port=5000, debug=True)