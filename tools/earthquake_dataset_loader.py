# tools/earthquake_dataset_loader.py

import os
import zipfile
import shutil
from pathlib import Path


class EarthquakeDatasetLoader:
    """
    Strumento per gestire dataset di terremoti INGV.
    Funzioni:
      - caricare directory locali
      - estrarre ZIP contenenti dataset
      - validare file (TXT / CSV / JSON / XML)
      - preparare strutture per dataset multi-giorno
    """

    VALID_EXTENSIONS = {".txt", ".csv", ".json", ".xml"}
    IGNORE_FILES = {".DS_Store", "Thumbs.db"}

    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.getcwd(), "earthquake_workspace")

        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)

    # ----------------------------------------------------------------------

    def load_from_path(self, path: str) -> str:
        """
        Carica dataset da:
          - cartella
          - file singolo
          - archivio ZIP
        Restituisce sempre un path a una directory contenente i file.
        """

        path = Path(path)

        # Caso 1: ZIP
        if path.is_file() and path.suffix.lower() == ".zip":
            return self._extract_zip(path)

        # Caso 2: Singolo file (TXT/CSV/JSON/XML)
        if path.is_file():
            if path.suffix.lower() not in self.VALID_EXTENSIONS:
                raise ValueError(f"Formato file non valido per dataset INGV: {path.suffix}")
            return self._prepare_single_file(path)

        # Caso 3: Directory già esistente
        if path.is_dir():
            return str(path)

        raise FileNotFoundError(f"Percorso non valido: {path}")

    # ----------------------------------------------------------------------

    def _extract_zip(self, zip_path: Path) -> str:
        """Estrae lo ZIP in una nuova subdirectory del workspace."""
        target_dir = os.path.join(self.workspace_dir, zip_path.stem)
        os.makedirs(target_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(target_dir)
            return target_dir
        except Exception as e:
            raise Exception(f"Errore durante l’estrazione ZIP: {e}")

    # ----------------------------------------------------------------------

    def _prepare_single_file(self, file_path: Path) -> str:
        """
        Copia un singolo file dataset in una directory dedicata
        per facilitarne l'analisi pipeline.
        """

        target_dir = os.path.join(self.workspace_dir, f"{file_path.stem}_dataset")
        os.makedirs(target_dir, exist_ok=True)

        shutil.copy(file_path, target_dir)
        return target_dir

    # ----------------------------------------------------------------------

    def list_dataset_files(self, directory: str) -> list:
        """
        Restituisce lista di file INGV validi nella directory.
        """
        dataset_files = []

        for root, _, files in os.walk(directory):
            for f in files:
                if f in self.IGNORE_FILES:
                    continue
                ext = os.path.splitext(f)[1].lower()
                if ext in self.VALID_EXTENSIONS:
                    fullpath = os.path.join(root, f)
                    dataset_files.append(fullpath)

        return dataset_files

    # ----------------------------------------------------------------------

    def clean_workspace(self):
        """Cancella completamente il workspace dei dataset."""
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir, ignore_errors=True)
            os.makedirs(self.workspace_dir, exist_ok=True)
