import os
import shutil
import time
import hashlib
import argparse
from datetime import datetime

def calculate_hash(file_path):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def log_message(log_path, message):
    """Logs a message to the console and to the log file."""
    full_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(full_message)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(full_message + "\n")

def synchronize_folders(source, replica, log_path):
    """Synchronizes the source folder with the replica folder."""

    # Ensure the replica folder exists
    if not os.path.exists(replica):
        os.makedirs(replica)
        log_message(log_path, f"🗂 Created replica folder: {replica}")

    # Synchronize files and subfolders from source to replica
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        destination_path = os.path.join(replica, relative_path)

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
            log_message(log_path, f"📁 Created folder: {destination_path}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(destination_path, file)

            if not os.path.exists(replica_file) or \
                    calculate_hash(source_file) != calculate_hash(replica_file):
                shutil.copy2(source_file, replica_file)
                log_message(log_path, f"📄 Copied file: {source_file} ➡️ {replica_file}")

    # Remove extra files and folders from the replica that no longer exist in the source
    for root, dirs, files in os.walk(replica, topdown=False):
        relative_path = os.path.relpath(root, replica)
        source_path = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_path, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                log_message(log_path, f"❌ Removed file: {replica_file}")

        for folder in dirs:
            replica_folder = os.path.join(root, folder)
            source_folder = os.path.join(source_path, folder)

            if not os.path.exists(source_folder):
                shutil.rmtree(replica_folder)
                log_message(log_path, f"❌ Removed folder: {replica_folder}")

def main():
    parser = argparse.ArgumentParser(description="Folder Synchronizer (source ➡️ replica)")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval (in seconds)")
    parser.add_argument("log", help="Path to the log file")

    args = parser.parse_args()

    source = args.source
    replica = args.replica
    interval = args.interval
    log_path = args.log

    if not os.path.exists(source):
        print(f"Error: Source folder '{source}' does not exist.")
        return

    log_message(log_path, "🚀 Starting folder synchronizer...")
    log_message(log_path, f"📂 Source folder: {source}")
    log_message(log_path, f"📂 Replica folder: {replica}")
    log_message(log_path, f"⏱ Interval: {interval} seconds")
    log_message(log_path, f"📝 Log file: {log_path}")

    while True:
        synchronize_folders(source, replica, log_path)
        log_message(log_path, "✅ Synchronization completed.")
        time.sleep(interval)

if __name__ == "__main__":
    main()
