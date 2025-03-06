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