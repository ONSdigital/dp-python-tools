# Secrets

## Overview

A wrapper class around [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)'s Secrets Manager client.

Encapsulates:
- Creation of the client (and storing it as a variable for re-use)
- Retrieving a secret from the client
- Retrieving the value of the secret from the response
- Parsing any exceptions/errors thrown during the above process and formatting the output neater

## Usage

After instantiating an instance of the [SecretsClient](./secrets_client.py), a boto3 Secrets Manager client will automatically be instantiated by the class.

After that, `SecretsClient` class has one public method `get_secret`.

### get_secret

This retrieves a secret and parses the response from AWS.

It returns an instance of [Secret](./secret.py), which contains:
- A boolean indicating success
- A value object (the value of the secret from AWS, if any)
- An error message (if any)

#### Value parsing

- If a secret is a a _binary_ value, the result will be base64 encoded

- If the secret is a _string value_ and is _not a JSON string_:
  - Then the value is set to this simple string value

- If the secret _is a JSON_:
  - The value is converted to a dictionary. Then:
    - If the dictionary has a key that matches the ID of the secret:
      - The value for that key is set to the value of the `Secret` object
      - Otherwise the value for the secret is set to the dictionary object

Examples:
1. AWS Secret response has `SecretBinary` set

```python
secret_value_encoded = base64.b64encode(b"example value")
secret = {
    "Name": "binary_secret"
    "SecretBinary": <BYTES>
}

client = SecretsClient()
response = client.get_secret("binary_secret")

assert response.value == secret_value_encoded
```

2. AWS Secret response is a simple string value
```python
secret_value = "Simple stirng value"
secret = {
    "Name": "string_secret_id"
    "SecretString": secret_value
}

client = SecretsClient()
response = client.get_secret("string_secret_id")

assert response.value == secret_value
```

3. AWS Secret response is a JSON string, without a key that matches the secret ID
```python
secret_value = '{"key_name": "value here"}'
secret = {
    "Name": "json_secret_id"
    "SecretString": secret_value
}

client = SecretsClient()
response = client.get_secret("json_secret_id")

expected_dict = json.loads(secret_value)
assert response.value == expected_dict
assert response.value["key_name"] == expected_dict["key_name"]
```


4. AWS Secret response is a JSON string, **with** a key that matches the secret ID
```python
secret_value = '{"matching_json_key_secret_id": "value here"}'
secret = {
    "Name": "matching_json_key_secret_id"
    "SecretString": secret_value
}

client = SecretsClient()
response = client.get_secret("matching_json_key_secret_id")

assert response.value == "value here"
```

### batch_get_secrets

Retrieves _multiple_ secrets IDs in a batch, and then parses each one as per [get-secret](#get_secret)

