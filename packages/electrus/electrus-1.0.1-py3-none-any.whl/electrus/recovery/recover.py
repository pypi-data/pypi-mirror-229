import os
import zipfile
import tarfile
import json

class Recovery:
    def __init__(self, client):
        """
        Initialize the Recovery instance.

        Args:
            client: The Electus client.

        Usage:
            recovery = Recovery(client)
        """
        self.client = client

    def backup(self, database, path=None, format='zip'):
        """
        Create a backup of a Electus database.

        Args:
            database (str): The name of the database to backup.
            path (str, optional): The path to save the backup file.
            format (str, optional): The format of the backup ('zip', 'tar', or 'json').

        Returns:
            str: A message indicating the result of the backup.

        Usage:
            result = recovery.backup('mydb', path='/backup', format='zip')
        """
        try:
            if self.client._is_local:
                if not self._is_database_exist(database):
                    return f"Database '{database}' does not exist."

                if not path:
                    path = os.path.join(os.getcwd(), 'backup')
                    os.makedirs(path, exist_ok=True)

                backup_path = os.path.join(path, f'{database}.{format}')
                if format == 'zip':
                    self._create_zip_backup(database, backup_path)
                elif format == 'tar':
                    self._create_tar_backup(database, backup_path)
                elif format == 'json':
                    self._create_json_backup(database, backup_path)
                else:
                    raise ValueError("Unsupported backup format.")

                return f"Backup of '{database}' created at '{backup_path}'."
            else:
                return "Connection failed! Electus is not connected."
        except Exception as e:
            return f"Error creating backup: {str(e)}"

    def _is_database_exist(self, database):
        return os.path.exists(os.path.join(self.client.data_dir, database))

    def _create_zip_backup(self, database, backup_path):
        source_dir = os.path.join(self.client.data_dir, database)
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

    def _create_tar_backup(self, database, backup_path):
        source_dir = os.path.join(self.client.data_dir, database)
        with tarfile.open(backup_path, 'w') as tarf:
            tarf.add(source_dir, arcname=os.path.basename(source_dir))

    def _create_json_backup(self, database, backup_path):
        source_dir = os.path.join(self.client.data_dir, database)
        data = {'database': database, 'files': {}}
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                with open(file_path, 'rb') as f:
                    data['files'][relative_path] = f.read().decode('utf-8')

        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=4)

    def restore(self, path, format='zip'):
        """
        Restore a Electus database from a backup file.

        Args:
            path (str): The path to the backup file.
            format (str, optional): The format of the backup ('zip', 'tar', or 'json').

        Returns:
            str: A message indicating the result of the restore.

        Usage:
            result = recovery.restore('/backup/mydb.zip', format='zip')
        """
        try:
            if self.client._is_local:
                if format == 'zip':
                    self._extract_zip_restore(path)
                elif format == 'tar':
                    self._extract_tar_restore(path)
                elif format == 'json':
                    self._extract_json_restore(path)
                else:
                    raise ValueError("Unsupported backup format.")

                return f"Database restored from '{format}' backup."
            else:
                return "Connection failed! Electus is not connected."
        except Exception as e:
            return f"Error restoring database: {str(e)}"

    def _extract_zip_restore(self, backup_path):
        if not os.path.exists(backup_path):
            raise ValueError("Backup file not found.")

        restored_folder = os.path.splitext(os.path.basename(backup_path))[0]
        target_path = os.path.join(os.path.expanduser("~"), '.electrus', restored_folder)

        os.makedirs(target_path, exist_ok=True)
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(target_path)

    def _extract_tar_restore(self, backup_path):
        if not os.path.exists(backup_path):
            raise ValueError("Backup file not found.")

        restored_folder = os.path.splitext(os.path.basename(backup_path))[0]
        target_path = os.path.join(os.path.expanduser("~"), '.electrus', restored_folder)

        os.makedirs(target_path, exist_ok=True)
        with tarfile.open(backup_path, 'r') as tarf:
            tarf.extractall(target_path)

    def _extract_json_restore(self, backup_path):
        if not os.path.exists(backup_path):
            raise ValueError("Backup file not found.")

        with open(backup_path, 'r') as f:
            data = json.load(f)

        restored_folder = data['database']
        target_path = os.path.join(os.path.expanduser("~"), '.electrus', restored_folder)

        os.makedirs(target_path, exist_ok=True)
        for relative_path, content in data['files'].items():
            file_path = os.path.join(target_path, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(content.encode('utf-8'))
