import sys
import os
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..'))
from src.SourceData import SourceData
import pytest
from dotenv import load_dotenv
from datetime import datetime



load_dotenv()

SOURCE_NAME = "TEST"+str(datetime.now())
SOURCE_NAME_INVALID = "INVALID"
USER_ID = 5000091


@pytest.mark.test
def test_insert_select():
    SourceData.insert_source_data(SOURCE_NAME)
    source_id = SourceData.get_source_data_id(SOURCE_NAME)
    source_id is not None


@pytest.mark.test
def test_select_invalid():
    source_id = SourceData.get_source_data_id(SOURCE_NAME_INVALID)
    source_id is None
