from flask import Blueprint
from .routes import init_routes

epu_bp = Blueprint('epu', __name__)

# Inicializar rutas
init_routes(epu_bp)