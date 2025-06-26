from common.database import db_session
from .models import Epu
from common.utils.sftp_handler import SFTPHandler
from common.utils.file_compressor import FileCompressor
from flask import current_app
import os
import io
import shutil

class EpuService:

    @staticmethod
    def search_facturacion(cuenta, dateInit, dateEnd):
        """ Busca la facturacion ."""
        data = Epu.obtener_facturacion(cuenta, dateInit, dateEnd)
        return data
    
    @staticmethod
    def search_facturacion_sp(entidad, cen_alt, cuenta):
        """ Busca la facturacion por un SP ."""
        data = Epu.obtener_facturacion_sp(entidad, cen_alt, cuenta)
        return data

    @staticmethod
    def download_files(data, file_type):
        """ Recibe data como un arreglo de diccionarios con la información de los archivos a descargar. """
        sftp = None
        try:
            TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'temp_files')
            os.makedirs(TEMP_DIR, exist_ok=True)  # Crea la carpeta si no existe
            sftp = SFTPHandler(current_app.config['FTP_HOST'], 
                              current_app.config['FTP_USER'],
                              current_app.config['FTP_PASS'],
                              current_app.config['FTP_PORT']
                           )
            sftp.connect()
            files = []
            for item in data:
                if file_type == '7z':
                    pdf_filename = f"pdfvcto{item['VCTO'].lower()}"
                    file_path = f"/root/pdfvcto/pdfvcto.backup/{item['VCTO_ANO']}/{item['VCTO_MES']}/{pdf_filename}"
                    local_path = os.path.join(TEMP_DIR, f"{pdf_filename}")
                else:
                    pdf_filename = f"{item['VCTO_ANO']}_{item['VCTO_MES']}_0001{item['ALTA']}{item['CUENTA']}.pdf"
                    file_path = f"/root/pdfvcto/pdfvcto.online/{item['VCTO_ANO']}/{item['VCTO_MES']}/{pdf_filename}"
                    local_path = os.path.join(TEMP_DIR, f"{pdf_filename}")

                sftp.download_file(file_path, local_path)
                files.append(local_path)
            return files
        except Exception as e:
            print(f"Error downloading files: {str(e)}")
            raise
        finally:
            if sftp:
                sftp.close()

    @staticmethod
    def unzip_files(files):
        try:
            """ Descomprimo los archivos 7zip y los devuelve como una lista de rutas de archivos. """
            compressor = FileCompressor()
            unzipped_files = []
            
            for file in files:
                try:
                    unzipped_files.extend(compressor.decompress_file(file))
                except Exception as e:
                    print(f"Error decompressing file {file}: {str(e)}")
                    raise
            
            """ Elimino los archivos 7z originales después de descomprimirlos """
            for file in files:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Error removing file {file}: {str(e)}")

            return unzipped_files
        except Exception as e:
            print(f"Error unzipping files: {str(e)}")
            raise

    @staticmethod
    def zip_files_downloaded(files):
        """ Comprime los archivos descargados en un archivo ZIP en memoria y lo devuelve como buffer. """
        compressor = FileCompressor()
        files_dict = {}
        for file_path in files:
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                files_dict[filename] = io.BytesIO(f.read())
        zip_buffer = compressor.compress_files(files_dict)
        return zip_buffer

    @staticmethod
    def remove_folder_temp():
        TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'temp_files')
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)

