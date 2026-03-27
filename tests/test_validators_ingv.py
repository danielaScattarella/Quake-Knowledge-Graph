import pytest
import os
from utils.validators import (
    validate_ingv_dataset_url,
    validate_local_dataset_path,
    sanitize_input,
    validate_dataset_name
)

class TestValidators:

    def test_validate_ingv_dataset_url(self):
        # URL validi per dataset sismici INGV o fonti autorizzate
        assert validate_ingv_dataset_url("https://webservices.ingv.it/fdsnws/event/1/query?starttime=2026-03-20T00%3A00%3A00&endtime=2026-03-27T23%3A59%3A59&minmag=2&maxmag=10&mindepth=-10&maxdepth=1000&minlat=-90&maxlat=90&minlon=-180&maxlon=180&minversion=100&orderby=time-asc&format=text&limit=10000")
        assert validate_ingv_dataset_url("https://example.com/ingv/earthquakes.csv")

        # URL NON validi
        assert not validate_ingv_dataset_url("https://pippo.com/user/repo")
        assert not validate_ingv_dataset_url("not a url")
        assert not validate_ingv_dataset_url("")

    def test_validate_local_dataset_path(self):
        assert validate_local_dataset_path("query.txt")
        assert validate_local_dataset_path("data/query.csv")

        # Traversal: bloccare tentativi di uscita directory
        if os.sep == "/":
            assert not validate_local_dataset_path("../secret.txt")  

    def test_sanitize_input(self):
        assert sanitize_input("  roma  ") == "roma"
        assert sanitize_input("magnitudo\0extra") == "magnitudoextra"
        assert sanitize_input("") == ""

    def test_validate_dataset_name(self):
        assert validate_dataset_name("INGV Earthquakes 2024")
        assert validate_dataset_name("terremoti_italia_2023")
        assert validate_dataset_name("dataset-01")

        # NON validi
        assert not validate_dataset_name("Dataset!!")
        assert not validate_dataset_name("")