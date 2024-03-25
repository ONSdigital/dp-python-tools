# SesClient

The `SesClient` is a Python helper class that simplifies sending emails using AWS Simple Email Service (SES) and the `boto3` client.

## Permissions

The `SesClient` class uses the currently active AWS permissions of the machine where it's running. 

If you need to specify a profile (such as when developing), you can pass in a specific profile via the `profile_name` argument when creating an instance of the `SesClient` class.


## Features

- Validates sender and recipient email addresses using the `email_validator` library.
- Validates the AWS region.
- Sends emails with a subject and body to a recipient.

## Usage


### Importing the `SesClient` class

```python
from ses_client import SesClient
```

### Creating an instance of the SesClient class
```python
ses_client = SesClient('sender@example.com', 'us-west-2', profile_name='my-profile')
```

### Sending an email
```python
ses_client.send('recipient@example.com', 'subject', 'body')
```

## Error Handling

The SesClient class raises a ValueError if the sender or recipient email address is invalid, or if the AWS region is invalid. 

It also raises a botocore.exceptions.BotoCoreError or botocore.exceptions.ClientError if there is an error creating the boto3 client or sending the email.
