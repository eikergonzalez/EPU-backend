from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))

def init_db(app):
   
    # Configuración de conexión Oracle
    oracle_connection_string = (
        f"oracle+cx_oracle://{app.config['ORACLE_USER']}:"
        f"{app.config['ORACLE_PASSWORD']}@"
        f"{app.config['ORACLE_HOST']}:"
        f"{app.config['ORACLE_PORT']}/"
        f"?service_name={app.config['ORACLE_SERVICE']}"
    )
    
    engine = create_engine(
        oracle_connection_string,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        arraysize=50,  # Mejora para fetch de múltiples registros
        echo=False  # Cambiar a True para debug
    )
    
    db_session.configure(bind=engine)
    Base.metadata.create_all(bind=engine)