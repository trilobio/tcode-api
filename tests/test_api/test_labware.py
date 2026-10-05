"""Unittests for labware description/descriptor schemas."""

import unittest

import tcode_api.api as tc
from tcode_api.schemas.registry import schema_registry
from tcode_api.utilities import create_transform, mm

from .test_base import BaseTestCases


def _full_module_fields() -> dict:
    """Every field a ModuleDescription requires, including the labware base's."""
    return {
        "x_length": mm(127.76),
        "y_length": mm(85.48),
        "z_length": mm(20.0),
        "pinchable": False,
        "holder_transform": create_transform(z=mm(12.5)),
        "supports_liftable_labware": True,
    }


class TestModuleDescription(BaseTestCases.TestBaseSchemaVersionedModel):
    """Unittests for ModuleDescription."""

    model = tc.ModuleDescription

    def _create_valid_model_instance(self) -> tc.ModuleDescription:
        return tc.ModuleDescription(**_full_module_fields())

    def test_supports_liftable_labware_is_required(self) -> None:
        """Whether a module permits LIFT must be stated, never assumed.

        Guessing `True` would let the gripper drive its paddles into a module body that
        blocks them; guessing `False` would silently forbid a valid grasp. Both are worse
        than refusing to validate, so this mirrors `pinchable` on the labware base.
        """
        fields = _full_module_fields()
        del fields["supports_liftable_labware"]
        with self.assertRaises(ValueError):
            tc.ModuleDescription(**fields)

    def test_holder_transform_round_trips(self) -> None:
        """The holder transform survives serialize -> deserialize."""
        module = tc.ModuleDescription(**_full_module_fields())
        reloaded = tc.ModuleDescription.model_validate(module.model_dump())
        self.assertEqual(reloaded.holder_transform, create_transform(z=mm(12.5)))

    def test_missing_holder_transform_is_rejected(self) -> None:
        """A Description requires the holder transform; partial data is a Descriptor."""
        fields = _full_module_fields()
        del fields["holder_transform"]
        with self.assertRaises(ValueError):
            tc.ModuleDescription(**fields)


class TestModuleDescriptor(unittest.TestCase):
    """Unittests for ModuleDescriptor, the all-optional counterpart."""

    def test_empty_descriptor_is_valid(self) -> None:
        """A Descriptor may specify nothing at all."""
        descriptor = tc.ModuleDescriptor()
        self.assertIsNone(descriptor.holder_transform)
        self.assertIsNone(descriptor.supports_liftable_labware)

    def test_partial_descriptor_keeps_specified_fields(self) -> None:
        """Fields that are supplied survive a round trip."""
        descriptor = tc.ModuleDescriptor(
            holder_transform=create_transform(z=mm(12.5)), supports_liftable_labware=False
        )
        reloaded = tc.ModuleDescriptor.model_validate(descriptor.model_dump())
        self.assertEqual(reloaded.holder_transform, create_transform(z=mm(12.5)))
        self.assertFalse(reloaded.supports_liftable_labware)


class TestModuleRegistration(unittest.TestCase):
    """The registry builds the Description when complete, the Descriptor otherwise."""

    def test_complete_data_builds_description(self) -> None:
        data = tc.ModuleDescription(**_full_module_fields()).model_dump()
        built = schema_registry.build_instance(data)
        self.assertIsInstance(built, tc.ModuleDescription)

    def test_partial_data_builds_descriptor(self) -> None:
        """Wire data that omits required fields builds the Descriptor.

        Note the fields must be *absent*, not present-and-None: the fallback in
        ``build_description_or_descriptor`` only triggers when every validation error is
        ``missing``. A ``model_dump()`` of a Descriptor emits explicit ``None``s and so does
        not round-trip through the registry -- true of every Description/Descriptor pair,
        not just Module.
        """
        data = {
            "type": "Module",
            "schema_version": 1,
            "holder_transform": create_transform(z=mm(12.5)),
        }
        built = schema_registry.build_instance(data)
        self.assertIsInstance(built, tc.ModuleDescriptor)
