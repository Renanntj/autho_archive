#!/usr/bin/env python3

import os
import shutil
import hashlib
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta

HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
BACKUP_DIR = HOME / "Downloads_Backup"
LOG_FILE = HOME / "auto_manager.log"
CLEANUP_DAYS = 30


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def organize_files():
    logging.info("Starting file organization.")

    categories = {
        "PDF": [".pdf"],
        "IMAGES": [".jpg", ".jpeg", ".png"],
        "ZIP": [".zip"],
        "DOCUMENTS": [".doc", ".docx", ".xls", ".xlsx"]
    }

    for category, extensions in categories.items():
        destination_folder = DOWNLOADS / category
        destination_folder.mkdir(exist_ok=True)

        for file in DOWNLOADS.iterdir():
            if file.is_file() and file.suffix.lower() in extensions:
                shutil.move(str(file), destination_folder / file.name)
                logging.info(f"Moved: {file.name} → {category}")

def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(block)
    return sha256_hash.hexdigest()

def remove_duplicates():
    logging.info("Checking for duplicate files.")
    hashes = {}

    for root, _, files in os.walk(DOWNLOADS):
        for name in files:
            path = Path(root) / name
            file_hash = calculate_hash(path)

            if file_hash in hashes:
                os.remove(path)
                logging.info(f"Duplicate removed: {path}")
            else:
                hashes[file_hash] = path

def incremental_backup():
    logging.info("Starting backup.")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(DOWNLOADS, BACKUP_DIR)
    logging.info("Backup completed.")

def clean_old_files():
    logging.info("Removing old files.")
    limit = datetime.now() - timedelta(days=CLEANUP_DAYS)

    for root, _, files in os.walk(DOWNLOADS):
        for name in files:
            path = Path(root) / name
            if datetime.fromtimestamp(path.stat().st_mtime) < limit:
                os.remove(path)
                logging.info(f"Old file removed: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organization and backup automation.")
    parser.add_argument("--organize", action="store_true")
    parser.add_argument("--duplicates", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.organize:
        organize_files()
    if args.duplicates:
        remove_duplicates()
    if args.backup:
        incremental_backup()
    if args.clean:
        clean_old_files()
    if args.all:
        organize_files()
        remove_duplicates()
        incremental_backup()
        clean_old_files()

    print("Execution finished.")