"""Config file validation system using Pydantic models.

This module implements a flexible configuration management system.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Dict, Generic, Type, TypeVar

import yaml
from pydantic import BaseModel

T = TypeVar(name="T", bound=BaseModel)


class ConfigLoader(ABC, Generic[T]):
    """Abstract base class for config file loaders.

    Defines the interface for loading and validating configuration files
    using Pydantic models.
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the config loader with a Pydantic model.

        :param model: Pydantic model class for validation
        :type model: Type[T]
        """
        self._model = model

    @abstractmethod
    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse the config file and return raw data.

        :param file_path: Path to the configuration file
        :type file_path: Path
        :return: Parsed configuration data
        :rtype: Dict[str, Any]
        """
        ...

    def load(self, file_path: Path) -> T:
        """Load and validate configuration from file.

        :param file_path: Path to the configuration file
        :type file_path: Path
        :return: Validated Pydantic model instance
        :rtype: T
        :raises FileNotFoundError: If config file doesn't exist
        :raises ValidationError: If config doesn't match schema
        """
        if not file_path.exists():
            msg = f"Config file not found: {file_path}"
            raise FileNotFoundError(msg)

        raw = self._parse_file(file_path=file_path)
        return self._model.model_validate(obj=raw)


class JSONConfigLoader(ConfigLoader[T]):
    """JSON configuration file loader."""

    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON configuration file.

        :param file_path: Path to JSON file
        :type file_path: Path
        :return: Parsed JSON data
        :rtype: Dict[str, Any]
        :raises ValueError: If JSON file has a format error
        """
        try:
            with file_path.open(mode="r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            msg = f"Format error found in JSON file {file_path.name}"
            raise ValueError(msg) from e


class YAMLConfigLoader(ConfigLoader[T]):
    """YAML configuration file loader."""

    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        with file_path.open(mode="r", encoding="utf-8") as f:
            return yaml.safe_load(f)


class ConfigLoaderFactory:
    """Factory for creating appropriate config loaders.

    Maps file extensions to loader classes
    """

    _loaders: ClassVar[Dict[str, Type[ConfigLoader]]] = {
        ".json": JSONConfigLoader,
        ".yaml": YAMLConfigLoader,
    }

    @classmethod
    def register_loader(cls, extension: str, loader_class: Type[ConfigLoader]) -> None:
        """Register a new config loader for a file extension.

        :param extension: File extension (e.g., '.toml')
        :type extension: str
        :param loader_class: Loader class to handle this extension
        :type loader_class: Type[ConfigLoader]
        """
        cls._loaders[extension] = loader_class

    @classmethod
    def get_loader(cls, file_path: Path, model: Type[T]) -> ConfigLoader:
        """Get appropriate loader based on file extension.

        :param file_path: Path to configuration file
        :type file_path: str | Path
        :param model: Pydantic model for validation
        :type model: Type[T]
        :return: Appropriate config loader instance
        :rtype: ConfigLoader[T]
        :raises ValueError: If file extension is not supported
        """
        extension = file_path.suffix.lower()

        if extension not in cls._loaders:
            msg = f"""
            Unsupported file extension: {extension}.
            Supported: {list(cls._loaders.keys())}
            """
            raise ValueError(msg)

        loader_class = cls._loaders[extension]
        return loader_class(model)


class ConfigManager:
    """High-level config manager.

    Provides a simple interface for loading various config files.
    """

    def __init__(self) -> None:
        """Initialize the config manager."""
        self._configs: Dict[str, BaseModel] = {}

    def load_config(self, name: str, file_path: Path, model: Type[T]) -> T:
        """Load and cache a configuration file.

        :param name: Identifier for this configuration
        :type name: str
        :param file_path: Path to configuration file
        :type file_path: str | Path
        :param model: Pydantic model for validation
        :type model: Type[T]
        :return: Validated configuration model
        :rtype: T
        """
        loader = ConfigLoaderFactory.get_loader(file_path, model)
        config = loader.load(file_path)
        self._configs[name] = config
        return config

    def get_config(self, name: str, model: Type[T]) -> T:
        """Retrieve a cached configuration.

        :param name: Configuration identifier
        :type name: str
        :param model: Expected Pydantic model type for type checking.
        :type model: Type[T]
        :return: Cached configuration model with proper type
        :rtype: T
        :raises KeyError: If configuration not found
        """
        if name not in self._configs:
            msg = f"Configuration '{name}' not loaded"
            raise KeyError(msg)

        config = self._configs[name]

        if not isinstance(config, model):
            msg = f"""
            Configuration '{name}' is of type {Type[config].__name__},
            expected '{model.__name__}'
            """
            raise TypeError(msg)

        return config

    def has_config(self, name: str) -> bool:
        """Check if a configuration is loaded.

        :param name: Configuration identifier
        :type name: str
        :return: True if config exists
        :rtype: bool
        """
        return name in self._configs
