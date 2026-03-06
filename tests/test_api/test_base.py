import tempfile
import unittest

from tcode_api.schemas.base import BaseSchemaVersionedModel


class BaseTestCases:
    """Namespace to prevent unittest discovery of base test case classes."""

    class TestBaseSchemaVersionedModel(unittest.TestCase):
        model: type[BaseSchemaVersionedModel]

        """Unittests for any model that subclasses :class:``BaseSchemaVersionedModel``."""

        def _create_valid_model_instance(self) -> BaseSchemaVersionedModel:
            """Create and return a valid instance of the model under test.

            Subclasses must override this method.
            """
            raise NotImplementedError(
                "Subclasses must implement create_valid_model_instance method."
            )

        def test_file_io(self) -> None:
            """ConfiguredBaseModel subclasses should be able to serialize to and from file-like objects."""
            model = self._create_valid_model_instance()
            with tempfile.TemporaryFile(mode="w+") as text_io:
                model.write(text_io)
                text_io.seek(0)
                model_read = model.read(text_io)

            self.assertEqual(model, model_read)
