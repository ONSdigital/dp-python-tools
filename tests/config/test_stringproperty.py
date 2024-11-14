import pytest

from dpytools.config.properties.string import StringProperty


def test_string_property():
    """
    Tests if a string property instance can be created
    and validated with no errors.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="Test",
        min_len=1,
        max_len=40,
    )

    test_property.secondary_validation()

    assert test_property.name == "Test String Property"
    assert test_property.value == "Test string value"
    assert test_property.regex == "Test"
    assert test_property.min_len == 1
    assert test_property.max_len == 40


def test_string_property_empty_val():
    """
    Tests if a string property with an empty string as the value
    raises the expected exception from the secondary validation.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="",
        regex="Test regex",
        min_len=1,
        max_len=40,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert "Str value for Test String Property is an empty string" in str(e.value)


def test_string_property_min_len():
    """
    Tests if a string property instance with a non-matching minimum
    length string raises the expected error from secondary validation.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="string",
        min_len=50,
        max_len=51,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert (
        "Str value for Test String Property is shorter than minimum length 50"
        in str(e.value)
    )


def test_string_property_max_len():
    """
    Tests if a string property instance with a non-matching maximum
    length string raises the expected error from secondary validation.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="string",
        min_len=1,
        max_len=2,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert (
        "Str value for Test String Property is longer than maximum length 2"
    ) in str(e.value)


def test_string_property_regex_no_match():
    """
    Tests if a string property instance with a non-matching regex/value
    raises the expected error from secondary validation.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="Test regex",
        min_len=1,
        max_len=50,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert (
        "Str value for Test String Property does not match the given regex."
    ) in str(e.value)


def test_string_property_regex_no_match():
    """
    Tests if a string property instance with a non-matching regex/value
    raises the expected error from secondary validation.
    """

    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="Non-matching regex",
        min_len=1,
        max_len=50,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert (
        "Str value for Test String Property does not match the given regex."
    ) in str(e.value)


def test_string_property_secondary_validation():
    """
    Tests that a ValueError is raised when the string value
    does not match the provided regex pattern.
    """
    test_property = StringProperty(
        _name="Test String Property",
        _value="Test string value",
        regex="Non-matching regex",
        min_len=1,
        max_len=50,
    )

    with pytest.raises(ValueError) as e:
        test_property.secondary_validation()

    assert (
        "Str value for Test String Property does not match the given regex."
    ) in str(e.value)


def test_string_property_type_invalid():
    """
    Test that a ValueError is raised when the value cannot be cast to a string.
    """

    class NonStringableObject:
        def __str__(self):
            raise Exception("Cannot convert to string")

    invalid_value = NonStringableObject()

    property_instance = StringProperty(
        _name="Test String Property",
        _value=invalid_value,
        regex=None,
        min_len=None,
        max_len=None,
    )

    with pytest.raises(ValueError) as exc_info:
        property_instance.type_is_valid()

    expected_message = f"Cannot cast {property_instance.name} value to string."
    assert expected_message in str(exc_info.value)
