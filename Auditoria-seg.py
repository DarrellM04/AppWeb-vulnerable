from flask import Flask, request, render_template_string, redirect, session, jsonify
import sqlite3
import os
import subprocess
import logging
from datetime import datetime
import hashlib

app = Flask(__name__)

# ============================================
# VULNERABILIDAD 1: Secret Key Hardcoded y Débil
# ============================================
app.secret_key = 'clave_super_secreta_123'

# ============================================
# VULNERABILIDAD 2: Configuración Insegura
# ============================================
app.config['DEBUG'] = True  # Debug en producción
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas - muy largo

# ============================================
# LOGS CON INFORMACIÓN SENSIBLE (VULNERABLE)
# ============================================
logging.basicConfig(
    filename='app_security.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================
def init_database():
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    
    # Tabla de usuarios - VULNERABILIDAD: Contraseñas en texto plano
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT,
                  rol TEXT DEFAULT 'empleado',
                  departamento TEXT,
                  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabla de documentos con clasificación
    c.execute('''CREATE TABLE IF NOT EXISTS documentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  titulo TEXT NOT NULL,
                  contenido TEXT,
                  clasificacion TEXT NOT NULL,
                  propietario_id INTEGER,
                  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  fecha_retencion DATE)''')
    
    # Tabla de información financiera - VULNERABILIDAD: Datos sensibles sin cifrar
    c.execute('''CREATE TABLE IF NOT EXISTS informacion_financiera
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  empleado_id INTEGER,
                  numero_cuenta TEXT,
                  salario REAL,
                  numero_seguro_social TEXT,
                  tarjeta_corporativa TEXT,
                  cvv TEXT)''')
    
    # Tabla de logs de sistema
    c.execute('''CREATE TABLE IF NOT EXISTS logs_sistema
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  evento TEXT,
                  usuario TEXT,
                  ip_address TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insertar usuarios de prueba
    usuarios_prueba = [
        ('admin', 'admin123', 'admin@empresa.com', 'administrador', 'TI'),
        ('jperez', 'Password123', 'jperez@empresa.com', 'empleado', 'Ventas'),
        ('mgarcia', '12345', 'mgarcia@empresa.com', 'empleado', 'RRHH'),
        ('lmartinez', 'qwerty', 'lmartinez@empresa.com', 'gerente', 'Finanzas')
    ]
    
    for usuario in usuarios_prueba:
        try:
            c.execute("INSERT INTO usuarios (username, password, email, rol, departamento) VALUES (?, ?, ?, ?, ?)", usuario)
        except sqlite3.IntegrityError:
            pass
    
    # Insertar documentos clasificados
    documentos_prueba = [
        ('Manual de Bienvenida', 'Información general de la empresa', 'PUBLICO', 1, None),
        ('Plan Estratégico 2025', 'Objetivos y estrategias confidenciales', 'CONFIDENCIAL', 1, '2027-12-31'),
        ('Contraseñas de Sistemas', 'Prod_DB: admin/SuperSecret2024! | AWS: AKIA...', 'SECRETO', 1, '2025-12-31'),
        ('Nómina Ejecutivos', 'Salarios y bonos de directivos', 'CONFIDENCIAL', 4, '2030-12-31'),
        ('Auditoría Interna 2024', 'Hallazgos de seguridad y fraude detectado', 'SECRETO', 1, '2035-12-31')
    ]
    
    for doc in documentos_prueba:
        try:
            c.execute("INSERT INTO documentos (titulo, contenido, clasificacion, propietario_id, fecha_retencion) VALUES (?, ?, ?, ?, ?)", doc)
        except:
            pass
    
    # Insertar información financiera sensible
    info_financiera = [
        (1, '1234567890', 85000.00, '123-45-6789', '4532-1234-5678-9010', '123'),
        (2, '0987654321', 45000.00, '987-65-4321', '5425-2334-3010-9876', '456'),
        (3, '1122334455', 52000.00, '111-22-3333', '3782-822463-10005', '789'),
        (4, '5544332211', 120000.00, '444-55-6666', '6011-1111-1111-1117', '321')
    ]
    
    for info in info_financiera:
        try:
            c.execute("INSERT INTO informacion_financiera (empleado_id, numero_cuenta, salario, numero_seguro_social, tarjeta_corporativa, cvv) VALUES (?, ?, ?, ?, ?, ?)", info)
        except:
            pass
    
    conn.commit()
    conn.close()
    logging.info("Base de datos inicializada correctamente")

init_database()

# ============================================
# FUNCIÓN PARA REGISTRAR LOGS
# ============================================
def registrar_log(evento, usuario='Anónimo'):
    ip = request.remote_addr
    logging.info(f"Evento: {evento} | Usuario: {usuario} | IP: {ip}")
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs_sistema (evento, usuario, ip_address) VALUES (?, ?, ?)", 
              (evento, usuario, ip))
    conn.commit()
    conn.close()

# ============================================
# PÁGINA PRINCIPAL
# ============================================
HOME_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Gestión Empresarial</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 2px solid #dee2e6;
        }
        .nav a {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .nav a:hover { background: #0056b3; transform: translateY(-2px); }
        .content { padding: 30px; }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            background: #343a40;
            color: white;
            padding: 20px;
            text-align: center;
        }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #667eea; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Sistema de Gestión Empresarial</h1>
            <p>Portal Corporativo - Versión 1.0</p>
        </div>
        
        <div class="nav">
            <a href="/login">🔐 Login</a>
            <a href="/registro">📝 Registro</a>
            <a href="/documentos">📄 Documentos</a>
            <a href="/buscar">🔍 Búsqueda</a>
            <a href="/herramientas">🛠️ Herramientas</a>
            <a href="/admin">👨‍💼 Admin</a>
            <a href="/sistema">ℹ️ Info Sistema</a>
        </div>
        
        <div class="content">
            <div class="info-box">
                <strong>📊 Sistema de Auditoría de Seguridad</strong><br>
                Esta aplicación está diseñada para demostrar vulnerabilidades comunes en aplicaciones web.
            </div>
            
            <h2>🎯 Componentes del Sistema</h2>
            <table>
                <tr>
                    <th>Módulo</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                </tr>
                <tr>
                    <td>Autenticación</td>
                    <td>Sistema de login y registro de usuarios</td>
                    <td>✅ Activo</td>
                </tr>
                <tr>
                    <td>Gestión Documental</td>
                    <td>Almacenamiento de documentos clasificados</td>
                    <td>✅ Activo</td>
                </tr>
                <tr>
                    <td>Base de Datos</td>
                    <td>SQLite con información empresarial</td>
                    <td>✅ Activo</td>
                </tr>
                <tr>
                    <td>Sistema de Logs</td>
                    <td>Registro de eventos del sistema</td>
                    <td>✅ Activo</td>
                </tr>
                <tr>
                    <td>Herramientas Red</td>
                    <td>Utilidades de diagnóstico</td>
                    <td>✅ Activo</td>
                </tr>
            </table>
            
            <div class="warning-box">
                <strong>⚠️ Aviso Importante:</strong> Este sistema contiene datos sensibles. 
                Acceso restringido a personal autorizado.
            </div>
        </div>
        
        <div class="footer">
            <p>Sistema de Gestión Empresarial v1.0 | Flask Development Server</p>
            <p>{{ server_info }}</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    registrar_log("Acceso a página principal")
    return render_template_string(HOME_HTML, server_info=f"Python/{os.sys.version.split()[0]} Flask/3.0")

# ============================================
# VULNERABILIDAD 3: SQL INJECTION EN LOGIN
# ============================================
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - Sistema Empresarial</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
                     width: 400px; }
        h2 { text-align: center; color: #333; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; 
                border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #5568d3; }
        .message { padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .hint { background: #d1ecf1; padding: 10px; margin: 15px 0; border-radius: 5px; font-size: 12px; }
        a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 Iniciar Sesión</h2>
        
        <div class="hint">
            💡 Usuarios de prueba: admin/admin123, jperez/Password123
        </div>
        
        {% if mensaje %}
        <div class="message {{ tipo_mensaje }}">{{ mensaje }}</div>
        {% endif %}
        
        <form method="POST">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        
        <p style="text-align: center; margin-top: 20px;">
            <a href="/">← Volver al inicio</a> | 
            <a href="/registro">Registrarse</a>
        </p>
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    tipo_mensaje = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABILIDAD CRÍTICA: SQL Injection
        # NO usar en producción - concatenación directa de SQL
        query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
        
        # Log vulnerable - registra contraseña
        logging.warning(f"Intento de login - Usuario: {username} Password: {password}")
        registrar_log(f"Intento de login: {username}", username)
        
        conn = sqlite3.connect('empresa.db')
        c = conn.cursor()
        
        try:
            c.execute(query)
            usuario = c.fetchone()
            
            if usuario:
                session['user_id'] = usuario[0]
                session['username'] = usuario[1]
                session['rol'] = usuario[4]
                
                logging.info(f"Login exitoso: {username}")
                registrar_log(f"Login exitoso", username)
                
                mensaje = f'¡Bienvenido {usuario[1]}! Rol: {usuario[4]}'
                tipo_mensaje = 'success'
                
                return redirect('/admin')
            else:
                mensaje = 'Credenciales incorrectas'
                tipo_mensaje = 'error'
                
        except Exception as e:
            # Expone errores SQL - Información sensible
            mensaje = f'Error en la base de datos: {str(e)}'
            tipo_mensaje = 'error'
            logging.error(f"Error SQL: {str(e)}")
        
        conn.close()
    
    return render_template_string(LOGIN_HTML, mensaje=mensaje, tipo_mensaje=tipo_mensaje)

# ============================================
# REGISTRO DE USUARIOS
# ============================================
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # VULNERABILIDAD: Sin validación de contraseñas débiles
        # VULNERABILIDAD: Contraseña guardada en texto plano
        
        conn = sqlite3.connect('empresa.db')
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO usuarios (username, password, email) VALUES (?, ?, ?)",
                      (username, password, email))
            conn.commit()
            registrar_log(f"Nuevo usuario registrado: {username}", username)
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Usuario ya existe"
        finally:
            conn.close()
    
    return '''
    <h2>Registro</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Usuario" required><br>
        <input type="password" name="password" placeholder="Contraseña" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <button type="submit">Registrarse</button>
    </form>
    <a href="/">Volver</a>
    '''

# ============================================
# VULNERABILIDAD 4: XSS en Búsqueda
# ============================================
@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '')
    
    # VULNERABILIDAD: XSS - No sanitiza entrada del usuario
    registrar_log(f"Búsqueda realizada: {query}")
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Búsqueda</title>
        <style>
            body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
            .search-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: auto; }}
            input {{ width: 70%; padding: 12px; font-size: 16px; }}
            button {{ padding: 12px 30px; background: #667eea; color: white; border: none; cursor: pointer; }}
            .hint {{ background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="search-box">
            <h2>🔍 Búsqueda de Documentos</h2>
            <div class="hint">💡 Prueba buscar: "test", "admin", etc.</div>
            <form method="GET">
                <input type="text" name="q" value="{query}" placeholder="Buscar documentos...">
                <button type="submit">Buscar</button>
            </form>
            
            <h3>Resultados para: {query}</h3>
            <p>No se encontraron documentos que coincidan con la búsqueda.</p>
            <a href="/">← Volver</a>
        </div>
    </body>
    </html>
    '''
    
    return html

# ============================================
# VULNERABILIDAD 5: Command Injection
# ============================================
@app.route('/herramientas', methods=['GET', 'POST'])
def herramientas():
    output = ''
    host = ''
    
    if request.method == 'POST':
        host = request.form.get('host', '')
        
        # VULNERABILIDAD CRÍTICA: Command Injection
        registrar_log(f"Ping ejecutado a: {host}")
        
        try:
            command = f'ping -c 3 {host}'
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5).decode()
        except Exception as e:
            output = str(e)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Herramientas de Red</title>
        <style>
            body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
            .tool-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: auto; }}
            input {{ width: 70%; padding: 12px; }}
            button {{ padding: 12px 30px; background: #dc3545; color: white; border: none; cursor: pointer; }}
            .output {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; 
                      font-family: monospace; white-space: pre-wrap; }}
            .hint {{ background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="tool-box">
            <h2>🛠️ Herramientas de Diagnóstico de Red</h2>
            <div class="hint">💡 Prueba: 127.0.0.1, google.com</div>
            <form method="POST">
                <input type="text" name="host" value="{host}" placeholder="IP o Hostname">
                <button type="submit">Ejecutar Ping</button>
            </form>
            {f'<div class="output">{output}</div>' if output else ''}
            <a href="/">← Volver</a>
        </div>
    </body>
    </html>
    '''

# ============================================
# VULNERABILIDAD 6: IDOR - Acceso a Documentos
# ============================================
@app.route('/documentos')
@app.route('/documentos/<int:doc_id>')
def documentos(doc_id=None):
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    
    if doc_id:
        # VULNERABILIDAD: No verifica si el usuario tiene permiso
        c.execute("SELECT * FROM documentos WHERE id=?", (doc_id,))
        doc = c.fetchone()
        
        if doc:
            registrar_log(f"Acceso a documento ID: {doc_id}")
            return f'''
            <h2>{doc[1]}</h2>
            <p><strong>Clasificación:</strong> {doc[3]}</p>
            <p><strong>Contenido:</strong><br>{doc[2]}</p>
            <p><strong>Retención hasta:</strong> {doc[5] or 'Indefinida'}</p>
            <a href="/documentos">← Volver a documentos</a>
            '''
    
    c.execute("SELECT id, titulo, clasificacion FROM documentos")
    docs = c.fetchall()
    conn.close()
    
    html = '<h2>📚 Documentos del Sistema</h2>'
    html += '<table border="1" style="width:100%; border-collapse:collapse;">'
    html += '<tr><th>ID</th><th>Título</th><th>Clasificación</th><th>Acción</th></tr>'
    
    for doc in docs:
        html += f'<tr><td>{doc[0]}</td><td>{doc[1]}</td><td>{doc[2]}</td>'
        html += f'<td><a href="/documentos/{doc[0]}">Ver</a></td></tr>'
    
    html += '</table><br><a href="/">← Volver</a>'
    return html

# ============================================
# PANEL DE ADMINISTRACIÓN
# ============================================
@app.route('/admin')
def admin():
    # VULNERABILIDAD: Control de acceso débil
    if 'username' not in session:
        return redirect('/login')
    
    username = session.get('username')
    rol = session.get('rol')
    
    registrar_log(f"Acceso al panel admin", username)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Panel de Administración</title>
        <style>
            body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
            .admin-panel {{ background: white; padding: 30px; border-radius: 10px; max-width: 900px; margin: auto; }}
            .card {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
            a {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; 
                 text-decoration: none; border-radius: 5px; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="admin-panel">
            <h1>👨‍💼 Panel de Administración</h1>
            <div class="card">
                <strong>Usuario:</strong> {username}<br>
                <strong>Rol:</strong> {rol}<br>
                <strong>Sesión:</strong> {session.get('user_id')}
            </div>
            
            <h3>🔗 Accesos Rápidos</h3>
            <a href="/ver-usuarios">Ver Usuarios</a>
            <a href="/ver-logs">Ver Logs</a>
            <a href="/ver-financiero">Info Financiera</a>
            <a href="/backup">Descargar Backup BD</a>
            <a href="/logout">Cerrar Sesión</a>
            <br><br>
            <a href="/">← Volver al inicio</a>
        </div>
    </body>
    </html>
    '''

# ============================================
# VULNERABILIDAD 7: Exposición de Datos Sensibles
# ============================================
@app.route('/ver-usuarios')
def ver_usuarios():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password, email, rol FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    
    # VULNERABILIDAD: Expone contraseñas en texto plano
    html = '<h2>👥 Lista de Usuarios</h2>'
    html += '<table border="1" style="width:100%; border-collapse:collapse;">'
    html += '<tr><th>ID</th><th>Usuario</th><th>Contraseña</th><th>Email</th><th>Rol</th></tr>'
    
    for u in usuarios:
        html += f'<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[4]}</td></tr>'
    
    html += '</table><br><a href="/admin">← Volver</a>'
    return html

@app.route('/ver-financiero')
def ver_financiero():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("""
        SELECT u.username, f.numero_cuenta, f.salario, f.numero_seguro_social, 
               f.tarjeta_corporativa, f.cvv
        FROM informacion_financiera f
        JOIN usuarios u ON f.empleado_id = u.id
    """)
    datos = c.fetchall()
    conn.close()
    
    # VULNERABILIDAD: Datos financieros sin cifrar
    html = '<h2>💰 Información Financiera</h2>'
    html += '<table border="1" style="width:100%; border-collapse:collapse;">'
    html += '<tr><th>Usuario</th><th>Cuenta</th><th>Salario</th><th>SSN</th><th>Tarjeta</th><th>CVV</th></tr>'
    
    for d in datos:
        html += f'<tr><td>{d[0]}</td><td>{d[1]}</td><td>${d[2]:,.2f}</td><td>{d[3]}</td><td>{d[4]}</td><td>{d[5]}</td></tr>'
    
    html += '</table>