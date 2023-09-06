from abc import ABC, abstractmethod
from typing import Self
from uuid import uuid4

from trainerbase.memory import Address, make_address, pm


class GameObject(ABC):
    DPG_TAG_PREFIX = "object__"
    DPG_TAG_POSTFIX_IS_FROZEN = "__frozen"
    DPG_TAG_POSTFIX_GETTER = "__getter"
    DPG_TAG_POSTFIX_SETTER = "__setter"

    updated_objects: list[Self] = []

    @staticmethod
    @abstractmethod
    def pm_read(address: int):
        pass

    @staticmethod
    @abstractmethod
    def pm_write(address: int, value):
        pass

    def __init__(
        self,
        address: Address | int,
        frozen=None,
    ):
        GameObject.updated_objects.append(self)

        self.address = make_address(address)
        self.frozen = frozen

        dpg_tag = f"{GameObject.DPG_TAG_PREFIX}{uuid4()}"
        self.dpg_tag_frozen = f"{dpg_tag}{GameObject.DPG_TAG_POSTFIX_IS_FROZEN}"
        self.dpg_tag_getter = f"{dpg_tag}{GameObject.DPG_TAG_POSTFIX_GETTER}"
        self.dpg_tag_setter = f"{dpg_tag}{GameObject.DPG_TAG_POSTFIX_SETTER}"

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" at {hex(self.address.resolve())}:"
            f" value={self.value},"
            f" frozen={self.frozen},"
            f" dpg_tag_frozen={self.dpg_tag_frozen},"
            f" dpg_tag_getter={self.dpg_tag_getter}"
            f" dpg_tag_setter={self.dpg_tag_setter}"
            ">"
        )

    def after_read(self, value):
        return value

    def before_write(self, value):
        return value

    @property
    def value(self):
        return self.after_read(self.pm_read(self.address.resolve()))

    @value.setter
    def value(self, new_value):
        self.pm_write(self.address.resolve(), self.before_write(new_value))


class GameFloat(GameObject):
    pm_read = pm.read_float
    pm_write = pm.write_float

    def before_write(self, value):
        return float(value)


class GameDouble(GameObject):
    pm_read = pm.read_double
    pm_write = pm.write_double

    def before_write(self, value):
        return float(value)


class GameByte(GameObject):
    pm_read = pm.read_bytes
    pm_write = pm.write_bytes

    def before_write(self, value: int):
        return value.to_bytes(1, "little")

    def after_read(self, value):
        return int.from_bytes(value, "little")

    @property
    def value(self):
        return self.after_read(self.pm_read(self.address.resolve(), 1))

    @value.setter
    def value(self, new_value):
        self.pm_write(self.address.resolve(), self.before_write(new_value), 1)


def create_simple_game_object_class(pm_type_name: str, class_name: str = None) -> GameObject:
    if class_name is None:
        class_name = f"Game{pm_type_name}"

    pm_type_name = pm_type_name.lower()

    try:
        pm_read = getattr(pm, f"read_{pm_type_name}")
        pm_write = getattr(pm, f"write_{pm_type_name}")
    except AttributeError as e:
        raise ValueError(f"Pymem doesn't have reader/writer for type {pm_type_name}") from e

    return type(class_name, (GameObject,), {"pm_read": pm_read, "pm_write": pm_write})


GameInt = create_simple_game_object_class("Int")
GameShort = create_simple_game_object_class("Short")
GameLongLong = create_simple_game_object_class("LongLong")

GameUnsignedInt = create_simple_game_object_class("uint", "GameUnsignedInt")
GameUnsignedShort = create_simple_game_object_class("ushort", "GameUnsignedShort")
GameUnsignedLongLong = create_simple_game_object_class("ulonglong", "GameUnsignedLongLong")

GameBool = create_simple_game_object_class("Bool")
