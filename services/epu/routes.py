from flask import request, send_file, jsonify
from flasgger import swag_from
from .services import EpuService
from .schemas import EpuSchema, SchemaSearchSp
from marshmallow import ValidationError
import io
import os
from datetime import datetime, timedelta
import pandas as pd

def init_routes(bp):
    
    @bp.route('/search', methods=['POST'])
    @swag_from({
        'tags': ['EPU'],
        'description': 'Consultar carlotas bancarias',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    '$ref': '#/definitions/SearchRequest'
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Archivo ZIP con los resultados',
                'content': {
                    'application/zip': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid request data',
            },
            404: {
                'description': 'Files not found'
            },
            500: {
                'description': 'Server error'
            }
        },
        'definitions': {
            'SearchRequest': {
                'type': 'object',
                'properties': {
                    'contract_number': {
                        'type': 'string',
                        'example': '100003187135'
                    },
                    'dateInit': {
                        'type': 'string',
                        'example': '2024-01-01'
                    },
                    'dateEnd': {
                        'type': 'string',
                        'example': '2024-06-01'
                    }
                },
                'required': ['contract_number', 'dateInit', 'dateEnd'],
                'additionalProperties': False
            }
        }
    })
    def search():
        try:
            schema = EpuSchema()
            data = schema.load(request.get_json())
            date_now = datetime.now().date().replace(day=1)
            date_init = datetime.strptime(data['dateInit'], "%Y-%m-%d").date().replace(day=1)
            date_end = datetime.strptime(data['dateEnd'], "%Y-%m-%d").date().replace(day=1)

            one_year_ago = date_now - timedelta(days=365)
            date_init_mayor = None
            date_end_mayor = None
            date_init_menor = None
            date_end_menor = None
            files_mayor = []
            files_menor = []

            # Generar todas las fechas entre date_init y date_end
            all_dates = pd.date_range(start=date_init, end=date_end).date.tolist()

            # Filtrar
            fechas_mayor = [date for date in all_dates if date < one_year_ago]
            meses_unicos_mayor = {(d.year, d.month) for d in fechas_mayor}
            fechas_mayor_final = [f"{year:04d}-{month:02d}-01" for year, month in sorted(meses_unicos_mayor)]
            fechas_mayor_final_ordenadas = sorted(fechas_mayor_final)

            fechas_menor = [date for date in all_dates if date >= one_year_ago]
            meses_unicos_menor = {(d.year, d.month) for d in fechas_menor}
            fechas_menor_final = [f"{year:04d}-{month:02d}-01" for year, month in sorted(meses_unicos_menor)]
            # Asegura que la lista esté ordenada
            fechas_menor_final_ordenadas = sorted(fechas_menor_final)

            if fechas_mayor_final_ordenadas:
                date_init_mayor = datetime.strptime(fechas_mayor_final_ordenadas[0], "%Y-%m-%d").date()
                date_end_mayor = datetime.strptime(fechas_mayor_final_ordenadas[-1], "%Y-%m-%d").date()
            
            if fechas_menor_final_ordenadas:
                date_init_menor = datetime.strptime(fechas_menor_final_ordenadas[0], "%Y-%m-%d").date()
                date_end_menor = datetime.strptime(fechas_menor_final_ordenadas[-1], "%Y-%m-%d").date()


            if date_init_mayor and date_end_mayor:
                print(f"Rango de fechas mayor: {date_init_mayor} a {date_end_mayor}, tipo de archivo: 7z")
                """ Busca la facturación de un contrato en un rango de fechas mayor a un año """
                facturacion_mayor = EpuService.search_facturacion(
                    data['contract_number'],
                    date_init_mayor,
                    date_end_mayor
                )

                if not facturacion_mayor:
                    return jsonify({"error": "No hay datos para mostrar"}), 200

                """ Descargo los archivos de facturación """
                
                files_mayor = EpuService.download_files(facturacion_mayor, "7z")

                if not files_mayor:
                    return jsonify({"error": "No hay archivos para descargar"}), 200

                files_mayor = EpuService.unzip_files(files_mayor)

                if not files_mayor:
                    return jsonify({"error": "Error al descomprimir los archivos"}), 200

            if date_init_menor and date_end_menor:
                print(f"Fechas menor a un año: {date_init_menor} a {date_end_menor}")
                """ Busca la facturación de un contrato en un rango de fechas menor a un año """
                facturacion_menor = EpuService.search_facturacion(
                    data['contract_number'],
                    date_init_menor,
                    date_end_menor
                )

                if not facturacion_menor:
                    return jsonify({"error": "No hay datos para mostrar"}), 200

                """ Descargo los archivos de facturación """
                print(f"Rango de fechas menor: {date_init_menor} a {date_end_menor}, tipo de archivo: pdf")

                files_menor = EpuService.download_files(facturacion_menor, "pdf")

                if not files_menor:
                    return jsonify({"error": "No hay archivos para descargar"}), 200

            """ Combino los archivos descargados de ambos rangos de fechas """
            files = files_mayor + files_menor

            if not files:
                return jsonify({"error": "No hay archivos para descargar"}), 200

            zip_buffer = EpuService.zip_files_downloaded(files)
            zip_buffer.seek(0)
            
            EpuService.remove_folder_temp()

            download_name = f"{data['contract_number']}_{date_init.strftime('%Y%m%d')}_{date_end.strftime('%Y%m%d')}.zip"
            
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/zip'
            )
        except ValidationError as err:
            return jsonify({"error ValidationError ": err.messages}), 200
        except Exception as e:
            return jsonify({"error index ": str(e)}), 200
    
    @bp.route('/search-sp', methods=['POST'])
    @swag_from({
        'tags': ['EPU'],
        'description': 'Obtiene las fechas de facturación de un cliente usando un procedimiento almacenado.',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'entidad': {'type': 'string', 'example': '001'},
                        'cen_alt': {'type': 'string', 'example': '002'},
                        'cuenta': {'type': 'string', 'example': '100003187135'}
                    },
                    'required': ['entidad', 'cen_alt', 'cuenta']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Respuesta exitosa con fechas de facturación',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'integer', 'example': 0},
                        'mensaje': {'type': 'string', 'example': 'EXITO'},
                        'data': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'fch_fcn': {'type': 'string', 'example': '2024-01-01'},
                                    'fch_vnc': {'type': 'string', 'example': '2024-12-31'}
                                }
                            }
                        }
                    }
                }
            },
            400: {'description': 'Faltan parámetros'},
            500: {'description': 'Error interno del servidor'}
        }
    })
    def search_sp():
        try:
            schema = SchemaSearchSp()
            data = schema.load(request.get_json())
            entidad = data['entidad']
            cen_alt = data['cen_alt']
            cuenta = data['cuenta']

            if not entidad or not cen_alt or not cuenta:
                return jsonify({"error": "Faltan parámetros"}), 400

            resultado = EpuService.obtener_fechas_facturacion(entidad, cen_alt, cuenta)
            return jsonify(resultado)
        except ValidationError as err:
            return jsonify({"error ValidationError ": err.messages}), 200
        except Exception as e:
            return jsonify({"error index ": str(e)}), 200