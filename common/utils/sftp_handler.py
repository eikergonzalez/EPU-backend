import paramiko
from io import BytesIO

class SFTPHandler:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.transport = None
        self.sftp = None

    def connect(self):
        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            return self
        except Exception as e:
            print(f"Error conectando a SFTP: {self.host}:{self.port} - {e}")
            raise

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

    def search_files(self, search_pattern, directory='.'):
        file_list = []
        for filename in self.sftp.listdir(directory):
            if search_pattern.lower() in filename.lower():
                file_list.append(filename)
        return file_list

    def download_files(self, filenames, directory='.'):
        files = {}
        for filename in filenames:
            file_data = BytesIO()
            remote_path = f"{directory}/{filename}" if directory != '.' else filename
            self.sftp.getfo(remote_path, file_data)
            file_data.seek(0)
            files[filename] = file_data
        return files
    
    def download_file(self, remote_path, local_path):
        try:
            """Descarga un archivo del SFTP y lo guarda en disco."""
            print(f"Descargando {remote_path} a {local_path}")
            self.sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"Error download_file: {e}")
            raise

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def close(self):
        if hasattr(self, 'sftp') and self.sftp:
            self.sftp.close()
        if hasattr(self, 'transport') and self.transport:
            self.transport.close()