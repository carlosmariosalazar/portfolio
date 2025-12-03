"""Shared module test fixtures."""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from shared.src.utils.config_manager import ConfigManager


@pytest.fixture
def tmp_path() -> Path:
    """Create a temporal path for storing test config files.

    :return: Temporal path
    :rtype: Path
    """
    path = Path(__file__).parent / "tmp"
    path.mkdir(parents= False, exist_ok= True)
    return path

@pytest.fixture
def valid_db_config_data() -> Dict[str,Any]:
    """Provide a valid test configuration data.

    :return: Valid config dictionary
    :rtype: Dict[str,Any]
    """
    return {
        "host": "localhost",
        "port": 4321,
        "database": "testdb",
        "username": "admin",
        "password": "123"
    }

@pytest.fixture
def valid_app_config_data() -> Dict[str, Any]:
    """Provide a valid test application configuration data.

    :return: Valid config dictionary
    :rtype: Dict[str, Any]
    """
    return {
        "app_name": "app",
        "debug": True,
        "log_level": "DEBUG"
    }

@pytest.fixture
def invalid_config_data() -> Dict[str, Any]:
    """Provide invalid configurationd data.

    :return: Invalid config dictionary with missing fields
    :rtype: Dict[str, Any]
    """
    return {
        "host": "localhost",
        "port": "invalid_port",
        "database": "testdb",
    }

@pytest.fixture
def tmp_json_config(tmp_path: Path, valid_db_config_data: Dict[str, Any]) -> Path:
    """Write a valid JSON config in a temporary path.

    :param tmp_path: Temporary path for testing
    :type tmp_path: Path
    :param valid_db_config_data: Valid config dictionary
    :type valid_db_config_data: Dict[str, Any]
    """
    config_file_path = tmp_path / "config.json"

    with config_file_path.open(mode= "w", encoding= "utf-8") as f:
        json.dump(valid_db_config_data, f, indent= 4)
    return config_file_path

@pytest.fixture
def tmp_yaml_config(tmp_path: Path, valid_app_config_data: Dict[str, Any]) -> Path:
    """Create a temporary YAML config file.

    :param tmp_path: Temporary path for testing
    :type tmp_path: Path
    :param valid_app_config_data: Valid config data
    :type valid_app_config_data: Dict[str, Any]
    :return: Path to temporary YAML file
    :rtype: Path
    """
    config_file = tmp_path / "config.yaml"
    with config_file.open("w", encoding="utf-8") as f:
        yaml.dump(valid_app_config_data, f)
    return config_file

@pytest.fixture
def tmp_invalid_json_config(
    tmp_path: Path,
    invalid_config_data: Dict[str, Any]
    ) -> Path:
    """Write an invalid JSON config in a temporary path.

    :param tmp_path: Temporary path
    :type tmp_path: Path
    :param invalid_db_config_data: Invalid config dictionary
    :type invalid_db_config_data: Dict[str, Any]
    """
    config_file_path = tmp_path / "invalid_config.json"

    with config_file_path.open(mode= "w", encoding= "utf-8") as f:
        json.dump(invalid_config_data, f, indent= 4)
    return config_file_path

@pytest.fixture
def tmp_invalid_json(tmp_path: Path) -> Path:
    """Create a temporary invalid JSON file.

    :param tmp_path: Pytest's temporary directory fixture
    :type tmp_path: Path
    :return: Path to temporary invalid JSON file
    :rtype: Path
    """
    config_file = tmp_path / "invalid.json"

    with config_file.open('w', encoding='utf-8') as f:
        f.write("{invalid json content")
    return config_file

@pytest.fixture
def config_manager() -> ConfigManager:
    """Provide a `ConfigManager` instance.

    :return: `ConfigManager` instance
    :rtype: ConfigManager
    """
    return ConfigManager()
