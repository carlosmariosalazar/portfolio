"""Test suit for the config management system."""

import json
from pathlib import Path
from typing import Any, Dict, Type

import pytest
from pydantic import BaseModel, ValidationError
from shared.src.utils.config_manager import (
    ConfigLoader,
    ConfigLoaderFactory,
    ConfigManager,
    JSONConfigLoader,
    YAMLConfigLoader,
)


class DatabaseTestConfig(BaseModel):
    """Test database configuration schema."""

    host: str
    port: int
    database: str
    username: str
    password:str

class AppTestConfig(BaseModel):
    """Test application configuration schema."""

    app_name: str
    debug: bool
    log_level: str


class TestJsonConfigLoader:
    """Test suite for JsonConfigLoader."""

    def test_load_valid_json_config(
        self,
        tmp_json_config: Path,
        valid_db_config_data: Dict[str, Any]
    ) -> None:
        """Test loading a valid JSON configuration file.

        :param temp_json_config: Path to temporary JSON file
        :type temp_json_config: Path
        :param valid_db_config_data: Expected config data
        :type valid_db_config_data: Dict[str, Any]
        """
        loader = JSONConfigLoader(model= DatabaseTestConfig)
        config = loader.load(tmp_json_config)

        assert isinstance(config, DatabaseTestConfig)
        assert config.host == valid_db_config_data["host"]
        assert config.port == valid_db_config_data["port"]
        assert config.database == valid_db_config_data["database"]

    def test_load_nonexistent_file(self) -> None:
        """Test loading a file that doesn't exist."""
        loader = JSONConfigLoader(DatabaseTestConfig)

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load(Path(__file__).parent / "nonexistent_config.json")

        assert "Config file not found" in str(exc_info.value)

    def test_load_invalid_json_syntax(self, tmp_invalid_json: Path) -> None:
        """Test loading an JSON file with invalid syntax"""
        loader = JSONConfigLoader(DatabaseTestConfig)

        with pytest.raises(ValueError, match= "Format error found in JSON file"):
            loader.load(tmp_invalid_json)

    def test_load_json_validation_error(
            self,
            tmp_path: Path,
            invalid_config_data: dict
            ) -> None:
        """Test loading JSON with data that fails Pydantic validation."""
        config_file = tmp_path / "invalid_schema.json"
        with config_file.open("w", encoding="utf-8") as f:
            json.dump(invalid_config_data, f)

        loader = JSONConfigLoader(DatabaseTestConfig)

        with pytest.raises(ValidationError) as exc_info:
            loader.load(config_file)

        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestYAMLConfigLoader:

    def test_load_yaml_config(
            self,
            tmp_yaml_config: Path,
            valid_app_config_data: Dict[str, Any]
            ) -> None:
        """Test loading a valid YAML configuration file"""
        loader = YAMLConfigLoader(model= AppTestConfig)
        config = loader.load(file_path= tmp_yaml_config)

        assert isinstance(config, AppTestConfig)
        assert config.app_name == valid_app_config_data["app_name"]
        assert config.debug == valid_app_config_data["debug"]
        assert config.log_level == valid_app_config_data["log_level"]


class TestConfigLoaderFactory:

    @pytest.mark.parametrize(
            argnames= ("extension", "expected_loader", "model"),
            argvalues= [
                (".json", JSONConfigLoader, DatabaseTestConfig),
                (".yaml", YAMLConfigLoader, AppTestConfig)
                ]
    )
    def test_get_loader_by_extension(
            self,
            extension: str,
            expected_loader: Type[ConfigLoader],
            model: Type[BaseModel],
            tmp_path: Path
            ) -> None:
        """Test factory creates correct loader for file extensions."""

        file_path = tmp_path / f"config.{extension}"

        loader = ConfigLoaderFactory.get_loader(
            file_path= file_path,
            model= model
            )

        assert isinstance(loader, expected_loader)

    def test_get_loader_unsupported_extension(
            self,
            tmp_path: Path
            ) -> None:
        """Test factory raises error for unsupported file extensions."""

        file_path = tmp_path / "config.toml"

        with pytest.raises(ValueError, match= "Unsupported file extension") as exc_info:
            ConfigLoaderFactory.get_loader(
                file_path= file_path,
                model= DatabaseTestConfig
                )

        assert ".toml" in str(exc_info.value)

    def test_register_custom_loader(
            self,
            tmp_path: Path
            ) -> None:
        """Test registering a custom loader class."""

        class CustomLoader(ConfigLoader):
            def _parse_file(self, file_path: Path) -> Dict[str, Any]:
                return {"_": file_path}

        ConfigLoaderFactory.register_loader(
            extension= ".custom",
            loader_class= CustomLoader
            )

        loader = ConfigLoaderFactory.get_loader(
            file_path= tmp_path / "file.custom",
            model= AppTestConfig
            )

        assert isinstance(loader, CustomLoader)

class TestConfigManager:

    def test_load_and_get_config(
            self,
            tmp_path: Path,
            config_manager: ConfigManager) -> None:
        """Test loading and retrieving a configuration."""

        config = config_manager.load_config(
            name= "database",
            file_path= tmp_path / "config.json",
            model= DatabaseTestConfig
            )

        assert isinstance(config, DatabaseTestConfig)

        retrieved = config_manager.get_config("database", DatabaseTestConfig)

        assert config == retrieved
        assert retrieved.host == "localhost"

    def test_load_nonexistent_config(self, config_manager: ConfigManager) -> None:
        """Test retrieving a configuration that wasn't loaded."""

        with pytest.raises(KeyError, match= "not loaded") as _:
            config_manager.get_config("nonexistent", DatabaseTestConfig)

    def test_load_config_invalid_model(
            self,tmp_path: Path,
            config_manager: ConfigManager
            ) -> None:
        """Test retreiving a configuration with invalid model."""

        config_manager.load_config(
            name= "database",
            file_path= tmp_path / "config.json",
            model= DatabaseTestConfig
            )

        with pytest.raises(TypeError, match= "expected") as _:
            config_manager.get_config("database", AppTestConfig)

    def test_has_config(
            self,
            tmp_path: Path,
            config_manager: ConfigManager
            ) -> None:
        """Test checking if a configuration exists."""

        assert not config_manager.has_config("database")

        config_manager.load_config(
            name= "database",
            file_path= tmp_path / "config.json",
            model= DatabaseTestConfig
            )

        assert config_manager.has_config("database")
