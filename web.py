from flask import Flask, render_template_string, request, redirect, session, jsonify, abort
import sqlite3
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clavesecreta2025'

# Base de datos SQLite
DATABASE = 'sistema_academico.db'

def login_required(f):
    """Requiere que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Requiere roles específicos para acceder"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario' not in session:
                return redirect('/login')
            
            if session.get('rol') not in roles:
                return render_template_string('''
                <!DOCTYPE html>
                <html><head><meta charset="UTF-8"><title>Acceso Denegado</title>
                <style>
                    body{font-family:Arial;background:#f5f5f5;display:flex;align-items:center;
                         justify-content:center;min-height:100vh;margin:0;}
                    .error-box{background:white;padding:50px;border-radius:10px;text-align:center;
                              box-shadow:0 10px 30px rgba(0,0,0,0.2);max-width:500px;}
                    .error-icon{font-size:5em;color:#dc3545;margin-bottom:20px;}
                    h1{color:#dc3545;margin-bottom:15px;}
                    p{color:#666;margin:15px 0;line-height:1.6;}
                    .info{background:#f8f9fa;padding:15px;border-radius:5px;margin:20px 0;}
                    a{display:inline-block;padding:12px 30px;background:#667eea;color:white;
                      text-decoration:none;border-radius:5px;margin-top:20px;transition:background 0.3s;}
                    a:hover{background:#5568d3;}
                </style></head>
                <body>
                    <div class="error-box">
                        <div class="error-icon">🚫</div>
                        <h1>Acceso Denegado</h1>
                        <p>No tienes permisos para acceder a esta sección del sistema.</p>
                        <div class="info">
                            <strong>Tu rol actual:</strong> {{ rol }}<br>
                            <strong>Roles permitidos:</strong> {{ roles_requeridos }}
                        </div>
                        <p>Contacta al administrador si crees que deberías tener acceso.</p>
                        <a href="/panel">← Volver al Panel</a>
                    </div>
                </body></html>
                ''', rol=session.get('rol', 'Ninguno').upper(), 
                     roles_requeridos=', '.join([r.upper() for r in roles]))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def registrar_auditoria(accion, detalles=''):
    """Registra acciones importantes en la tabla de auditoría"""
    try:
        conn = sqlite3.connect(DATABASE)
        usuario = session.get('usuario', 'anonimo')
        rol = session.get('rol', 'ninguno')
        ip = request.remote_addr
        
        conn.execute("""
            INSERT INTO auditoria (usuario, rol, accion, detalles, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario, rol, accion, detalles, ip))
        conn.commit()
        conn.close()
    except:
        pass

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Tabla de estudiantes
    c.execute('''CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        fecha_nacimiento DATE,
        grado TEXT,
        seccion TEXT,
        email TEXT,
        telefono TEXT,
        direccion TEXT,
        nombre_acudiente TEXT,
        telefono_acudiente TEXT,
        fecha_matricula DATE DEFAULT CURRENT_DATE,
        estado TEXT DEFAULT 'activo'
    )''')
    
    # Tabla de docentes
    c.execute('''CREATE TABLE IF NOT EXISTS docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        telefono TEXT,
        especialidad TEXT,
        fecha_ingreso DATE,
        usuario TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT DEFAULT 'docente',
        estado TEXT DEFAULT 'activo'
    )''')
    
    # Tabla de materias
    c.execute('''CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        grado TEXT,
        intensidad_horaria INTEGER,
        descripcion TEXT
    )''')
    
    # Tabla de notas
    c.execute('''CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        docente_id INTEGER NOT NULL,
        periodo TEXT,
        nota_periodo1 REAL,
        nota_periodo2 REAL,
        nota_periodo3 REAL,
        nota_periodo4 REAL,
        nota_final REAL,
        observaciones TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
        FOREIGN KEY (materia_id) REFERENCES materias(id),
        FOREIGN KEY (docente_id) REFERENCES docentes(id)
    )''')
    
    # Tabla de auditoría - NUEVA
    c.execute('''CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        rol TEXT,
        accion TEXT,
        detalles TEXT,
        ip_address TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insertar datos de prueba
    try:
        # Docentes con roles específicos
        docentes = [
            ('1234567890', 'María', 'González Pérez', 'mgonzalez@colegio.edu', '555-0101', 'Matemáticas', '2020-01-15', 'mgonzalez', 'docente123', 'docente'),
            ('0987654321', 'Juan', 'Ramírez López', 'jramirez@colegio.edu', '555-0102', 'Español', '2019-03-20', 'jramirez', 'docente456', 'docente'),
            ('1122334455', 'Ana', 'Martínez Silva', 'amartinez@colegio.edu', '555-0103', 'Ciencias', '2021-07-10', 'coordinador', 'coord789', 'coordinador'),
            ('5544332211', 'Carlos', 'Rodríguez Gómez', 'crodriguez@colegio.edu', '555-0104', 'Sistemas', '2018-09-01', 'admin', 'admin1234', 'admin')
        ]
        
        for doc in docentes:
            try:
                c.execute("INSERT INTO docentes (cedula, nombre, apellidos, email, telefono, especialidad, fecha_ingreso, usuario, password, rol) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", doc)
            except sqlite3.IntegrityError:
                pass
        
        # Materias
        materias = [
            ('MAT-6', 'Matemáticas', 'Sexto', 5, 'Álgebra y geometría básica'),
            ('ESP-6', 'Español', 'Sexto', 4, 'Literatura y gramática'),
            ('CIE-6', 'Ciencias Naturales', 'Sexto', 4, 'Biología y química'),
            ('SOC-6', 'Ciencias Sociales', 'Sexto', 3, 'Historia y geografía'),
            ('ING-6', 'Inglés', 'Sexto', 3, 'Nivel intermedio'),
            ('TEC-6', 'Tecnología', 'Sexto', 2, 'Informática básica'),
            ('MAT-7', 'Matemáticas', 'Séptimo', 5, 'Álgebra avanzada'),
            ('ESP-7', 'Español', 'Séptimo', 4, 'Literatura universal')
        ]
        
        for mat in materias:
            try:
                c.execute("INSERT INTO materias (codigo, nombre, grado, intensidad_horaria, descripcion) VALUES (?, ?, ?, ?, ?)", mat)
            except sqlite3.IntegrityError:
                pass
        
        # Estudiantes
        estudiantes = [
            ('1001234567', 'Pedro', 'Sánchez Ruiz', '2010-03-15', 'Noveno', 'A', 'psanchez@estudiante.edu', '555-1001', 'Calle 10 #20-30', 'Rosa Ruiz', '555-2001'),
            ('1001234568', 'Laura', 'García Méndez', '2010-05-22', 'Sexto', 'A', 'lgarcia@estudiante.edu', '555-1002', 'Calle 5 #15-25', 'Luis García', '555-2002'),
            ('1001234569', 'Diego', 'Torres Vega', '2009-11-08', 'Séptimo', 'A', 'dtorres@estudiante.edu', '555-1003', 'Avenida 8 #12-18', 'Carmen Vega', '555-2003'),
            ('1001234570', 'Sofía', 'Morales Castro', '2010-07-30', 'Sexto', 'B', 'smorales@estudiante.edu', '555-1004', 'Calle 20 #30-40', 'Roberto Morales', '555-2004'),
            ('1001234571', 'Andrés', 'Jiménez Rojas', '2009-09-12', 'Séptimo', 'A', 'ajimenez@estudiante.edu', '555-1005', 'Calle 15 #25-35', 'Patricia Rojas', '555-2005'),
            ('1001234572', 'Valentina', 'López Herrera', '2010-02-18', 'Sexto', 'A', 'vlopez@estudiante.edu', '555-1006', 'Calle 30 #40-50', 'María Herrera', '555-2006'),
            ('1001234573', 'Santiago', 'Pérez Navarro', '2010-08-25', 'Sexto', 'B', 'sperez@estudiante.edu', '555-1007', 'Calle 25 #35-45', 'Jorge Pérez', '555-2007'),
            ('1001234574', 'Isabella', 'Ramírez Silva', '2009-12-03', 'Séptimo', 'A', 'iramirez@estudiante.edu', '555-1008', 'Avenida 12 #22-32', 'Ana Silva', '555-2008')
        ]
        
        for est in estudiantes:
            try:
                c.execute("INSERT INTO estudiantes (cedula, nombre, apellidos, fecha_nacimiento, grado, seccion, email, telefono, direccion, nombre_acudiente, telefono_acudiente) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", est)
            except sqlite3.IntegrityError:
                pass
        
        # Notas
        notas = [
            (1, 1, 1, '2025-1', 4.5, 4.2, 4.8, 4.6, 4.5, 'Excelente desempeño'),
            (1, 2, 2, '2025-1', 3.8, 4.0, 4.1, 3.9, 3.9, 'Buen trabajo'),
            (2, 1, 1, '2025-1', 5.0, 4.9, 4.8, 5.0, 4.9, 'Sobresaliente'),
            (2, 2, 2, '2025-1', 4.5, 4.6, 4.7, 4.5, 4.6, 'Muy bien'),
            (3, 7, 1, '2025-1', 4.0, 3.8, 4.2, 4.1, 4.0, 'Buen rendimiento'),
            (4, 1, 1, '2025-1', 3.5, 3.7, 3.6, 3.8, 3.6, 'Regular'),
            (5, 7, 1, '2025-1', 4.8, 4.7, 4.9, 4.8, 4.8, 'Excelente')
        ]
        
        for nota in notas:
            try:
                c.execute("INSERT INTO notas (estudiante_id, materia_id, docente_id, periodo, nota_periodo1, nota_periodo2, nota_periodo3, nota_periodo4, nota_final, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", nota)
            except:
                pass
        
    except Exception as e:
        print(f"Error insertando datos: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# Inicializar BD al arrancar
init_database()

# PÁGINA PRINCIPAL (Pública - sin login requerido)
HOME_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Centro Educativo San Carlo de Acutis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .logo-section {
            text-align: center;
            padding: 20px;
        }
        .logo-section h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .logo-section p {
            color: #666;
            font-size: 1.1em;
        }
        .nav-bar {
            background: #5568d3;
            padding: 15px;
            text-align: center;
        }
        .nav-bar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 5px;
            transition: background 0.3s;
            display: inline-block;
        }
        .nav-bar a:hover {
            background: #667eea;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 20px;
        }
        .security-notice {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .security-notice h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        .footer {
            background: white;
            padding: 20px;
            text-align: center;
            margin-top: 30px;
            border-top: 3px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <h1>🎓 Centro Educativo San Carlo de Acutis</h1>
            <p>Sistema de Gestión Académica 2025 - Versión Segura con RBAC</p>
        </div>
        <div class="nav-bar">
            <a href="/">🏠 Inicio</a>
            <a href="/login">🔐 Ingresar</a>
        </div>
    </div>
    
    <div class="container">
        <div class="security-notice">
            <h3>🔒 Sistema Protegido con Control de Acceso</h3>
            <p><strong>Este sistema implementa autenticación y autorización basada en roles (RBAC).</strong></p>
            <p>Solo usuarios autorizados pueden acceder a información sensible según su rol:</p>
            <ul style="margin-top:10px;margin-left:20px;">
                <li><strong>🔴 Admin:</strong> Acceso total al sistema, BD y configuración</li>
                <li><strong>🟠 Coordinador:</strong> Puede ver estudiantes, docentes y todas las notas</li>
                <li><strong>🟢 Docente:</strong> Solo puede ver sus propias notas y estudiantes asignados</li>
            </ul>
            <p style="margin-top:10px;">Para acceder, debe iniciar sesión con credenciales válidas.</p>
        </div>
    </div>
    
    <div class="footer">
        <p>&copy; 2025 Centro Educativo San Carlo de Acutis | Sistema Académico v3.0 Seguro</p>
        <p>🔐 Protegido con autenticación y control de acceso basado en roles (RBAC)</p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    registrar_auditoria('Visita a página principal')
    return HOME_HTML

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    tipo = ''
    
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        conn = get_db_connection()
        docente = conn.execute("SELECT * FROM docentes WHERE usuario=? AND password=?", (usuario, password)).fetchone()
        conn.close()
        
        if docente:
            session['user_id'] = docente['id']
            session['usuario'] = docente['usuario']
            session['nombre'] = f"{docente['nombre']} {docente['apellidos']}"
            session['rol'] = docente['rol']
            
            registrar_auditoria('Login exitoso', f"Rol: {docente['rol']}")
            
            return redirect('/panel')
        else:
            mensaje = 'Usuario o contraseña incorrectos'
            tipo = 'error'
            registrar_auditoria('Intento de login fallido', f"Usuario: {usuario}")
    
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Login Seguro</title>
    <style>
        body {font-family:Arial;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              display:flex;align-items:center;justify-content:center;min-height:100vh;}
        .login-box {background:white;padding:40px;border-radius:10px;max-width:450px;width:100%;
                    box-shadow:0 10px 40px rgba(0,0,0,0.3);}
        h2 {text-align:center;color:#333;margin-bottom:30px;}
        input {width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;}
        button {width:100%;padding:12px;background:#667eea;color:white;border:none;
               border-radius:5px;cursor:pointer;font-size:16px;}
        button:hover {background:#5568d3;}
        .message {padding:10px;margin:10px 0;border-radius:5px;text-align:center;}
        .error {background:#f8d7da;color:#721c24;border:1px solid #f5c6cb;}
        .hint {background:#d1ecf1;padding:15px;margin:15px 0;border-radius:5px;font-size:13px;}
        .roles {background:#f8f9fa;padding:15px;margin:15px 0;border-radius:5px;font-size:12px;}
    </style></head>
    <body>
        <div class="login-box">
            <h2>🔐 Acceso Seguro al Sistema</h2>
            <div class="hint">
                <strong>💡 Usuarios de Prueba:</strong><br>
                • admin/admin1234 (Administrador)<br>
                • coordinador/coord789 (Coordinador)<br>
                • mgonzalez/docente123 (Docente)
            </div>
            <div class="roles">
                <strong>Permisos por Rol:</strong><br>
                🔴 <strong>Admin:</strong> Acceso total (Estudiantes, Docentes, Notas, BD, Auditoría)<br>
                🟠 <strong>Coordinador:</strong> Estudiantes, Docentes, Todas las Notas<br>
                🟢 <strong>Docente:</strong> Solo sus notas y estudiantes
            </div>
            {% if mensaje %}
            <div class="message {{ tipo }}">{{ mensaje }}</div>
            {% endif %}
            <form method="POST">
                <input type="text" name="usuario" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar Seguro</button>
            </form>
            <p style="text-align:center;margin-top:20px;">
                <a href="/" style="color:#667eea;">← Volver al inicio</a>
            </p>
        </div>
    </body></html>
    ''', mensaje=mensaje, tipo=tipo)

