import os
import time

# Base path where folders will be created
BASE_PATH = "test_folder"

# Function to create folders with a delay


def create_folders_with_delay():
    for i in range(1, 22):  # 21 folders (1 to 21)
        folder_path = os.path.join(BASE_PATH, f"Folder_{i}")
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")
        time.sleep(3)  # Delay of 30 seconds


if __name__ == "__main__":
    create_folders_with_delay()
