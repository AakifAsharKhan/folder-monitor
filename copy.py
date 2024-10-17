import os
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Folder to watch
WATCHED_DIR = "test_folder"
# Destination folder where modified folders will be copied
DEST_DIR = "G:\My Drive\TEST!"

# Initialize logging
logging.basicConfig(filename="upload_log.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

# Function to copy a folder to the destination
def copy_folder_to_destination(folder_path):
    folder_name = os.path.basename(folder_path)
    dest_path = os.path.join(DEST_DIR, folder_name)

    try:
        # Copy the folder and its contents to the destination
        shutil.copytree(folder_path, dest_path)
        logging.info(f"Copied folder: {folder_name} to {DEST_DIR}")
        print(f"Copied folder: {folder_name} to {DEST_DIR}")  # Debug print
    except Exception as e:
        logging.error(f"Failed to copy {folder_name}: {e}")
        print(f"Failed to copy {folder_name}: {e}")  # Debug print

# Event handler for folder changes
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.modified_folders = set()

    # Handle both folder creation and modification events
    def on_modified(self, event):
        self.handle_event(event)

    def on_created(self, event):
        self.handle_event(event)

    def handle_event(self, event):
        if event.is_directory:
            print(f"Detected change in directory: {event.src_path}")  # Debug print
            self.modified_folders.add(event.src_path)
            print(f"Folders pending copy: {self.modified_folders}")  # Debug print
            if len(self.modified_folders) >= 10:
                self.process_and_copy()

    def process_and_copy(self):
        modified_list = list(self.modified_folders)[:10]
        for folder_path in modified_list:
            try:
                copy_folder_to_destination(folder_path)
                shutil.rmtree(folder_path)  # Delete folder after copying
                logging.info(f"Copied and deleted folder: {folder_path}")
                print(f"Copied and deleted folder: {folder_path}")  # Debug print
            except Exception as e:
                logging.error(f"Error processing folder {folder_path}: {e}")
                print(f"Error processing folder {folder_path}: {e}")  # Debug print
            finally:
                self.modified_folders.remove(folder_path)

# Main function to monitor folder
def monitor_folder():
    event_handler = FolderChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
            print("Monitoring for folder changes...")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Ensure the destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)
    monitor_folder()
