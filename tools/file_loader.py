# tools/file_loader.py

import os
import zipfile

# Estensioni tipiche dei dataset INGV
INGV_EXTENSIONS = (".txt", ".csv", ".json", ".xml")

# File di sistema irrilevanti
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}


def load_files_from_directory(directory, extensions=INGV_EXTENSIONS):
    """
    Carica file da una directory contenenti dataset sismici INGV.
    Non effettua esclusioni tipiche dei repository software.
    Restituisce:
        [
            {
                "path": "subfolder/file.txt",
                "content": "...raw content...",
                "size": 12345
            },
            ...
        ]
    """

    files = []

    try:
        for root, dirs, filenames in os.walk(directory):
            for fname in filenames:
                if fname in EXCLUDE_FILES:
                    continue

                path = os.path.join(root, fname)
                rel_path = os.path.relpath(path, directory)

                # accetta solo dataset INGV
                if not fname.lower().endswith(extensions):
                    continue

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    files.append({
                        "path": rel_path,
                        "content": content,
                        "size": len(content)
                    })

                except Exception:
                    continue

    except Exception as e:
        print(f"[ERROR] Errore durante la scansione directory: {e}")

    return files


def extract_zip_to_dir(zip_path, dest_dir):
    """
    Estrae ZIP contenente dataset INGV.
    """
    os.makedirs(dest_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest_dir)
    except Exception as e:
        print(f"[ERROR] Impossibile estrarre ZIP: {e}")

    return dest_dir