import builtins
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Type, TypeVar, Union, get_args, get_origin

import yaml

from .field import HydraletteField, fields

T = TypeVar("T")


@dataclass
class ConfigBase:
    @classmethod
    def create(cls: Type[T], overrides=sys.argv[1:]) -> T:
        if not issubclass(cls, ConfigBase):
            raise ValueError(f"Type '{cls}' is not a subclass of ConfigBase")

        for help_flag in ("--help", "-h"):
            if help_flag in overrides:
                cls.print_help_page()
                raise SystemExit(0)

        cls.convert_fields_to_hydralette()
        config = cls.parse_and_instantiate(overrides)
        config.resolve_references()
        return config

    @classmethod
    def convert_fields_to_hydralette(cls):
        if hasattr(cls, "__dataclass_fields__"):
            for key, field in cls.__dataclass_fields__.items():
                hydralette_field = HydraletteField.from_dc_field(field)
                cls.__dataclass_fields__[key] = hydralette_field

    @classmethod
    def parse_and_instantiate(cls: Type[T], overrides: List[str] = sys.argv[1:]) -> T:
        kwargs = {}
        sub_config_overrides = defaultdict(list)
        sub_config_types = defaultdict()

        # parse overrides
        for override in overrides:
            eq_index = override.index("=")
            key = override[:eq_index]
            subkeys = key.split(".")
            value = override[eq_index + 1 :]

            # Match key to the corresponding field
            matched_field = None
            matched_fields = [field for field in fields(cls) if field.name == key]
            matched_sub_fields = [field for field in fields(cls) if field.name == subkeys[0]]
            if matched_fields:
                matched_field = matched_fields[0]
                top_level = True
            elif matched_sub_fields:
                matched_field = matched_sub_fields[0]
                top_level = False
            else:
                raise ValueError(f"Key '{key}' could not be found in {cls}")

            # top level primitive assignments: key=val
            if top_level and not is_hydralette_config(matched_field.type):
                kwargs[key] = convert_type(matched_field, value)

            # config groups: key=group_name
            elif top_level and is_hydralette_config(matched_field.type):
                sub_config_types[key] = matched_field.groups[value]

            # sub level assignments: subkey[0].subkey[1]=val
            else:
                if subkeys[0] not in sub_config_types:
                    sub_config_types[subkeys[0]] = matched_field.type
                sub_config_overrides[subkeys[0]].append(f"{'.'.join(subkeys[1:])}={value}")

        # create sub configs
        for key, sub_cls in sub_config_types.items():
            kwargs[key] = cls.parse_and_instantiate(sub_cls, sub_config_overrides[key])  # type: ignore

        config = cls(**kwargs)
        return config

    @staticmethod
    def _get_attr(obj, name, only_repr=False):
        value = getattr(obj, name)
        if isinstance(value, ConfigBase):
            return value.to_dict()
        elif only_repr and not type(value).__name__ in dir(builtins):
            return repr(value)
        else:
            return value

    def to_dict(self, only_repr=False) -> Dict[str, Any]:
        return {field.name: self._get_attr(self, field.name, only_repr=only_repr) for field in fields(self)}  # type: ignore

    def to_yaml(self, only_repr=False) -> str:
        d = self.to_dict(only_repr=only_repr)
        return yaml.dump(d)

    def print_yaml(self):
        print(self.to_yaml(only_repr=True))

    @classmethod
    def print_help_page(cls) -> None:
        printed = []

        def format_type_info(t) -> str:
            if get_origin(t) is Union:
                return f"Union[{', '.join(st.__name__ for st in get_args(t))}]"
            else:
                return t.__name__

        def print_options_for_class(cls, trace, group_info="", super_class=None):
            if cls in printed:
                return

            if group_info:
                group_info = f" ({group_info})"
            name = cls.__module__ + "." + cls.__name__
            print(f"Options from '{name}'{group_info}:")

            for field in fields(cls):
                if super_class is not None and field.name in [f.name for f in fields(super_class)]:
                    continue
                arg_descr = field.metadata.get("help", "") if not is_hydralette_config(field.type) else "Options see below"
                _trace = trace + "." if trace else ""
                type_fmt = format_type_info(field.type)
                arg_name = f"{_trace}{field.name}: {type_fmt}"
                print(f"\t{arg_name:55s}{arg_descr}")

            printed.append(cls)
            print()
            sub_config_fields = [field for field in fields(cls) if is_hydralette_config(field.type)]
            for field in sub_config_fields:
                _trace = trace + "." if trace else ""
                if field.groups:
                    for key, typ in field.groups.items():
                        print_options_for_class(typ, f"{_trace}{field.name}", f"active if '{field.name}={key}'")
                else:
                    print_options_for_class(field.type, f"{_trace}{field.name}")

        print(f"Usage: python {sys.argv[0]} [option=value]\n")
        print_options_for_class(cls, "")

    def resolve_references(self, root_config=None):
        for field in fields(self):  # type: ignore
            value = getattr(self, field.name)
            if field.reference is not None:
                setattr(self, field.name, field.reference(root_config))
            elif is_hydralette_config(value):
                value.resolve_references(root_config=root_config)


def is_hydralette_config(obj: Any) -> bool:
    return (
        isinstance(obj, ConfigBase)
        or (isinstance(obj, type) and issubclass(obj, ConfigBase))
        or (get_origin(obj) is Union and all(issubclass(t, ConfigBase) for t in get_args(obj)))
    )


def convert_type(field: HydraletteField, value: str) -> Any:
    if field.convert is not None:
        return field.convert(value)
    else:
        try:
            return field.type(value)
        except:  # noqa
            return value