# PANEL DOCENTE (Requiere login, opciones según rol)
@app.route('/panel')
@login_required
def panel():
    registrar_auditoria('Acceso al panel')
    
    rol = session.get('rol')
    
    # Opciones según rol
    if rol == 'admin':
        opciones = '''
            <div class="menu-item"><h3>👨‍🎓</h3><a href="/estudiantes">Estudiantes</a><span class="badge">Admin</span></div>
            <div class="menu-item"><h3>👨‍🏫</h3><a href="/docentes">Docentes</a><span class="badge">Admin/Coord</span></div>
            <div class="menu-item"><h3>📊</h3><a href="/notas">Todas las Notas</a><span class="badge">Admin/Coord</span></div>
            <div class="menu-item"><h3>💾</h3><a href="/backup">Respaldos</a><span class="badge">Admin</span></div>
            <div class="menu-item"><h3>🗄️</h3><a href="/ver-base-datos">Ver BD</a><span class="badge">Admin</span></div>
            <div class="menu-item"><h3>📋</h3><a href="/auditoria">Auditoría</a><span class="badge">Admin</span></div>
        '''
    elif rol == 'coordinador':
        opciones = '''
            <div class="menu-item"><h3>👨‍🎓</h3><a href="/estudiantes">Estudiantes</a></div>
            <div class="menu-item"><h3>👨‍🏫</h3><a href="/docentes">Docentes</a></div>
            <div class="menu-item"><h3>📊</h3><a href="/notas">Todas las Notas</a></div>
            <div class="menu-item"><h3>📄</h3><a href="/reportes">Reportes</a></div>
        '''
    else:  # docente
        opciones = '''
            <div class="menu-item"><h3>📊</h3><a href="/mis-notas">Mis Notas</a></div>
            <div class="menu-item"><h3>👨‍🎓</h3><a href="/mis-estudiantes">Mis Estudiantes</a></div>
            <div class="menu-item"><h3>📄</h3><a href="/reportes">Reportes</a></div>
        '''
    
    return f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Panel</title>
    <style>
        body {{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .panel {{background:white;padding:30px;border-radius:10px;max-width:1000px;margin:auto;}}
        .welcome {{background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color:white;padding:20px;border-radius:8px;margin-bottom:20px;}}
        .role-badge {{display:inline-block;padding:5px 15px;background:rgba(255,255,255,0.2);
                     border-radius:20px;font-size:0.9em;margin-left:10px;}}
        .security-info {{background:#d4edda;border-left:4px solid #28a745;padding:15px;
                        margin:20px 0;border-radius:5px;}}
        .menu-grid {{display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
                    gap:15px;margin-top:20px;}}
        .menu-item {{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;
                    border-left:4px solid #667eea;transition:all 0.3s;position:relative;}}
        .menu-item:hover {{transform:translateY(-3px);box-shadow:0 5px 15px rgba(0,0,0,0.1);}}
        .menu-item .badge {{position:absolute;top:10px;right:10px;background:#ffc107;color:#000;
                          padding:2px 8px;border-radius:10px;font-size:0.7em;}}
        a {{color:#667eea;text-decoration:none;font-weight:bold;}}
    </style></head>
    <body>
        <div class="panel">
            <div class="welcome">
                <h1>👨‍🏫 Bienvenido, {session['nombre']}</h1>
                <p>Usuario: {session['usuario']} 
                <span class="role-badge">🔐 {session['rol'].upper()}</span></p>
            </div>
            
            <div class="security-info">
                <strong>🛡️ Acceso Controlado por Roles</strong><br>
                Tu nivel de acceso está limitado según tu rol. Solo puedes ver información autorizada para tu perfil.
            </div>
            
            <h2>📋 Panel de Control</h2>
            <div class="menu-grid">
                {opciones}
                <div class="menu-item"><h3>🚪</h3><a href="/logout">Cerrar Sesión</a></div>
            </div>
        </div>
    </body></html>
    '''

# ESTUDIANTES - Solo Admin y Coordinador
@app.route('/estudiantes')
@role_required('admin', 'coordinador')
def estudiantes():
    registrar_auditoria('Acceso a lista de estudiantes')
    
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes WHERE estado='activo' ORDER BY apellidos").fetchall()
    conn.close()
    
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Estudiantes</title>
    <style>
        body{{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .container{{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}}
        .security-badge{{background:#28a745;color:white;padding:10px 20px;border-radius:20px;
                        display:inline-block;margin-bottom:20px;}}
        table{{width:100%;border-collapse:collapse;margin:20px 0;}}
        th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd;}}
        th{{background:#667eea;color:white;}}
        tr:hover{{background:#f8f9fa;}}
    </style></head>
    <body>
        <div class="container">
            <span class="security-badge">🔐 Acceso: {session.get('rol').upper()}</span>
            <h2>👨‍🎓 Lista de Estudiantes Activos</h2>
            <table>
                <tr><th>Cédula</th><th>Nombre Completo</th><th>Grado</th><th>Sección</th>
                <th>Email</th><th>Acudiente</th><th>Teléfono</th></tr>'''
    
    for est in estudiantes:
        html += f'''<tr>
            <td>{est['cedula']}</td>
            <td>{est['nombre']} {est['apellidos']}</td>
            <td>{est['grado']}</td>
            <td>{est['seccion']}</td>
            <td>{est['email