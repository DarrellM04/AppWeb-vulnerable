from flask import Flask, request, render_template_string, redirect, session, jsonify
import sqlite3
import os
import subprocess
import logging
from datetime import datetime

app = Flask(__name__)

# VULNERABILIDAD 1: Secret Key Hardcoded y Débil
app.secret_key = 'clave_super_secreta_123'

# VULNERABILIDAD 2: Configuración Insegura
app.config['DEBUG'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# LOGS CON INFORMACIÓN SENSIBLE (VULNERABLE)
logging.basicConfig(
    filename='app_security.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# INICIALIZACIÓN DE BASE DE DATOS
def init_database():
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT,
                  rol TEXT DEFAULT 'empleado',
                  departamento TEXT,
                  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS documentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  titulo TEXT NOT NULL,
                  contenido TEXT,
                  clasificacion TEXT NOT NULL,
                  propietario_id INTEGER,
                  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  fecha_retencion DATE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS informacion_financiera
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  empleado_id INTEGER,
                  numero_cuenta TEXT,
                  salario REAL,
                  numero_seguro_social TEXT,
                  tarjeta_corporativa TEXT,
                  cvv TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS logs_sistema
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  evento TEXT,
                  usuario TEXT,
                  ip_address TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
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

def registrar_log(evento, usuario='Anonimo'):
    ip = request.remote_addr
    logging.info(f"Evento: {evento} | Usuario: {usuario} | IP: {ip}")
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs_sistema (evento, usuario, ip_address) VALUES (?, ?, ?)", 
              (evento, usuario, ip))
    conn.commit()
    conn.close()

# PÁGINA PRINCIPAL
@app.route('/')
def home():
    registrar_log("Acceso a pagina principal")
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Sistema de Gestión Empresarial</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                   min-height: 100vh; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.3); overflow: hidden; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                     padding: 30px; text-align: center; }
            .nav { background: #f8f9fa; padding: 15px 30px; border-bottom: 2px solid #dee2e6; }
            .nav a { display: inline-block; padding: 10px 20px; margin: 5px; background: #007bff;
                    color: white; text-decoration: none; border-radius: 5px; transition: all 0.3s; }
            .nav a:hover { background: #0056b3; transform: translateY(-2px); }
            .content { padding: 30px; }
            .info-box { background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px;
                       margin: 20px 0; border-radius: 4px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #667eea; color: white; }
            .footer { background: #343a40; color: white; padding: 20px; text-align: center; }
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
                    Esta aplicación contiene vulnerabilidades intencionales para auditoría.
                </div>
                
                <h2>🎯 Componentes del Sistema</h2>
                <table>
                    <tr><th>Módulo</th><th>Descripción</th><th>Estado</th></tr>
                    <tr><td>Autenticación</td><td>Sistema de login y registro</td><td>✅ Activo</td></tr>
                    <tr><td>Gestión Documental</td><td>Documentos clasificados</td><td>✅ Activo</td></tr>
                    <tr><td>Base de Datos</td><td>SQLite con información empresarial</td><td>✅ Activo</td></tr>
                    <tr><td>Sistema de Logs</td><td>Registro de eventos</td><td>✅ Activo</td></tr>
                    <tr><td>Herramientas Red</td><td>Utilidades de diagnóstico</td><td>✅ Activo</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Sistema de Gestión Empresarial v1.0 | Flask Development Server</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

# LOGIN - SQL INJECTION
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    tipo_mensaje = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABILIDAD CRÍTICA: SQL Injection
        query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
        
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
                
                mensaje = f'Bienvenido {usuario[1]}! Rol: {usuario[4]}'
                tipo_mensaje = 'success'
                
                return redirect('/admin')
            else:
                mensaje = 'Credenciales incorrectas'
                tipo_mensaje = 'error'
                
        except Exception as e:
            mensaje = f'Error en la base de datos: {str(e)}'
            tipo_mensaje = 'error'
            logging.error(f"Error SQL: {str(e)}")
        
        conn.close()
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
            .login-box {{ background: white; padding: 40px; border-radius: 10px; width: 400px; }}
            h2 {{ text-align: center; color: #333; margin-bottom: 30px; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd;
                    border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none;
                     border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #5568d3; }}
            .message {{ padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center; }}
            .error {{ background: #f8d7da; color: #721c24; }}
            .success {{ background: #d4edda; color: #155724; }}
            .hint {{ background: #d1ecf1; padding: 10px; margin: 15px 0; border-radius: 5px; font-size: 12px; }}
            a {{ color: #667eea; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🔐 Iniciar Sesión</h2>
            <div class="hint">💡 Usuario: admin | Contraseña: admin123</div>
            {"<div class='message " + tipo_mensaje + "'>" + mensaje + "</div>" if mensaje else ""}
            <form method="POST">
                <input type="text" name="username" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/">← Volver</a> | <a href="/registro">Registrarse</a>
            </p>
        </div>
    </body>
    </html>
    '''
    return html

# REGISTRO
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        conn = sqlite3.connect('empresa.db')
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO usuarios (username, password, email) VALUES (?, ?, ?)",
                      (username, password, email))
            conn.commit()
            registrar_log(f"Nuevo usuario registrado: {username}", username)
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Usuario ya existe <br><a href='/registro'>Volver</a>"
        finally:
            conn.close()
    
    return '''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Registro</title>
    <style>
        body { font-family: Arial; padding: 40px; background: #f5f5f5; }
        .box { background: white; padding: 30px; border-radius: 10px; max-width: 400px; margin: auto; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #28a745; color: white; border: none; cursor: pointer; }
    </style></head>
    <body>
        <div class="box">
            <h2>Registro de Usuario</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <input type="email" name="email" placeholder="Email" required>
                <button type="submit">Registrarse</button>
            </form>
            <a href="/">Volver</a>
        </div>
    </body></html>
    '''

# BÚSQUEDA - XSS
@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '')
    registrar_log(f"Busqueda realizada: {query}")
    
    # VULNERABILIDAD: XSS
    html = f'''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Búsqueda</title>
    <style>
        body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
        .search-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: auto; }}
        input {{ width: 70%; padding: 12px; }}
        button {{ padding: 12px 30px; background: #667eea; color: white; border: none; cursor: pointer; }}
        .hint {{ background: #d1ecf1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
    </style></head>
    <body>
        <div class="search-box">
            <h2>🔍 Búsqueda de Documentos</h2>
            <div class="hint">💡 Prueba buscar algo...</div>
            <form method="GET">
                <input type="text" name="q" value="{query}" placeholder="Buscar...">
                <button type="submit">Buscar</button>
            </form>
            <h3>Resultados para: {query}</h3>
            <p>No se encontraron documentos.</p>
            <a href="/">← Volver</a>
        </div>
    </body></html>
    '''
    return html

# HERRAMIENTAS - COMMAND INJECTION
@app.route('/herramientas', methods=['GET', 'POST'])
def herramientas():
    output = ''
    host = ''
    
    if request.method == 'POST':
        host = request.form.get('host', '')
        registrar_log(f"Ping ejecutado a: {host}")
        
        try:
            command = f'ping -c 3 {host}'
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5).decode()
        except Exception as e:
            output = str(e)
    
    return f'''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Herramientas</title>
    <style>
        body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
        .tool-box {{ background: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: auto; }}
        input {{ width: 70%; padding: 12px; }}
        button {{ padding: 12px 30px; background: #dc3545; color: white; border: none; cursor: pointer; }}
        .output {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px;
                  font-family: monospace; white-space: pre-wrap; }}
    </style></head>
    <body>
        <div class="tool-box">
            <h2>🛠️ Herramientas de Red</h2>
            <form method="POST">
                <input type="text" name="host" value="{host}" placeholder="IP o Hostname">
                <button type="submit">Ejecutar Ping</button>
            </form>
            {f'<div class="output">{output}</div>' if output else ''}
            <a href="/">← Volver</a>
        </div>
    </body></html>
    '''

# DOCUMENTOS - IDOR
@app.route('/documentos')
@app.route('/documentos/<int:doc_id>')
def documentos(doc_id=None):
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    
    if doc_id:
        c.execute("SELECT * FROM documentos WHERE id=?", (doc_id,))
        doc = c.fetchone()
        
        if doc:
            registrar_log(f"Acceso a documento ID: {doc_id}")
            return f'''
            <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Documento</title>
            <style>body{{font-family:Arial;padding:40px;background:#f5f5f5;}}
            .doc{{background:white;padding:30px;border-radius:10px;max-width:800px;margin:auto;}}</style>
            </head><body><div class="doc">
            <h2>{doc[1]}</h2>
            <p><strong>Clasificación:</strong> {doc[3]}</p>
            <p><strong>Contenido:</strong><br>{doc[2]}</p>
            <p><strong>Retención hasta:</strong> {doc[5] or 'Indefinida'}</p>
            <a href="/documentos">← Volver</a>
            </div></body></html>
            '''
    
    c.execute("SELECT id, titulo, clasificacion FROM documentos")
    docs = c.fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Documentos</title>
    <style>body{font-family:Arial;padding:40px;background:#f5f5f5;}
    table{width:100%;border-collapse:collapse;background:white;}
    th,td{padding:12px;text-align:left;border:1px solid #ddd;}
    th{background:#667eea;color:white;}</style></head><body>
    <h2>📚 Documentos del Sistema</h2>
    <table><tr><th>ID</th><th>Título</th><th>Clasificación</th><th>Acción</th></tr>'''
    
    for doc in docs:
        html += f'<tr><td>{doc[0]}</td><td>{doc[1]}</td><td>{doc[2]}</td>'
        html += f'<td><a href="/documentos/{doc[0]}">Ver</a></td></tr>'
    
    html += '</table><br><a href="/">← Volver</a></body></html>'
    return html

# ADMIN PANEL
@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect('/login')
    
    username = session.get('username')
    rol = session.get('rol')
    registrar_log(f"Acceso al panel admin", username)
    
    return f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin Panel</title>
    <style>body{{font-family:Arial;padding:40px;background:#f5f5f5;}}
    .panel{{background:white;padding:30px;border-radius:10px;max-width:900px;margin:auto;}}
    .card{{background:#f8f9fa;padding:20px;margin:15px 0;border-radius:8px;}}
    a{{display:inline-block;padding:10px 20px;background:#007bff;color:white;
       text-decoration:none;border-radius:5px;margin:5px;}}</style>
    </head><body><div class="panel">
    <h1>👨‍💼 Panel de Administración</h1>
    <div class="card">
        <strong>Usuario:</strong> {username}<br>
        <strong>Rol:</strong> {rol}<br>
        <strong>ID Sesión:</strong> {session.get('user_id')}
    </div>
    <h3>🔗 Accesos</h3>
    <a href="/ver-usuarios">Ver Usuarios</a>
    <a href="/ver-logs">Ver Logs</a>
    <a href="/ver-financiero">Info Financiera</a>
    <a href="/backup-db">Backup BD</a>
    <a href="/logout">Cerrar Sesión</a>
    <br><br><a href="/">← Inicio</a>
    </div></body></html>
    '''

# VER USUARIOS - EXPOSICIÓN DE CONTRASEÑAS
@app.route('/ver-usuarios')
def ver_usuarios():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password, email, rol FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Usuarios</title>
    <style>body{font-family:Arial;padding:40px;background:#f5f5f5;}
    table{width:100%;border-collapse:collapse;background:white;}
    th,td{padding:12px;border:1px solid #ddd;}
    th{background:#dc3545;color:white;}</style></head><body>
    <h2>👥 Lista de Usuarios (CONTRASEÑAS VISIBLES)</h2>
    <table><tr><th>ID</th><th>Usuario</th><th>Contraseña</th><th>Email</th><th>Rol</th></tr>'''
    
    for u in usuarios:
        html += f'<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[4]}</td></tr>'
    
    html += '</table><br><a href="/admin">← Volver</a></body></html>'
    return html

# VER INFORMACIÓN FINANCIERA
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
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Financiero</title>
    <style>body{font-family:Arial;padding:40px;background:#f5f5f5;}
    table{width:100%;border-collapse:collapse;background:white;}
    th,td{padding:12px;border:1px solid #ddd;font-size:14px;}
    th{background:#ffc107;color:#000;}</style></head><body>
    <h2>💰 Información Financiera (DATOS SIN CIFRAR)</h2>
    <table><tr><th>Usuario</th><th>Cuenta</th><th>Salario</th><th>SSN</th><th>Tarjeta</th><th>CVV</th></tr>'''
    
    for d in datos:
        html += f'<tr><td>{d[0]}</td><td>{d[1]}</td><td>${d[2]:,.2f}</td><td>{d[3]}</td><td>{d[4]}</td><td>{d[5]}</td></tr>'
    
    html += '</table><br><a href="/admin">← Volver</a></body></html>'
    return html

# VER LOGS
@app.route('/ver-logs')
def ver_logs():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('empresa.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 50")
    logs = c.fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Logs</title>
    <style>body{font-family:Arial;padding:40px;background:#f5f5f5;}
    table{width:100%;border-collapse:collapse;background:white;font-size:12px;}
    th,td{padding:8px;border:1px solid #ddd;}
    th{background:#28a745;color:white;}</style></head><body>
    <h2>📋 Logs del Sistema</h2>
    <table><tr><th>ID</th><th>Evento</th><th>Usuario</th><th>IP</th><th>Timestamp</th></tr>'''
    
    for log in logs:
        html += f'<tr><td>{log[0]}</td><td>{log[1]}</td><td>{log[2]}</td><td>{log[3]}</td><td>{log[4]}</td></tr>'
    
    html += '</table><br><a href="/admin">← Volver</a></body></html>'
    return html

# BACKUP DE BASE DE DATOS
@app.route('/backup-db')
def backup_db():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('empresa.db')
    backup = '\n'.join(conn.iterdump())
    conn.close()
    
    registrar_log("Descarga de backup de BD", session.get('username'))
    
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Backup</title>
    <style>body{{font-family:Arial;padding:40px;background:#f5f5f5;}}
    .backup{{background:white;padding:30px;border-radius:10px;}}
    pre{{background:#f8f9fa;padding:15px;border-radius:5px;overflow-x:auto;}}</style>
    </head><body><div class="backup">
    <h2>💾 Backup de Base de Datos</h2>
    <pre>{backup[:2000]}... (truncado)</pre>
    <a href="/admin">← Volver</a>
    </div></body></html>'''

# INFORMACIÓN DEL SISTEMA
@app.route('/sistema')
def sistema():
    import sys
    import platform
    
    registrar_log("Acceso a informacion del sistema")
    
    info = f'''
    Python Version: {sys.version}
    Platform: {platform.platform()}
    Processor: {platform.processor()}
    Working Directory: {os.getcwd()}
    Flask Debug: {app.config['DEBUG']}
    Secret Key: {app.secret_key}
    '''
    
    # VULNERABILIDAD: Expone información sensible del sistema
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Info Sistema</title>
    <style>body{{font-family:Arial;padding:40px;background:#f5f5f5;}}
    .info{{background:white;padding:30px;border-radius:10px;max-width:900px;margin:auto;}}
    pre{{background:#f8f9fa;padding:15px;border-radius:5px;overflow-x:auto;}}</style>
    </head><body><div class="info">
    <h2>ℹ️ Información del Sistema</h2>
    <pre>{info}</pre>
    <h3>Variables de Entorno (primeras 5):</h3>
    <pre>{dict(list(os.environ.items())[:5])}</pre>
    <a href="/">← Volver</a>
    </div></body></html>'''

# LOGOUT
@app.route('/logout')
def logout():
    username = session.get('username', 'Anonimo')
    registrar_log(f"Logout", username)
    session.clear()
    return redirect('/')

# ENDPOINT PARA ROBOTS.TXT
@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin
Disallow: /backup-db
Disallow: /ver-financiero
Disallow: /sistema
'''

# ENDPOINT QUE SIMULA ARCHIVO DE CONFIGURACIÓN
@app.route('/config.bak')
def config_bak():
    return '''# Configuración de la aplicación
SECRET_KEY = 'clave_super_secreta_123'
DATABASE = 'empresa.db'
DEBUG = True
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'
'''

# ENDPOINT DE SALUD (HEALTHCHECK)
@app.route('/health')
def health():
    return jsonify({
        'status': 'running',
        'database': 'empresa.db',
        'debug_mode': app.config['DEBUG'],
        'session_active': 'username' in session
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando aplicación vulnerable para auditoría")
    print("=" * 60)
    print(f"📍 Servidor: http://0.0.0.0:5000")
    print(f"🗄️  Base de datos: empresa.db")
    print(f"📝 Logs: app_security.log")
    print("=" * 60)
    print("⚠️  ADVERTENCIA: Esta app contiene vulnerabilidades")
    print("    Solo usar en entornos controlados de laboratorio")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)