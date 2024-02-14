import pytest
from dpytools.config.properties import IntegerProperty

def test_int_property():
    """
    Tests if an integer property instance can be created 
    and validated with no errors.
    """

    test_property = IntegerProperty(
        _name = "Test Integer property",
        _value = 24,
        min_val = 0,
        max_val = 101
    )

    test_property.type_is_valid()
    test_property.secondary_validation()
    
    assert test_property.name == "Test Integer property"
    assert test_property.value == 24
    assert test_property.min_val == 0
    assert test_property.max_val == 101


def test_int_property_type_invalid():
    """
    Tests if an integer property with a type of value that 
    cannot be cast to string raises an exception.
    """

    test_property = IntegerProperty(
        _name = "Test Integer Property",
        _value = "Not an integer",
        min_val = 0,
        max_val = 101
    )

    with pytest.raises(Exception) as e:

        test_property.type_is_valid()

    assert "Cannot cast Test Integer Property value Not an integer to integer." in str(e.value)


def test_int_property_empty_val():
    """
    Tests if an integer property with nothing as the value
    raises the expected exception from the secondary validation.
    """

    test_property = IntegerProperty(
        _name = "Test Integer Property",
        _value = None,
        min_val = 0,
        max_val = 101
    )

    with pytest.raises(ValueError) as e:

        test_property.secondary_validation()

    assert "Integer value for Test Integer Property does not exist." in str(e.value)


def test_int_property_min_val():
    """
    Tests if an integer property with a value lower than the allowed minimum
    raises the expected exception from the secondary validation.
    """

    test_property = IntegerProperty(
        _name = "Test Integer Property",
        _value = 9,
        min_val = 10,
        max_val = 101
    )

    with pytest.raises(ValueError) as e:

        test_property.secondary_validation()

    assert "Integer value for Test Integer Property is lower than allowed minimum." in str(e.value)

    

def test_int_property_max_val():
    """
    Tests if an integer property with a value higher than the allowed maximum
    raises the expected exception from the secondary validation.
    """

    test_property = IntegerProperty(
        _name = "Test Integer Property",
        _value = 102,
        min_val = 0,
        max_val = 101
    )

    with pytest.raises(ValueError) as e:

        test_property.secondary_validation()

    assert "Integer value for Test Integer Property is higher than allowed maximum." in str(e.value)