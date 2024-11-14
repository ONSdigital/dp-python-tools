import pytest
from dpytools.config.properties.base import BaseProperty

class SampleProperty(BaseProperty):
    def type_is_valid(self):
        # Implementation for testing purposes
        pass

def test_name_setter_raises_error():
    """
    Test that setting a new name after instantiation raises a ValueError.
    """
    property_instance = SampleProperty(_name="Initial Name", _value="Some Value")
    with pytest.raises(ValueError) as exc_info:
        property_instance.name = "New Name"
    assert "Trying to change name property to value New Name but you cannot change a property name after instantiation." in str(exc_info.value)

def test_value_setter_raises_error():
    """
    Test that setting a new value after instantiation raises a ValueError.
    """
    property_instance = SampleProperty(_name="Property Name", _value="Initial Value")
    with pytest.raises(ValueError) as exc_info:
        property_instance.value = "New Value"
    assert "Trying to change value to New Value but you cannot change a property value after instantiation." in str(exc_info.value)

def test_type_is_valid_not_implemented():
    """
    Test that calling super().type_is_valid raises NotImplementedError.
    """
    class IncompleteProperty(BaseProperty):
        def type_is_valid(self):
            return super().type_is_valid()

    property_instance = IncompleteProperty(_name="Property Name", _value="Property Value")

    with pytest.raises(NotImplementedError) as exc_info:
        property_instance.type_is_valid()

    assert "Subclasses must implement type_is_valid method." in str(exc_info.value)

def test_secondary_validation_no_error():
    """
    Test that secondary_validation does not raise an error by default.
    """
    property_instance = SampleProperty(_name="Property Name", _value="Property Value")
    property_instance.secondary_validation()