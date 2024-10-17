import os
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import LoggingEventHandler
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Folder to watch
WATCHED_DIR = "test_folder"

# Initialize logging
logging.basicConfig(filename="upload_log.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

# Google Drive authentication


def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("credentials.json")
    gauth.LocalWebserverAuth()  # Opens a local webserver to handle OAuth authentication
    # gauth.SaveCredentialsFile("credentials.json")
    return GoogleDrive(gauth)

# Function to upload folder to Google Drive


def upload_folder(drive, folder_path):
    folder_name = os.path.basename(folder_path)
    folder_metadata = {"title": folder_name,
                       "mimeType": "application/vnd.google-apps.folder"}
    drive_folder = drive.CreateFile(folder_metadata)
    drive_folder.Upload()

    # Upload files in the folder
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            try:
                file_path = os.path.join(root, file_name)
                file_drive = drive.CreateFile(
                    {"title": file_name, "parents": [{"id": drive_folder["id"]}]})
                file_drive.SetContentFile(file_path)
                file_drive.Upload()
            except Exception as e:
                logging.error(f"Failed to upload {file_name}: {e}")

    return folder_name

# Event handler for folder changes


class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, drive):
        self.modified_folders = set()
        self.drive = drive

    def on_modified(self, event):
        if event.is_directory:
            self.modified_folders.add(event.src_path)
            if len(self.modified_folders) >= 1:
                self.process_and_upload()

    def process_and_upload(self):
        modified_list = list(self.modified_folders)[:1]
        for folder_path in modified_list:
            try:
                folder_name = upload_folder(self.drive, folder_path)
                shutil.rmtree(folder_path)  # Delete folder after upload
                logging.info(f"Uploaded and deleted folder: {folder_name}")
            except Exception as e:
                logging.error(f"Error processing folder {folder_path}: {e}")
            finally:
                self.modified_folders.remove(folder_path)

# Main function to monitor folder


def monitor_folder():
    drive = authenticate_drive()
    event_handler = FolderChangeHandler(drive)
    # event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    monitor_folder()
