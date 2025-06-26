import os

class Config:
    # Configuración Oracle
    ORACLE_USER = os.getenv('ORACLE_USER', 'root')
    ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD', '123456')
    ORACLE_HOST = os.getenv('ORACLE_HOST', 'localhost')
    ORACLE_PORT = os.getenv('ORACLE_PORT', '1521')
    ORACLE_SERVICE = os.getenv('ORACLE_SERVICE', 'FREEPDB1')
    
    # Otras configuraciones
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración FTP
    FTP_HOST = os.getenv('FTP_HOST', 'localhost')
    FTP_PORT = int(os.getenv('FTP_PORT', 21))
    FTP_USER = os.getenv('FTP_USER', 'anonymous')
    FTP_PASS = os.getenv('FTP_PASS', '')
    FTP_BASE_DIR = os.getenv('FTP_BASE_DIR', '/')
    USE_SFTP = os.getenv('FTP_BASE_DIR', False)