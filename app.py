from flask import Flask
import logging
from dotenv import load_dotenv
from flask_cors import CORS
from common.database import init_db, db_session
from config import Config
from services.epu import epu_bp
from flasgger import Swagger
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos
    init_db(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if db_session is not None:
            db_session.remove()

    # Configurar CORS
    """ CORS(app, resources={r"/*": {"origins": ORIGIN_CORS_LIST}},
      supports_credentials=True,
      allow_headers=["Content-Type", "Authorization"]) """

    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.config['SWAGGER'] = {
        'title': 'br-ms-sd10001-oi00039-embassadorepus',
        'uiversion': 3,
        'specs_route': '/api/docs/'
    }
    Swagger(app)

    app.config['FTP_CONFIG'] = {
        'HOST': Config.FTP_HOST,
        'USERNAME': Config.FTP_USER,
        'PASSWORD': Config.FTP_PASS,
        'PORT': Config.FTP_PORT,
        'USE_SFTP': Config.USE_SFTP
    }

    # Registrar blueprints (microservicios)
    app.register_blueprint(epu_bp, url_prefix='/api')
    #app.register_blueprint(productos_bp, url_prefix='/api/productos')
    #app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')

    return app

if __name__ == '__main__':
    app = create_app()
    host = os.environ.get('APP_HOST', '0.0.0.0')
    port = int(os.environ.get('APP_PORT', 3020))
    debug = os.environ.get('APPDEBUG', 'True').lower() in ['true', '1', 'yes']
    app.run(host=host, port=port, debug=debug)