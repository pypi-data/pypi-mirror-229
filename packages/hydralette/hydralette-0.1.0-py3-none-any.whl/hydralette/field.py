from dataclasses import MISSING, Field
from dataclasses import fields as dc_fields
from typing import Any, Callable, Dict, Optional, Tuple


def field(
    *,
    reference: Optional[Callable] = None,
    convert: Optional[Callable] = None,
    validate: Optional[Callable] = None,
    groups: Dict[str, type] = {},
    default=MISSING,
    default_factory=MISSING,
    init=True,
    repr=True,
    hash=None,
    compare=True,
    metadata=None,
    kw_only=MISSING
) -> Any:
    return HydraletteField(
        reference=reference,
        convert=convert,
        validate=validate,
        groups=groups,
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
        kw_only=kw_only,
    )


class HydraletteField(Field):
    """Field subclass that adds
    - referencing other values
    - type conversion functions
    - validation functions
    - config group information
    """

    def __init__(
        self,
        *,
        reference: Optional[Callable] = None,
        convert: Optional[Callable] = None,
        validate: Optional[Callable] = None,
        groups: Dict[str, type] = {},
        **kwargs
    ):
        super().__init__(**kwargs)
        self.reference = reference
        self.convert = convert
        self.validate = validate
        self.groups = groups

    @classmethod
    def from_dc_field(cls: type["HydraletteField"], field: Field) -> "HydraletteField":
        hydralette_field = cls(
            default=field.default,
            default_factory=field.default_factory,
            init=field.init,
            repr=field.repr,
            hash=field.hash,
            compare=field.compare,
            metadata=field.metadata,
            kw_only=field.kw_only,
        )
        hydralette_field.name = field.name
        hydralette_field._field_type = field._field_type  # type: ignore

        return hydralette_field


def fields(class_or_instance) -> Tuple[HydraletteField]:
    return dc_fields(class_or_instance)  # type: ignore
