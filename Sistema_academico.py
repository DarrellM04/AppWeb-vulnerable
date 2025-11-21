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
                    a{display:inline-block;padding:12px 30px;background:#667eea;color:white;
                      text-decoration:none;border-radius:5px;margin-top:20px;transition:background 0.3s;}
                    a:hover{background:#5568d3;}
                </style></head>
                <body>
                    <div class="error-box">
                        <div class="error-icon">🚫</div>
                        <h1>Acceso Denegado</h1>
                        <p>No tienes permisos para acceder a esta sección del sistema.</p>
                        <p>Si crees que esto es un error, contacta al administrador del sistema.</p>
                        <a href="/panel">← Volver al Panel</a>
                    </div>
                </body></html>
                ''')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # -------------------------------------------------------------
    # TABLA: ESTUDIANTES (CORREGIDA)
    # -------------------------------------------------------------
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
        usuario TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        estado TEXT DEFAULT 'activo'
    )''')

    # -------------------------------------------------------------
    # TABLA: DOCENTES
    # -------------------------------------------------------------
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
        rol TEXT,
        estado TEXT DEFAULT 'activo'
    )''')

    # -------------------------------------------------------------
    # TABLA: MATERIAS
    # -------------------------------------------------------------
    c.execute('''CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        grado TEXT,
        intensidad_horaria INTEGER,
        descripcion TEXT
    )''')

    # -------------------------------------------------------------
    # TABLA: NOTAS
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # TABLA: AUDITORIA
    # -------------------------------------------------------------
    c.execute('''CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        rol TEXT,
        accion TEXT,
        detalles TEXT,
        ip_address TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # -------------------------------------------------------------
    # INSERTAR DOCENTES
    # -------------------------------------------------------------
    try:
        docentes = [
            ('1234567890', 'María', 'González Pérez', 'mgonzalez@colegio.edu', '555-0101', 'Matemáticas', '2020-01-15', 'mgonzalez', 'docente123', 'docente'),
            ('0987654321', 'Juan', 'Ramírez López', 'jramirez@colegio.edu', '555-0102', 'Español', '2019-03-20', 'jramirez', 'docente456', 'docente'),
            ('1122334455', 'Ana', 'Martínez Silva', 'amartinez@colegio.edu', '555-0103', 'Ciencias', '2021-07-10', 'amartinez', 'docente789', 'coordinador'),
            ('5544332211', 'Carlos', 'Rodríguez Gómez', 'crodriguez@colegio.edu', '555-0104', 'Sistemas', '2018-09-01', 'admin', 'admin1234', 'admin')
        ]

        for doc in docentes:
            try:
                c.execute("""
                    INSERT INTO docentes 
                    (cedula, nombre, apellidos, email, telefono, especialidad, fecha_ingreso, usuario, password, rol)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, doc)
            except sqlite3.IntegrityError:
                pass

    except Exception as e:
        print("Error insertando docentes:", e)

    # -------------------------------------------------------------
    # INSERTAR MATERIAS
    # -------------------------------------------------------------
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
            c.execute("""
                INSERT INTO materias (codigo, nombre, grado, intensidad_horaria, descripcion)
                VALUES (?, ?, ?, ?, ?)
            """, mat)
        except sqlite3.IntegrityError:
            pass

    # -------------------------------------------------------------
    # INSERTAR ESTUDIANTES (CORREGIDO)
    # -------------------------------------------------------------
    estudiantes = [
        ('estudiante1', 'qwerty', '1001234567', 'Pedro', 'Sánchez Ruiz', '2010-03-15', 'Noveno', 'A', 'psanchez@estudiante.edu', '555-1001', 'Calle 10 #20-30', 'Rosa Ruiz', '555-2001'),
        ('estudiante2', 'qwerty', '1001234568', 'Laura', 'García Méndez', '2010-05-22', 'Sexto', 'A', 'lgarcia@estudiante.edu', '555-1002', 'Calle 5 #15-25', 'Luis García', '555-2002'),
        ('estudiante3', 'qwerty', '1001234569', 'Diego', 'Torres Vega', '2009-11-08', 'Séptimo', 'A', 'dtorres@estudiante.edu', '555-1003', 'Avenida 8 #12-18', 'Carmen Vega', '555-2003'),
        ('estudiante4', 'qwerty', '1001234570', 'Sofía', 'Morales Castro', '2010-07-30', 'Sexto', 'B', 'smorales@estudiante.edu', '555-1004', 'Calle 20 #30-40', 'Roberto Morales', '555-2004'),
        ('estudiante5', 'qwerty', '1001234571', 'Andrés', 'Jiménez Rojas', '2009-09-12', 'Séptimo', 'A', 'ajimenez@estudiante.edu', '555-1005', 'Calle 15 #25-35', 'Patricia Rojas', '555-2005'),
        ('estudiante6', 'qwerty', '1001234572', 'Valentina', 'López Herrera', '2010-02-18', 'Sexto', 'A', 'vlopez@estudiante.edu', '555-1006', 'Calle 30 #40-50', 'María Herrera', '555-2006'),
        ('estudiante7', 'qwerty', '1001234573', 'Santiago', 'Pérez Navarro', '2010-08-25', 'Sexto', 'B', 'sperez@estudiante.edu', '555-1007', 'Calle 25 #35-45', 'Jorge Pérez', '555-2007'),
        ('estudiante8', 'qwerty', '1001234574', 'Isabella', 'Ramírez Silva', '2009-12-03', 'Séptimo', 'A', 'iramirez@estudiante.edu', '555-1008', 'Avenida 12 #22-32', 'Ana Silva', '555-2008')
    ]

    for est in estudiantes:
        try:
            c.execute("""
                INSERT INTO estudiantes 
                (usuario, password, cedula, nombre, apellidos, fecha_nacimiento, grado, seccion,
                 email, telefono, direccion, nombre_acudiente, telefono_acudiente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, est)
        except sqlite3.IntegrityError:
            pass

    # -------------------------------------------------------------
    # INSERTAR NOTAS
    # -------------------------------------------------------------
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
            c.execute("""
                INSERT INTO notas 
                (estudiante_id, materia_id, docente_id, periodo, nota_periodo1,
                 nota_periodo2, nota_periodo3, nota_periodo4, nota_final, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, nota)
        except:
            pass

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# Inicializar BD al arrancar
init_database()

# PÁGINA PRINCIPAL
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
            <h1> Centro Educativo San Carlo de Acutis</h1>
            <p>Sistema de Gestión Académica 2025</p>
        </div>
        <div class="nav-bar">
            <a href="/"> Inicio</a>
            <a href="/login"> Ingresar</a>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2025 Centro Educativo San Carlo de Acutis | Sistema Académico </p>
    </div>
</body>
</html>
'''

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

@app.route('/')
def home():
    registrar_auditoria('Visita a página principal')
    return HOME_HTML

# LOGIN - Para docentes Y estudiantes
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    tipo = ''
    
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        conn = get_db_connection()
        
        # Intentar login como docente
        docente = conn.execute("SELECT * FROM docentes WHERE usuario=? AND password=?", (usuario, password)).fetchone()
        
        if docente:
            session['user_id'] = docente['id']
            session['usuario'] = docente['usuario']
            session['nombre'] = f"{docente['nombre']} {docente['apellidos']}"
            session['rol'] = docente['rol']
            
            registrar_auditoria('Login exitoso')
            conn.close()
            return redirect('/panel')
        
        # Intentar login como estudiante
        estudiante = conn.execute("SELECT * FROM estudiantes WHERE usuario=? AND password=?", (usuario, password)).fetchone()
        
        if estudiante:
            session['user_id'] = estudiante['id']
            session['usuario'] = estudiante['usuario']
            session['nombre'] = f"{estudiante['nombre']} {estudiante['apellidos']}"
            session['rol'] = 'estudiante'
            session['tipo_usuario'] = 'estudiante'
            
            registrar_auditoria('Login exitoso')
            conn.close()
            return redirect('/panel')
        
        conn.close()
        mensaje = 'Usuario o contraseña incorrectos'
        tipo = 'error'
        registrar_auditoria('Intento de login fallido', f"Usuario: {usuario}")
    
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Login</title>
    <style>
        body {font-family:Arial;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              display:flex;align-items:center;justify-content:center;min-height:100vh;}
        .login-box {background:white;padding:40px;border-radius:10px;max-width:400px;width:100%;
                    box-shadow:0 10px 40px rgba(0,0,0,0.3);}
        h2 {text-align:center;color:#333;margin-bottom:30px;}
        input {width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;}
        button {width:100%;padding:12px;background:#667eea;color:white;border:none;
               border-radius:5px;cursor:pointer;font-size:16px;}
        button:hover {background:#5568d3;}
        .message {padding:10px;margin:10px 0;border-radius:5px;text-align:center;}
        .error {background:#f8d7da;color:#721c24;}
        .info {background:#d1ecf1;padding:10px;margin:15px 0;border-radius:5px;font-size:13px;color:#0c5460;}
    </style></head>
    <body>
        <div class="login-box">
            <h2>🔐 Inicio Sesión</h2>
            <div class="info">
                <strong>Acceso para:</strong><br>
                • Docentes y personal administrativo<br>
                • Estudiantes
            </div>
            {% if mensaje %}
            <div class="message {{ tipo }}">{{ mensaje }}</div>
            {% endif %}
            <form method="POST">
                <input type="text" name="usuario" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar</button>
            </form>
            <p style="text-align:center;margin-top:20px;">
                <a href="/" style="color:#667eea;">← Volver al inicio</a>
            </p>
        </div>
    </body></html>
    ''', mensaje=mensaje, tipo=tipo)

# PANEL - Diferente según tipo de usuario
@app.route('/panel')
@login_required
def panel():
    registrar_auditoria('Acceso al panel')
    
    rol = session.get('rol')
    tipo_usuario = session.get('tipo_usuario')
    
    # Panel para ESTUDIANTES
    if tipo_usuario == 'estudiante':
        return f'''
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Panel Estudiante</title>
        <style>
            body {{font-family:Arial;background:#f5f5f5;padding:20px;}}
            .panel {{background:white;padding:30px;border-radius:10px;max-width:800px;margin:auto;}}
            .welcome {{background:linear-gradient(135deg, #28a745 0%, #20c997 100%);
                      color:white;padding:20px;border-radius:8px;margin-bottom:20px;}}
            .menu-grid {{display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
                        gap:15px;margin-top:20px;}}
            .menu-item {{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;
                        border-left:4px solid #28a745;transition:all 0.3s;}}
            .menu-item:hover {{transform:translateY(-3px);box-shadow:0 5px 15px rgba(0,0,0,0.1);}}
            a {{color:#28a745;text-decoration:none;font-weight:bold;}}
        </style></head>
        <body>
            <div class="panel">
                <div class="welcome">
                    <h1>👨‍🎓 Bienvenido, {session['nombre']}</h1>
                    <p>Portal del Estudiante</p>
                </div>
                
                <h2>📋 Mis Opciones</h2>
                <div class="menu-grid">
                    <div class="menu-item"><h3>📊</h3><a href="/estudiante/mis-notas">Mis Calificaciones</a></div>
                    <div class="menu-item"><h3>📚</h3><a href="/estudiante/mis-materias">Mis Materias</a></div>
                    <div class="menu-item"><h3>📄</h3><a href="/estudiante/boletin">Boletín de Notas</a></div>
                    <div class="menu-item"><h3>🚪</h3><a href="/logout">Cerrar Sesión</a></div>
                </div>
            </div>
        </body></html>
        '''
    
    # Panel para DOCENTES/ADMIN
    opciones = []
    
    # Opciones comunes para todos los docentes
    opciones.append('<div class="menu-item"><h3>📊</h3><a href="/mis-notas">Mis Notas</a></div>')
    opciones.append('<div class="menu-item"><h3>📄</h3><a href="/reportes">Reportes</a></div>')
    
    if rol in ['docente']:
        opciones.append('<div class="menu-item"><h3>👨‍🎓</h3><a href="/mis-estudiantes">Mis Estudiantes</a></div>')
    # Opciones para coordinador y admin
    if rol in ['coordinador', 'admin']:
        opciones.append('<div class="menu-item"><h3>👨‍🎓</h3><a href="/estudiantes">Todos los Estudiantes</a></div>')
        opciones.append('<div class="menu-item"><h3>👨‍🏫</h3><a href="/docentes">Personal Docente</a></div>')
        opciones.append('<div class="menu-item"><h3>📊</h3><a href="/notas">Todas las Notas</a></div>')
    
    # Opciones solo para admin
    if rol == 'admin':
        opciones.append('<div class="menu-item"><h3>💾</h3><a href="/backup">Respaldos</a></div>')
        opciones.append('<div class="menu-item"><h3>🗄️</h3><a href="/ver-base-datos">Base de Datos</a></div>')
        opciones.append('<div class="menu-item"><h3>📋</h3><a href="/auditoria">Auditoría</a></div>')
    
    opciones_html = '\n'.join(opciones)
    
    return f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Panel</title>
    <style>
        body {{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .panel {{background:white;padding:30px;border-radius:10px;max-width:1000px;margin:auto;}}
        .welcome {{background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color:white;padding:20px;border-radius:8px;margin-bottom:20px;}}
        .security-info {{background:#d4edda;border-left:4px solid #28a745;padding:15px;
                        margin:20px 0;border-radius:5px;}}
        .menu-grid {{display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
                    gap:15px;margin-top:20px;}}
        .menu-item {{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;
                    border-left:4px solid #667eea;transition:all 0.3s;}}
        .menu-item:hover {{transform:translateY(-3px);box-shadow:0 5px 15px rgba(0,0,0,0.1);}}
        a {{color:#667eea;text-decoration:none;font-weight:bold;}}
    </style></head>
    <body>
        <div class="panel">
            <div class="welcome">
                <h1> Bienvenido, {session['nombre']}</h1>
                <p>Sistema de Gestión Académica</p>
            </div>
            <h2>📋 Panel de Control</h2>
            <div class="menu-grid">
                {opciones_html}
                <div class="menu-item"><h3>🚪</h3><a href="/logout">Cerrar Sesión</a></div>
            </div>
        </div>
    </body></html>
    '''

# ========== RUTAS PARA ESTUDIANTES ==========

@app.route('/estudiante/mis-notas')
@login_required
def estudiante_mis_notas():
    if session.get('tipo_usuario') != 'estudiante':
        return redirect('/panel')
    
    registrar_auditoria('Estudiante consulta sus notas')
    
    estudiante_id = session.get('user_id')
    conn = get_db_connection()
    
    # Obtener notas del estudiante
    notas = conn.execute("""
        SELECT n.*, m.nombre as nombre_materia, m.codigo,
               d.nombre as nombre_doc, d.apellidos as apellidos_doc
        FROM notas n
        JOIN materias m ON n.materia_id = m.id
        JOIN docentes d ON n.docente_id = d.id
        WHERE n.estudiante_id = ?
        ORDER BY m.nombre
    """, (estudiante_id,)).fetchall()
    
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Mis Notas</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}
        .header{background:linear-gradient(135deg, #28a745 0%, #20c997 100%);color:white;
                padding:20px;border-radius:8px;margin-bottom:20px;}
        table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;}
        th,td{padding:12px;text-align:center;border-bottom:1px solid #ddd;}
        th{background:#28a745;color:white;}
        tr:hover{background:#f8f9fa;}
        .nota-alta{color:#28a745;font-weight:bold;}
        .nota-media{color:#ffc107;font-weight:bold;}
        .nota-baja{color:#dc3545;font-weight:bold;}
        .promedio-final{font-size:1.1em;font-weight:bold;color:#28a745;}
    </style></head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Mis Calificaciones</h2>
                <p>Estudiante: ''' + session['nombre'] + '''</p>
            </div>
            <table>
                <tr><th>Materia</th><th>Código</th><th>Docente</th>
                <th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>Final</th><th>Observaciones</th></tr>'''
    
    promedio_total = 0
    count = 0
    
    for nota in notas:
        final = nota['nota_final'] or 0
        promedio_total += final
        count += 1
        
        # Clase CSS según nota
        if final >= 4.0:
            clase = 'nota-alta'
        elif final >= 3.0:
            clase = 'nota-media'
        else:
            clase = 'nota-baja'
        
        html += f'''<tr>
            <td><strong>{nota['nombre_materia']}</strong></td>
            <td>{nota['codigo']}</td>
            <td>{nota['nombre_doc']} {nota['apellidos_doc']}</td>
            <td>{nota['nota_periodo1'] or '-'}</td>
            <td>{nota['nota_periodo2'] or '-'}</td>
            <td>{nota['nota_periodo3'] or '-'}</td>
            <td>{nota['nota_periodo4'] or '-'}</td>
            <td class="{clase}">{nota['nota_final'] or '-'}</td>
            <td>{nota['observaciones'] or '-'}</td>
        </tr>'''
    
    # Calcular promedio
    promedio = promedio_total / count if count > 0 else 0
    
    html += f'''</table>
            <div style="text-align:right;margin:20px 0;padding:15px;background:#f8f9fa;border-radius:8px;">
                <span class="promedio-final">Promedio General: {promedio:.2f}</span>
            </div>
            <a href="/panel">← Volver al Panel</a>
        </div>
    </body></html>'''
    
    return html

@app.route('/estudiante/mis-materias')
@login_required
def estudiante_mis_materias():
    if session.get('tipo_usuario') != 'estudiante':
        return redirect('/panel')
    
    registrar_auditoria('Estudiante consulta sus materias')
    
    estudiante_id = session.get('user_id')
    conn = get_db_connection()
    
    # Obtener info del estudiante
    estudiante = conn.execute("SELECT * FROM estudiantes WHERE id=?", (estudiante_id,)).fetchone()
    
    # Obtener materias del grado
    materias = conn.execute("""
        SELECT DISTINCT m.*, d.nombre as nombre_doc, d.apellidos as apellidos_doc
        FROM materias m
        LEFT JOIN notas n ON m.id = n.materia_id AND n.estudiante_id = ?
        LEFT JOIN docentes d ON n.docente_id = d.id
        WHERE m.grado = ?
        ORDER BY m.nombre
    """, (estudiante_id, estudiante['grado'])).fetchall()
    
    conn.close()
    
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Mis Materias</title>
    <style>
        body{{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .container{{background:white;padding:30px;border-radius:10px;max-width:1000px;margin:auto;}}
        .header{{background:linear-gradient(135deg, #28a745 0%, #20c997 100%);color:white;
                padding:20px;border-radius:8px;margin-bottom:20px;}}
        .materia-grid{{display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:15px;margin:20px 0;}}
        .materia-card{{background:#f8f9fa;padding:20px;border-radius:8px;border-left:4px solid #28a745;}}
        .materia-card h3{{color:#28a745;margin-bottom:10px;}}
        .materia-card p{{color:#666;margin:5px 0;font-size:14px;}}
    </style></head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📚 Mis Materias</h2>
                <p>Grado: {estudiante['grado']} - Sección: {estudiante['seccion']}</p>
            </div>
            <div class="materia-grid">'''
    
    for mat in materias:
        docente = f"{mat['nombre_doc']} {mat['apellidos_doc']}" if mat['nombre_doc'] else "Por asignar"
        html += f'''
            <div class="materia-card">
                <h3>{mat['nombre']}</h3>
                <p><strong>Código:</strong> {mat['codigo']}</p>
                <p><strong>Horas/semana:</strong> {mat['intensidad_horaria']}</p>
                <p><strong>Docente:</strong> {docente}</p>
                <p><strong>Descripción:</strong> {mat['descripcion'] or 'Sin descripción'}</p>
            </div>'''
    
    html += '''</div>
            <a href="/panel">← Volver al Panel</a>
        </div>
    </body></html>'''
    
    return html

@app.route('/estudiante/boletin')
@login_required
def estudiante_boletin():
    if session.get('tipo_usuario') != 'estudiante':
        return redirect('/panel')
    
    registrar_auditoria('Estudiante genera boletín')
    
    estudiante_id = session.get('user_id')
    conn = get_db_connection()
    
    estudiante = conn.execute("SELECT * FROM estudiantes WHERE id=?", (estudiante_id,)).fetchone()
    
    notas = conn.execute("""
        SELECT n.*, m.nombre as nombre_materia, m.codigo
        FROM notas n
        JOIN materias m ON n.materia_id = m.id
        WHERE n.estudiante_id = ?
        ORDER BY m.nombre
    """, (estudiante_id,)).fetchall()
    
    conn.close()
    
    # Calcular promedio
    promedio = 0
    if notas:
        total = sum(n['nota_final'] or 0 for n in notas)
        promedio = total / len(notas)
    
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Boletín de Notas</title>
    <style>
        body{{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .boletin{{background:white;padding:40px;border-radius:10px;max-width:800px;margin:auto;
                 box-shadow:0 5px 20px rgba(0,0,0,0.1);}}
        .header-boletin{{text-align:center;border-bottom:3px solid #667eea;padding-bottom:20px;margin-bottom:20px;}}
        .header-boletin h1{{color:#667eea;margin-bottom:5px;}}
        .info-estudiante{{background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0;}}
        .info-estudiante p{{margin:5px 0;}}
        table{{width:100%;border-collapse:collapse;margin:20px 0;}}
        th,td{{padding:10px;border:1px solid #ddd;text-align:center;}}
        th{{background:#667eea;color:white;}}
        .promedio{{text-align:right;font-size:1.2em;margin:20px 0;padding:15px;
                  background:#d4edda;border-radius:8px;}}
        .footer-boletin{{text-align:center;margin-top:30px;padding-top:20px;
                        border-top:1px solid #ddd;color:#666;font-size:12px;}}
        @media print{{
            body{{background:white;}}
            .no-print{{display:none;}}
        }}
    </style></head>
    <body>
        <div class="boletin">
            <div class="header-boletin">
                <h1>🎓 Centro Educativo San Carlo de Acutis</h1>
                <h2>Boletín de Calificaciones</h2>
                <p>Período Académico 2025</p>
            </div>
            
            <div class="info-estudiante">
                <p><strong>Estudiante:</strong> {estudiante['nombre']} {estudiante['apellidos']}</p>
                <p><strong>Cédula:</strong> {estudiante['cedula']}</p>
                <p><strong>Grado:</strong> {estudiante['grado']} - Sección: {estudiante['seccion']}</p>
            </div>
            
            <table>
                <tr><th>Materia</th><th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>Definitiva</th></tr>'''
    
    for nota in notas:
        html += f'''<tr>
            <td><strong>{nota['nombre_materia']}</strong></td>
            <td>{nota['nota_periodo1'] or '-'}</td>
            <td>{nota['nota_periodo2'] or '-'}</td>
            <td>{nota['nota_periodo3'] or '-'}</td>
            <td>{nota['nota_periodo4'] or '-'}</td>
            <td><strong>{nota['nota_final'] or '-'}</strong></td>
        </tr>'''
    
    html += f'''</table>
            
            <div class="promedio">
                <strong>Promedio General: {promedio:.2f}</strong>
            </div>
            
            <div class="footer-boletin">
                <p>Este documento es un reporte informativo generado por el sistema académico.</p>
                <p>Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="no-print" style="text-align:center;margin-top:20px;">
                <button onclick="window.print()" style="padding:10px 30px;background:#667eea;
                        color:white;border:none;border-radius:5px;cursor:pointer;margin-right:10px;">
                    🖨️ Imprimir Boletín
                </button>
                <a href="/panel" style="padding:10px 30px;background:#6c757d;color:white;
                   text-decoration:none;border-radius:5px;">← Volver</a>
            </div>
        </div>
    </body></html>'''
    
    return html


@app.route('/estudiantes')
@login_required
@role_required('coordinador', 'admin')
def estudiantes():
    registrar_auditoria('Consulta lista de estudiantes')
    
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes WHERE estado='activo' ORDER BY apellidos").fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Estudiantes</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#667eea;color:white;}
        tr:hover{background:#f8f9fa;}
    </style></head>
    <body>
        <div class="container">
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
            <td>{est['email']}</td>
            <td>{est['nombre_acudiente']}</td>
            <td>{est['telefono_acudiente']}</td>
        </tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/mis-estudiantes')
@login_required
def mis_estudiantes():
    registrar_auditoria('Consulta mis estudiantes')
    
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes WHERE estado='activo' ORDER BY apellidos LIMIT 10").fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Mis Estudiantes</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#667eea;color:white;}
        tr:hover{background:#f8f9fa;}
    </style></head>
    <body>
        <div class="container">
            <h2>👨‍🎓 Mis Estudiantes</h2>
            <table>
                <tr><th>Nombre Completo</th><th>Grado</th><th>Sección</th><th>Email</th></tr>'''
    
    for est in estudiantes:
        html += f'''<tr>
            <td>{est['nombre']} {est['apellidos']}</td>
            <td>{est['grado']}</td>
            <td>{est['seccion']}</td>
            <td>{est['email']}</td>
        </tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/notas')
@login_required
@role_required('coordinador', 'admin')
def notas():
    registrar_auditoria('Consulta todas las notas')
    
    conn = get_db_connection()
    notas = conn.execute("""
        SELECT n.*, e.nombre as nombre_est, e.apellidos as apellidos_est,
               m.nombre as nombre_materia, d.nombre as nombre_doc
        FROM notas n
        JOIN estudiantes e ON n.estudiante_id = e.id
        JOIN materias m ON n.materia_id = m.id
        JOIN docentes d ON n.docente_id = d.id
        ORDER BY e.apellidos, m.nombre
    """).fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Notas</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1400px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;}
        th,td{padding:10px;text-align:center;border-bottom:1px solid #ddd;}
        th{background:#667eea;color:white;}
        tr:hover{background:#f8f9fa;}
        .promedio{font-weight:bold;color:#667eea;}
    </style></head>
    <body>
        <div class="container">
            <h2>📊 Registro de Calificaciones</h2>
            <table>
                <tr><th>Estudiante</th><th>Materia</th><th>Docente</th>
                <th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>Final</th><th>Periodo</th></tr>'''
    
    for nota in notas:
        html += f'''<tr>
            <td>{nota['nombre_est']} {nota['apellidos_est']}</td>
            <td>{nota['nombre_materia']}</td>
            <td>{nota['nombre_doc']}</td>
            <td>{nota['nota_periodo1'] or '-'}</td>
            <td>{nota['nota_periodo2'] or '-'}</td>
            <td>{nota['nota_periodo3'] or '-'}</td>
            <td>{nota['nota_periodo4'] or '-'}</td>
            <td class="promedio">{nota['nota_final'] or '-'}</td>
            <td>{nota['periodo']}</td>
        </tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/mis-notas')
@login_required
def mis_notas():
    registrar_auditoria('Consulta mis notas')
    
    user_id = session.get('user_id')
    conn = get_db_connection()
    notas = conn.execute("""
        SELECT n.*, e.nombre as nombre_est, e.apellidos as apellidos_est,
               m.nombre as nombre_materia
        FROM notas n
        JOIN estudiantes e ON n.estudiante_id = e.id
        JOIN materias m ON n.materia_id = m.id
        WHERE n.docente_id = ?
        ORDER BY e.apellidos, m.nombre
    """, (user_id,)).fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Mis Notas</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1400px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;}
        th,td{padding:10px;text-align:center;border-bottom:1px solid #ddd;}
        th{background:#667eea;color:white;}
        tr:hover{background:#f8f9fa;}
        .promedio{font-weight:bold;color:#667eea;}
    </style></head>
    <body>
        <div class="container">
            <h2>📊 Mis Calificaciones Registradas</h2>
            <table>
                <tr><th>Estudiante</th><th>Materia</th>
                <th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>Final</th><th>Periodo</th></tr>'''
    
    for nota in notas:
        html += f'''<tr>
            <td>{nota['nombre_est']} {nota['apellidos_est']}</td>
            <td>{nota['nombre_materia']}</td>
            <td>{nota['nota_periodo1'] or '-'}</td>
            <td>{nota['nota_periodo2'] or '-'}</td>
            <td>{nota['nota_periodo3'] or '-'}</td>
            <td>{nota['nota_periodo4'] or '-'}</td>
            <td class="promedio">{nota['nota_final'] or '-'}</td>
            <td>{nota['periodo']}</td>
        </tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/docentes')
@login_required
@role_required('coordinador', 'admin')
def docentes():
    registrar_auditoria('Consulta lista de docentes')
    
    conn = get_db_connection()
    docentes = conn.execute("SELECT * FROM docentes WHERE estado='activo' ORDER BY apellidos").fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Docentes</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#764ba2;color:white;}
        tr:hover{background:#f8f9fa;}
    </style></head>
    <body>
        <div class="container">
            <h2>👨‍🏫 Planta Docente</h2>
            <table>
                <tr><th>Cédula</th><th>Nombre Completo</th><th>Email</th>
                <th>Especialidad</th><th>Fecha Ingreso</th></tr>'''
    
    for doc in docentes:
        html += f'''<tr>
            <td>{doc['cedula']}</td>
            <td>{doc['nombre']} {doc['apellidos']}</td>
            <td>{doc['email']}</td>
            <td>{doc['especialidad']}</td>
            <td>{doc['fecha_ingreso']}</td>
        </tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/reportes')
@login_required
def reportes():
    registrar_auditoria('Acceso a reportes')
    
    return '''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Reportes</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:900px;margin:auto;}
        .report-grid{display:grid;grid-template-columns:repeat(auto-fit, minmax(250px, 1fr));
                     gap:20px;margin-top:20px;}
        .report-card{background:#f8f9fa;padding:25px;border-radius:8px;text-align:center;
                     border-left:4px solid #28a745;transition:all 0.3s;}
        .report-card:hover{transform:translateY(-3px);box-shadow:0 5px 15px rgba(0,0,0,0.1);}
        .report-icon{font-size:3em;margin-bottom:15px;}
        button{padding:10px 20px;background:#28a745;color:white;border:none;
               border-radius:5px;cursor:pointer;margin-top:10px;}
        button:hover{background:#218838;}
    </style></head>
    <body>
        <div class="container">
            <h2>📄 Generación de Reportes</h2>
            <div class="report-grid">
                <div class="report-card">
                    <div class="report-icon">📋</div>
                    <h3>Boletín de Notas</h3>
                    <p>Reporte individual por estudiante</p>
                    <button onclick="alert('Generando reporte...')">Generar</button>
                </div>
                <div class="report-card">
                    <div class="report-icon">📊</div>
                    <h3>Estadísticas de Curso</h3>
                    <p>Promedios y rendimiento general</p>
                    <button onclick="alert('Generando reporte...')">Generar</button>
                </div>
            </div>
            <br><br><a href="/panel">← Volver</a>
        </div>
    </body></html>
    '''

@app.route('/backup')
@login_required
@role_required('admin')
def backup():
    registrar_auditoria('Acceso a gestión de backups')
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        for i in range(1, 5):
            with open(f'{backup_dir}/backup_2025-01-{15-i:02d}.db', 'w') as f:
                f.write(f"BACKUP DATABASE {15-i}")
    
    backups = []
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            size = os.path.getsize(os.path.join(backup_dir, f))
            backups.append({'nombre': f, 'tamaño': f'{size/1024:.1f} KB', 'fecha': '2025-01-15 03:00:00'})
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Respaldos</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:900px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#28a745;color:white;}
    </style></head>
    <body>
        <div class="container">
            <h2>💾 Gestión de Respaldos</h2>
            <table><tr><th>Archivo</th><th>Tamaño</th><th>Fecha</th></tr>'''
    
    for b in backups:
        html += f'<tr><td>{b["nombre"]}</td><td>{b["tamaño"]}</td><td>{b["fecha"]}</td></tr>'
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/ver-base-datos')
@login_required
@role_required('admin')
def ver_base_datos():
    registrar_auditoria('Consulta estructura de base de datos')
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Base de Datos</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1000px;margin:auto;}
        .table-grid{display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:15px;margin:20px 0;}
        .table-card{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;border-left:4px solid #667eea;}
    </style></head>
    <body>
        <div class="container">
            <h2>🗄️ Estructura de la Base de Datos</h2>
            <div class="table-grid">'''
    
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) as c FROM {table['name']}").fetchone()['c']
        html += f'<div class="table-card"><h3>{table["name"]}</h3><p>{count} registros</p></div>'
    
    conn.close()
    html += '</div><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/auditoria')
@login_required
@role_required('admin')
def auditoria():
    registrar_auditoria('Consulta registros de auditoría')
    conn = get_db_connection()
    registros = conn.execute("SELECT * FROM auditoria ORDER BY fecha DESC LIMIT 100").fetchall()
    conn.close()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Auditoría</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1400px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;font-size:13px;}
        th,td{padding:10px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#dc3545;color:white;}
    </style></head>
    <body>
        <div class="container">
            <h2>📋 Registro de Auditoría</h2>
            <table><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Detalles</th><th>IP</th></tr>'''
    
    for reg in registros:
        html += f'''<tr><td>{reg['fecha']}</td><td>{reg['usuario']}</td>
            <td>{reg['accion']}</td><td>{reg['detalles'] or '-'}</td><td>{reg['ip_address']}</td></tr>'''
    
    html += '</table><a href="/panel">← Volver</a></div></body></html>'
    return html

@app.route('/logout')
def logout():
    usuario = session.get('usuario', 'desconocido')
    registrar_auditoria('Logout', f'Usuario: {usuario}')
    session.clear()
    return redirect('/')

@app.route('/api/stats')
@login_required
def api_stats():
    conn = get_db_connection()
    stats = {
        'estudiantes': conn.execute("SELECT COUNT(*) as c FROM estudiantes WHERE estado='activo'").fetchone()['c'],
        'docentes': conn.execute("SELECT COUNT(*) as c FROM docentes WHERE estado='activo'").fetchone()['c'],
        'notas': conn.execute("SELECT COUNT(*) as c FROM notas").fetchone()['c'],
    }
    conn.close()
    return jsonify(stats)


if __name__ == '__main__':
    print("=" * 70)
    print("🎓 SISTEMA ACADÉMICO - CENTRO EDUCATIVO SAN CARLO DE ACUTIS")
    print("=" * 70)
    print(f"📍 Servidor: http://0.0.0.0:5000")
    print(f"🗄️  Base de datos: SQLite - {DATABASE}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False)