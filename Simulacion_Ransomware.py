from flask import Flask, render_template_string, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'AcademicoSecretKey2025'

# Base de datos SQLite
DATABASE = 'sistema_academico.db'

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
    
    # Insertar datos de prueba
    try:
        # Docentes
        docentes = [
            ('1234567890', 'María', 'González Pérez', 'mgonzalez@colegio.edu', '555-0101', 'Matemáticas', '2020-01-15', 'mgonzalez', 'Docente123', 'docente'),
            ('0987654321', 'Juan', 'Ramírez López', 'jramirez@colegio.edu', '555-0102', 'Español', '2019-03-20', 'jramirez', 'Docente456', 'docente'),
            ('1122334455', 'Ana', 'Martínez Silva', 'amartinez@colegio.edu', '555-0103', 'Ciencias', '2021-07-10', 'amartinez', 'Docente789', 'coordinador'),
            ('5544332211', 'Carlos', 'Rodríguez Gómez', 'crodriguez@colegio.edu', '555-0104', 'Sistemas', '2018-09-01', 'admin', 'Admin2025', 'admin')
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
            ('1001234567', 'Pedro', 'Sánchez Ruiz', '2010-03-15', 'Sexto', 'A', 'psanchez@estudiante.edu', '555-1001', 'Calle 10 #20-30', 'Rosa Ruiz', '555-2001'),
            ('1001234568', 'Laura', 'García Méndez', '2010-05-22', 'Sexto', 'A', 'lgarcia@estudiante.edu', '555-1002', 'Carrera 5 #15-25', 'Luis García', '555-2002'),
            ('1001234569', 'Diego', 'Torres Vega', '2009-11-08', 'Séptimo', 'A', 'dtorres@estudiante.edu', '555-1003', 'Avenida 8 #12-18', 'Carmen Vega', '555-2003'),
            ('1001234570', 'Sofía', 'Morales Castro', '2010-07-30', 'Sexto', 'B', 'smorales@estudiante.edu', '555-1004', 'Calle 20 #30-40', 'Roberto Morales', '555-2004'),
            ('1001234571', 'Andrés', 'Jiménez Rojas', '2009-09-12', 'Séptimo', 'A', 'ajimenez@estudiante.edu', '555-1005', 'Carrera 15 #25-35', 'Patricia Rojas', '555-2005'),
            ('1001234572', 'Valentina', 'López Herrera', '2010-02-18', 'Sexto', 'A', 'vlopez@estudiante.edu', '555-1006', 'Calle 30 #40-50', 'María Herrera', '555-2006'),
            ('1001234573', 'Santiago', 'Pérez Navarro', '2010-08-25', 'Sexto', 'B', 'sperez@estudiante.edu', '555-1007', 'Carrera 25 #35-45', 'Jorge Pérez', '555-2007'),
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
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .card-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        .card h3 {
            color: #333;
            margin-bottom: 10px;
        }
        .card p {
            color: #666;
            font-size: 0.9em;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .stat-item {
            display: inline-block;
            padding: 15px 30px;
            margin: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .stat-number {
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
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
            <p>Sistema de Gestión Académica 2025</p>
        </div>
        <div class="nav-bar">
            <a href="/">🏠 Inicio</a>
            <a href="/login">🔐 Ingresar</a>
            <a href="/estudiantes">👨‍🎓 Estudiantes</a>
            <a href="/docentes">👨‍🏫 Docentes</a>
            <a href="/notas">📊 Notas</a>
            <a href="/reportes">📄 Reportes</a>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <h2 style="text-align: center; color: #333; margin-bottom: 20px;">📊 Estadísticas del Sistema</h2>
            <center>
                <div class="stat-item">
                    <div class="stat-number">{{ total_estudiantes }}</div>
                    <div class="stat-label">Estudiantes Activos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ total_docentes }}</div>
                    <div class="stat-label">Docentes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ total_materias }}</div>
                    <div class="stat-label">Materias</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ total_notas }}</div>
                    <div class="stat-label">Notas Registradas</div>
                </div>
            </center>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-icon">👨‍🎓</div>
                <h3>Estudiantes</h3>
                <p>Gestión de matrícula y datos personales</p>
            </div>
            <div class="card">
                <div class="card-icon">👨‍🏫</div>
                <h3>Docentes</h3>
                <p>Administración del personal docente</p>
            </div>
            <div class="card">
                <div class="card-icon">📊</div>
                <h3>Calificaciones</h3>
                <p>Registro y consulta de notas</p>
            </div>
            <div class="card">
                <div class="card-icon">📅</div>
                <h3>Asistencias</h3>
                <p>Control de asistencia diaria</p>
            </div>
            <div class="card">
                <div class="card-icon">📄</div>
                <h3>Reportes</h3>
                <p>Informes y certificados</p>
            </div>
            <div class="card">
                <div class="card-icon">💾</div>
                <h3>Respaldos</h3>
                <p>Copias de seguridad</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>&copy; 2025 Centro Educativo San Carlo de Acutis | Sistema Académico v2.5.1</p>
        <p>Base de Datos: SQLite | Servidor: Ubuntu Server 22.04</p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    conn = get_db_connection()
    
    total_estudiantes = conn.execute("SELECT COUNT(*) as total FROM estudiantes WHERE estado='activo'").fetchone()['total']
    total_docentes = conn.execute("SELECT COUNT(*) as total FROM docentes WHERE estado='activo'").fetchone()['total']
    total_materias = conn.execute("SELECT COUNT(*) as total FROM materias").fetchone()['total']
    total_notas = conn.execute("SELECT COUNT(*) as total FROM notas").fetchone()['total']
    
    conn.close()
    
    return render_template_string(HOME_HTML, 
                                 total_estudiantes=total_estudiantes,
                                 total_docentes=total_docentes,
                                 total_materias=total_materias,
                                 total_notas=total_notas)

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
            return redirect('/panel')
        else:
            mensaje = 'Usuario o contraseña incorrectos'
            tipo = 'error'
    
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
        .hint {background:#d1ecf1;padding:10px;margin:15px 0;border-radius:5px;font-size:12px;}
    </style></head>
    <body>
        <div class="login-box">
            <h2>🔐 Acceso Docentes</h2>
            <div class="hint">💡 Usuario: admin | Contraseña: Admin2025</div>
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

# PANEL DOCENTE
@app.route('/panel')
def panel():
    if 'usuario' not in session:
        return redirect('/login')
    
    return f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Panel Docente</title>
    <style>
        body {{font-family:Arial;background:#f5f5f5;padding:20px;}}
        .panel {{background:white;padding:30px;border-radius:10px;max-width:1000px;margin:auto;}}
        .welcome {{background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color:white;padding:20px;border-radius:8px;margin-bottom:20px;}}
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
                <h1>👨‍🏫 Bienvenido, {session['nombre']}</h1>
                <p>Rol: {session['rol']} | Usuario: {session['usuario']}</p>
            </div>
            <h2>📋 Panel de Control</h2>
            <div class="menu-grid">
                <div class="menu-item"><h3>👨‍🎓</h3><a href="/estudiantes">Ver Estudiantes</a></div>
                <div class="menu-item"><h3>📊</h3><a href="/notas">Ver Notas</a></div>
                <div class="menu-item"><h3>📄</h3><a href="/reportes">Reportes</a></div>
                <div class="menu-item"><h3>💾</h3><a href="/backup">Respaldos</a></div>
                <div class="menu-item"><h3>🗄️</h3><a href="/ver-base-datos">Ver BD</a></div>
                <div class="menu-item"><h3>🚪</h3><a href="/logout">Cerrar Sesión</a></div>
            </div>
        </div>
    </body></html>
    '''

# ESTUDIANTES
@app.route('/estudiantes')
def estudiantes():
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
    
    html += '</table><a href="/">← Volver</a></div></body></html>'
    return html

# NOTAS
@app.route('/notas')
def notas():
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
    
    html += '</table><a href="/">← Volver</a></div></body></html>'
    return html

# DOCENTES
@app.route('/docentes')
def docentes():
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
                <th>Especialidad</th><th>Rol</th><th>Fecha Ingreso</th></tr>'''
    
    for doc in docentes:
        html += f'''<tr>
            <td>{doc['cedula']}</td>
            <td>{doc['nombre']} {doc['apellidos']}</td>
            <td>{doc['email']}</td>
            <td>{doc['especialidad']}</td>
            <td>{doc['rol']}</td>
            <td>{doc['fecha_ingreso']}</td>
        </tr>'''
    
    html += '</table><a href="/">← Volver</a></div></body></html>'
    return html

# REPORTES
@app.route('/reportes')
def reportes():
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
                <div class="report-card">
                    <div class="report-icon">📅</div>
                    <h3>Reporte de Asistencias</h3>
                    <p>Control mensual de asistencia</p>
                    <button onclick="alert('Generando reporte...')">Generar</button>
                </div>
                <div class="report-card">
                    <div class="report-icon">🎓</div>
                    <h3>Certificados</h3>
                    <p>Certificados de estudio</p>
                    <button onclick="alert('Generando certificado...')">Generar</button>
                </div>
            </div>
            <br><br><a href="/">← Volver</a>
        </div>
    </body></html>
    '''

# BACKUP - CRÍTICO PARA EL ATAQUE
@app.route('/backup')
def backup():
    if 'usuario' not in session:
        return redirect('/login')
    
    # Crear archivos de backup simulados
    import os
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        # Crear backups falsos
        for i in range(1, 5):
            with open(f'{backup_dir}/backup_2025-01-{15-i:02d}.db', 'w') as f:
                f.write(f"BACKUP DATABASE {15-i}")
    
    backups = []
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            size = os.path.getsize(os.path.join(backup_dir, f))
            backups.append({
                'nombre': f,
                'tamaño': f'{size/1024:.1f} KB',
                'fecha': '2025-01-15 03:00:00'
            })
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Respaldos</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:900px;margin:auto;}
        table{width:100%;border-collapse:collapse;margin:20px 0;}
        th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;}
        th{background:#28a745;color:white;}
        button{padding:8px 15px;background:#007bff;color:white;border:none;
               border-radius:5px;cursor:pointer;}
        .warning{background:#fff3cd;padding:15px;border-left:4px solid #ffc107;
                 margin:20px 0;border-radius:5px;}
        .create-backup{background:#28a745;color:white;padding:15px 30px;
                       border:none;border-radius:5px;cursor:pointer;font-size:16px;}
    </style></head>
    <body>
        <div class="container">
            <h2>💾 Gestión de Respaldos</h2>
            <div class="warning">
                <strong>⚠️ Importante:</strong> Los respaldos se realizan automáticamente cada día a las 3:00 AM.
            </div>
            <button class="create-backup" onclick="alert('Creando respaldo...')">
                ➕ Crear Respaldo Manual
            </button>
            <h3>📋 Respaldos Disponibles</h3>
            <table>
                <tr><th>Nombre del Archivo</th><th>Tamaño</th><th>Fecha</th><th>Acciones</th></tr>'''
    
    for b in backups:
        html += f'''<tr>
            <td>📄 {b['nombre']}</td>
            <td>{b['tamaño']}</td>
            <td>{b['fecha']}</td>
            <td><button>⬇️ Descargar</button></td>
        </tr>'''
    
    html += '''</table>
        <h3>📊 Información del Sistema</h3>
        <ul>
            <li><strong>Base de datos principal:</strong> sistema_academico.db</li>
            <li><strong>Último respaldo:</strong> Hace 6 horas</li>
            <li><strong>Próximo respaldo:</strong> En 18 horas</li>
            <li><strong>Ubicación:</strong> ./backups/</li>
        </ul>
        <br><a href="/">← Volver</a>
        </div>
    </body></html>'''
    
    return html

# VER BASE DE DATOS (para demostración)
@app.route('/ver-base-datos')
def ver_base_datos():
    if 'usuario' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    
    # Obtener todas las tablas
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Base de Datos</title>
    <style>
        body{font-family:Arial;background:#f5f5f5;padding:20px;}
        .container{background:white;padding:30px;border-radius:10px;max-width:1200px;margin:auto;}
        .table-list{display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
                    gap:15px;margin:20px 0;}
        .table-card{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;
                    border-left:4px solid #667eea;}
        .table-icon{font-size:2em;margin-bottom:10px;}
        .warning{background:#d1ecf1;padding:15px;border-left:4px solid #0c5460;
                 margin:20px 0;border-radius:5px;}
    </style></head>
    <body>
        <div class="container">
            <h2>🗄️ Estructura de la Base de Datos</h2>
            <div class="warning">
                <strong>📍 Archivo:</strong> sistema_academico.db<br>
                <strong>📊 Motor:</strong> SQLite 3<br>
                <strong>💾 Tamaño:</strong> '''
    
    import os
    if os.path.exists(DATABASE):
        size = os.path.getsize(DATABASE)
        html += f'{size/1024:.2f} KB'
    
    html += '''</div>
            <h3>📋 Tablas en el Sistema</h3>
            <div class="table-list">'''
    
    table_info = {
        'estudiantes': {'icon': '👨‍🎓', 'desc': 'Información de estudiantes'},
        'docentes': {'icon': '👨‍🏫', 'desc': 'Personal docente'},
        'materias': {'icon': '📚', 'desc': 'Materias del plan de estudios'},
        'notas': {'icon': '📊', 'desc': 'Calificaciones'}
    }
    
    for table in tables:
        table_name = table['name']
        info = table_info.get(table_name, {'icon': '📄', 'desc': 'Datos del sistema'})
        
        count = conn.execute(f"SELECT COUNT(*) as c FROM {table_name}").fetchone()['c']
        
        html += f'''
                <div class="table-card">
                    <div class="table-icon">{info['icon']}</div>
                    <h3>{table_name}</h3>
                    <p>{info['desc']}</p>
                    <p><strong>{count}</strong> registros</p>
                </div>'''
    
    html += '''
            </div>
            <br><a href="/panel">← Volver al panel</a>
        </div>
    </body></html>'''
    
    conn.close()
    return html

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# API ENDPOINTS
@app.route('/api/estudiantes')
def api_estudiantes():
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes WHERE estado='activo'").fetchall()
    conn.close()
    return jsonify([dict(e) for e in estudiantes])

@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    
    stats = {
        'estudiantes': conn.execute("SELECT COUNT(*) as c FROM estudiantes WHERE estado='activo'").fetchone()['c'],
        'docentes': conn.execute("SELECT COUNT(*) as c FROM docentes WHERE estado='activo'").fetchone()['c'],
        'notas': conn.execute("SELECT COUNT(*) as c FROM notas").fetchone()['c'],
        'promedio_general': round(conn.execute("SELECT AVG(nota_final) as p FROM notas WHERE nota_final IS NOT NULL").fetchone()['p'], 2)
    }
    
    conn.close()
    return jsonify(stats)

if __name__ == '__main__':
    print("=" * 70)
    print("🎓 SISTEMA ACADÉMICO - CENTRO EDUCATIVO SAN CARLO DE ACUTIS")
    print("=" * 70)
    print(f"📍 Servidor: http://0.0.0.0:5000")
    print(f"🗄️  Base de datos: SQLite - {DATABASE}")
    print(f"👥 Usuarios de prueba:")
    print(f"   - admin/Admin2025 (Administrador)")
    print(f"   - mgonzalez/Docente123 (Docente)")
    print("=" * 70)
    print("✅ Sistema listo para operación")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False)