import os
import shutil
import argparse
from datetime import datetime

def reformat_storage(captured_birds_dir, storage_dir, dry_run, suffix=""):
    if not os.path.exists(captured_birds_dir):
        print(f"Directory {captured_birds_dir} does not exist.")
        return

    for filename in os.listdir(captured_birds_dir):
        if filename.startswith("bird_") and filename.endswith(".jpg"):
            filename_str = filename.replace(suffix, '')
            timestamp_str = filename_str[5:-4]  # Extract timestamp
            try:
                timestamp = int(timestamp_str)
                dt = datetime.fromtimestamp(timestamp)
                year = dt.strftime("%Y")
                month = dt.strftime("%m")
                day = dt.strftime("%d")
                time = dt.strftime("%H-%M-%S")

                # Create target directory
                target_dir = os.path.join(storage_dir, f"{year}", f"{month}", f"{day}")

                if not dry_run:
                    os.makedirs(target_dir, exist_ok=True)

                # Move and rename the file
                source_path = os.path.join(captured_birds_dir, filename)
                target_path = os.path.join(target_dir, f"{time}{suffix}.jpg")

                if dry_run:
                    print(f"Would move {filename} to {target_path}")
                else:
                    shutil.move(source_path, target_path)
                    print(f"Moved {filename} to {target_path}")

            except ValueError:
                print(f"Invalid timestamp in filename: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reformat storage of captured birds images.")
    parser.add_argument("--dry", action="store_true", help="Run in dry mode, do not create folders or move files.")
    parser.add_argument("--suffix", type=str, default="", help="Suffix to add to folder and filename.")
    args = parser.parse_args()

    captured_birds_dir = f"captured_birds{args.suffix}"
    storage_dir = f"storage{args.suffix}"
    reformat_storage(captured_birds_dir, storage_dir, args.dry, args.suffix)
