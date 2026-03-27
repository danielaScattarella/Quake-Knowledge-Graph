import pytest
import os
import tempfile
from pathlib import Path

from tools.file_loader import load_files_from_directory
from tools.text_splitter import split_text
from tools.data_analyzer import EarthquakeDataAnalyzer


# ============================================================
#  FILE LOADER TESTS
# ============================================================

class TestFileLoader:

    def test_load_files_from_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea alcuni file INGV validi
            f1 = os.path.join(tmpdir, "eventi.txt")
            f2 = os.path.join(tmpdir, "terremoti.csv")
            with open(f1, "w") as f:
                f.write("EventID|Time|Latitude|Longitude|Depth_Km\n1|a|b|c|d")
            with open(f2, "w") as f:
                f.write("EventID,Time,Latitude,Longitude,Depth_Km\n2,a,b,c,d")

            # Crea file da escludere
            with open(os.path.join(tmpdir, ".DS_Store"), "w") as f:
                f.write("ignored")

            files = load_files_from_directory(tmpdir)

            assert len(files) == 2
            paths = [f["path"] for f in files]
            assert "eventi.txt" in paths
            assert "terremoti.csv" in paths


# ============================================================
#  TEXT SPLITTER TESTS
# ============================================================

class TestTextSplitter:

    def test_split_text_dataset_not_splitted(self):
        ingv_text = (
            "EventID|Time|Latitude|Longitude|Depth_Km\n"
            "1|2023|42.1|12.5|10\n"
            "2|2023|40.2|14.1|12"
        )

        chunks = split_text(ingv_text)
        assert len(chunks) == 1  # non deve splittare dataset INGV

    def test_split_text_narrative(self):
        narrative = "a" * 2000
        chunks = split_text(narrative, chunk_size=500, chunk_overlap=50)
        assert len(chunks) > 1
        assert len(chunks[0]) <= 500


# ============================================================
#  EARTHQUAKE DATA ANALYZER TESTS
# ============================================================

class TestEarthquakeDataAnalyzer:

    def test_analyze_file_valid(self):
        content = (
            "EventID|Time|Latitude|Longitude|Depth_Km|Magnitude\n"
            "1|2023|42.1|12.5|10|3.5\n"
            "2|2023|40.0|15.0|12|4.0"
        )
        analyzer = EarthquakeDataAnalyzer()

        result = analyzer.analyze_file("test.txt", content)

        assert result["total_events"] == 2
        assert result["statistics"]["max_magnitude"] == 4.0
        assert len(result["anomalies"]) == 0

    def test_analyze_file_with_anomalies(self):
        content = (
            "EventID|Time|Latitude|Longitude|Depth_Km|Magnitude\n"
            "1|2023|999|12.5|10|3.5\n"        # latitudine non valida
            "2|2023|42.0|12.5|900|5.0"        # profondità anomala
        )
        analyzer = EarthquakeDataAnalyzer()

        result = analyzer.analyze_file("error.txt", content)

        assert result["total_events"] == 2
        assert len(result["anomalies"]) >= 2

    def test_analyze_file_empty(self):
        analyzer = EarthquakeDataAnalyzer()
        result = analyzer.analyze_file("empty.txt", "")

        assert result["error"] == "Empty file"
        assert result["events"] == []


# ============================================================
#  REPOSITORY-LIKE ANALYZER TEST (CONCLUSION FROM TRUNCATED MESSAGE)
# ============================================================

class TestCodeAnalyzerEquivalent:

    def test_basic_repository_analysis(self):
        # Simulazione mini-repository con file INGV e README
        files = [
            {"path": "eventi.txt", "content": "EventID|Time|Latitude|Longitude|Depth_Km\n1|2023|42|12|10"},
            {"path": "README.md", "content": "# Dataset INGV"}
        ]

        analyzer = EarthquakeDataAnalyzer()
        result = analyzer.analyze_file("eventi.txt", files[0]["content"])

        assert result["total_events"] == 1
        assert "statistics" in result