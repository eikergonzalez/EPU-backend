from io import BytesIO
import zipfile
from datetime import datetime
import py7zr
import os

class FileCompressor:
    @staticmethod
    def compress_files(files_dict):
        """Comprime archivos en un ZIP en memoria"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in files_dict.items():
                zipf.writestr(filename, file_data.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer

    @staticmethod
    def decompress_file(file_path):
        """Descomprime un archivo .7z y retorna una lista de rutas de archivos extraídos."""
        extracted_files = []
        extract_dir = os.path.splitext(file_path)[0]  # Carpeta con el mismo nombre que el archivo
        os.makedirs(extract_dir, exist_ok=True)
        with py7zr.SevenZipFile(file_path, mode='r') as archive:
            archive.extractall(path=extract_dir)
            for root, dirs, files in os.walk(extract_dir):
                for name in files:
                    extracted_files.append(os.path.join(root, name))
        return extracted_files