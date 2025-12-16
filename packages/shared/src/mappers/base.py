"""Simplified DTO-ORM Mapping system with unidirectional mappers.

This module implements a clean mapping system between Pydantic DTOs
and ORM models with separate responsibilities for creation and querying.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel
from shared.src.orm.base import Base

TCreateDTO = TypeVar("TCreateDTO", bound=BaseModel)
TQueryDTO = TypeVar("TQueryDTO", bound=BaseModel)
TOrm = TypeVar("TOrm", bound= Base)


class ToORMMapper(ABC, Generic[TCreateDTO, TOrm]):
    """Abstract mapper for converting Create DTOs to ORM models.

    Handles the creation flow: CreateDTO → ORM (for database inserts).
    """

    @abstractmethod
    def to_orm(self, dto: TCreateDTO) -> TOrm:
        """Convert Create DTO to new ORM instance.

        :param dto: Data Transfer Object for creation
        :type dto: TCreateDTO
        :return: New ORM model instance
        :rtype: TOrm
        """
        ...

class ToDTOMapper(ABC, Generic[TOrm, TQueryDTO]):
    """Abstract mapper for converting ORM models to Query DTOs.

    Handles the query flow: ORM → QueryDTO (for API responses).
    """

    @abstractmethod
    def to_dto(self, orm: TOrm) -> TQueryDTO:
        """Convert ORM model to Query DTO.

        :param orm: ORM model instance
        :type orm: TOrm
        :return: Query Data Transfer Object
        :rtype: TQueryDTO
        """
        ...


class AutoToORMMapper(ToORMMapper[TCreateDTO, TOrm]):
    """Automatic mapper for simple Create DTO to ORM conversions.

    Uses field name conventions for straightforward mappings without relationships.
    """

    def __init__(
        self,
        dto_class: Type[TCreateDTO],
        orm_class: Type[TOrm],
        field_transformers: Optional[Dict[str, Callable[[Any], Any]]] = None,
    ) -> None:
        """Initialize auto to-orm mapper.

        :param dto_class: Create DTO class type
        :type dto_class: Type[TCreateDTO]
        :param orm_class: ORM class type
        :type orm_class: Type[TOrm]
        :param field_transformers: Custom transformations per field
        :type field_transformers: Optional[Dict[str, Callable[[Any], Any]]]
        """
        self._dto_class = dto_class
        self._orm_class = orm_class
        self._field_transformers = field_transformers or {}

    def to_orm(self, dto: TCreateDTO) -> TOrm:
        """Convert Create DTO to new ORM instance.

        :param dto: Create DTO
        :type dto: TCreateDTO
        :return: New ORM instance
        :rtype: TOrm
        """
        orm_instance = self._orm_class()
        dto_dict = dto.model_dump()

        for field_name, value in dto_dict.items():
            if field_name in self._field_transformers:
                value = self._field_transformers[field_name](value)

            if hasattr(orm_instance, field_name):
                setattr(orm_instance, field_name, value)

        return orm_instance


class AutoToDTOMapper(ToDTOMapper[TOrm, TQueryDTO]):
    """Automatic mapper for simple ORM to Query DTO conversions.

    Uses field name conventions for straightforward mappings without relationships.
    """

    def __init__(self, orm_class: Type[TOrm], dto_class: Type[TQueryDTO]) -> None:
        """Initialize auto to-dto mapper.

        :param orm_class: ORM class type
        :type orm_class: Type[TOrm]
        :param dto_class: Query DTO class type
        :type dto_class: Type[TQueryDTO]
        """
        self._orm_class = orm_class
        self._dto_class = dto_class

    def to_dto(self, orm: TOrm) -> TQueryDTO:
        """Convert ORM to Query DTO using from_attributes.

        :param orm: ORM instance
        :type orm: TOrm
        :return: Query DTO
        :rtype: TQueryDTO
        """
        return self._dto_class.model_validate(orm)


class ManualToORMMapper(ToORMMapper[TCreateDTO, TOrm]):
    """Manual mapper with full control for complex Create DTO to ORM conversions.

    Useful for entities with relationships or complex business logic.
    """

    def __init__(
        self,
        dto_class: Type[TCreateDTO],
        orm_class: Type[TOrm],
        mapping_func: Callable[[TCreateDTO], TOrm],
    ) -> None:
        """Initialize manual to-orm mapper.

        :param dto_class: Create DTO class type
        :type dto_class: Type[TCreateDTO]
        :param orm_class: ORM class type
        :type orm_class: Type[TOrm]
        :param mapping_func: Custom mapping function
        :type mapping_func: Callable[[TCreateDTO], TOrm]
        """
        self._dto_class = dto_class
        self._orm_class = orm_class
        self._mapping_func = mapping_func

    def to_orm(self, dto: TCreateDTO) -> TOrm:
        """Convert Create DTO to ORM using custom function.

        :param dto: Create DTO
        :type dto: TCreateDTO
        :return: New ORM instance
        :rtype: TOrm
        """
        return self._mapping_func(dto)


class ManualToDTOMapper(ToDTOMapper[TOrm, TQueryDTO]):
    """Manual mapper with full control for complex ORM to Query DTO conversions.

    Essential for entities with relationships that need nested DTOs.
    """

    def __init__(
        self,
        orm_class: Type[TOrm],
        dto_class: Type[TQueryDTO],
        mapping_func: Callable[[TOrm], TQueryDTO],
    ) -> None:
        """Initialize manual to-dto mapper.

        :param orm_class: ORM class type
        :type orm_class: Type[TOrm]
        :param dto_class: Query DTO class type
        :type dto_class: Type[TQueryDTO]
        :param mapping_func: Custom mapping function
        :type mapping_func: Callable[[TOrm], TQueryDTO]
        """
        self._orm_class = orm_class
        self._dto_class = dto_class
        self._mapping_func = mapping_func

    def to_dto(self, orm: TOrm) -> TQueryDTO:
        """Convert ORM to Query DTO using custom function.

        :param orm: ORM instance
        :type orm: TOrm
        :return: Query DTO
        :rtype: TQueryDTO
        """
        return self._mapping_func(orm)

class MapperRegistry:
    """Registry for managing unidirectional mappers.

    Maintains separate registries for CreateDTO→ORM and ORM→QueryDTO mappings.
    """

    def __init__(self) -> None:
        """Initialize mapper registries."""
        self._to_orm_mappers: Dict[Tuple[Type, Type], ToORMMapper] = {}
        self._to_dto_mappers: Dict[Tuple[Type, Type], ToDTOMapper] = {}

    def register_to_orm(
            self,
            dto_class: Type[TCreateDTO],
            orm_class: Type[TOrm],
            mapper: ToORMMapper[TCreateDTO, TOrm]
            ) -> None:
        """Register a CreateDTO to ORM mapper.

        :param dto_class: Create DTO class
        :type dto_class: Type[TCreateDTO]
        :param orm_class: ORM class
        :type orm_class: Type[TOrm]
        :param mapper: Mapper instance
        :type mapper: ToORMMapper[TCreateDTO, TOrm]
        """
        key = (dto_class, orm_class)
        self._to_orm_mappers[key] = mapper

    def register_to_dto(
            self,
            orm_class: Type[TOrm],
            dto_class: Type[TQueryDTO],
            mapper: ToDTOMapper[TOrm, TQueryDTO]
        ) -> None:
        """Register an ORM to QueryDTO mapper.

        :param orm_class: ORM class
        :type orm_class: Type[TOrm]
        :param dto_class: Query DTO class
        :type dto_class: Type[TQueryDTO]
        :param mapper: Mapper instance
        :type mapper: ToDTOMapper[TOrm, TQueryDTO]
        """
        key = (orm_class, dto_class)
        self._to_dto_mappers[key] = mapper

    def to_orm(
            self,
            dto: TCreateDTO, # type: ignore
            orm_class: Type[TOrm]
        ) -> TOrm:
        """Map Create DTO to ORM using registered mapper.

        :param dto: Create DTO instance
        :type dto: TCreateDTO
        :param orm_class: Target ORM class
        :type orm_class: Type[TOrm]
        :return: New ORM instance
        :rtype: TOrm
        :raises KeyError: If no mapper registered
        """
        key = (type(dto), orm_class)

        if key not in self._to_orm_mappers:
            msg = f"""
            No to_orm mapper registered for {type(dto).__name__} -> {orm_class.__name__}
            """
            raise KeyError(msg)

        mapper = self._to_orm_mappers[key]
        return mapper.to_orm(dto)

    def to_dto(
            self,
            orm: TOrm, # type: ignore
            dto_class: Type[TQueryDTO]
        ) -> TQueryDTO:
        """Map ORM to Query DTO using registered mapper.

        :param orm: ORM instance
        :type orm: TOrm
        :param dto_class: Target Query DTO class
        :type dto_class: Type[TQueryDTO]
        :return: Query DTO instance
        :rtype: TQueryDTO
        :raises KeyError: If no mapper registered
        """
        key = (type(orm), dto_class)

        if key not in self._to_dto_mappers:
            msg = f"""
            No to_dto mapper registered for {type(orm).__name__} -> {dto_class.__name__}
            """
            raise KeyError(msg)

        mapper = self._to_dto_mappers[key]
        return mapper.to_dto(orm)

    def to_dto_list(
        self,
        orm_list: List[TOrm],
        dto_class: Type[TQueryDTO]
    ) -> List[TQueryDTO]:
        """Map list of ORM instances to Query DTOs.

        :param orm_list: List of ORM instances
        :type orm_list: List[TOrm]
        :param dto_class: Target Query DTO class
        :type dto_class: Type[TQueryDTO]
        :return: List of Query DTOs
        :rtype: List[TQueryDTO]
        """
        return [self.to_dto(orm, dto_class) for orm in orm_list]

    def to_orm_list(
            self,
            dto_list: List[TCreateDTO],
            orm_class: Type[TOrm]
        ) -> List[TOrm]:
        """Map list of Create DTO to ORM instances.

        :param dto_list: List of Create DTOs
        :type dto_list: List[TCreateDTO]
        :param orm_class: Target ORM class
        :type orm_class: Type[TOrm]
        :return: List of ORM instances
        :rtype: List[TOrm]
        """
        return [self.to_orm(dto, orm_class) for dto in dto_list]
