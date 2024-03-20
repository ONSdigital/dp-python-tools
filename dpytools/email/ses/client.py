import re
import boto3
from botocore.exceptions import BotoCoreError, ClientError

class SesClient:
    """
    A client for sending emails using AWS SES and the boto3 client.

    Attributes:
        client: The boto3 SES client.
        sender: The sender's email address.
    """

    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    def __init__(self, sender: str, aws_region: str):
        """
        Initialise the SesClient with the sender's email and AWS region.

        Args:
            sender (str): The sender's email address.
            aws_region (str): The AWS region.

        Raises:
            ValueError: If the sender's email or AWS region is invalid.
        """
        # check sender is actually a valid email (as in the format)
        if not re.match(self.EMAIL_REGEX, sender):
            raise ValueError("Invalid sender email format")
        
        # check the aws region looks valid
        if aws_region not in boto3.session.Session().get_available_regions('ses'):
            raise ValueError("Invalid AWS region")
        
        # create the boto3 client
        try:
            self.client = boto3.client('ses', region_name=aws_region)
            self.sender = sender
        except (BotoCoreError, ClientError) as err:
            print(f"Error creating SES client: {err}")
            raise err

    def send(self, recipient: str, subject: str, body: str):
        """
        Send an email to the recipient.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body of the email.

        Raises:
            ValueError: If the recipient's email is invalid.

        Returns:
            dict: The response from the send_email method of the SES client.
        """
        # check recipient is actually a valid email (as in the format)
        if not re.match(self.EMAIL_REGEX, recipient):
            raise ValueError("Invalid recipient email format")

        # send the email to the recipient using the client from init
        try:
            response = self.client.send_email(
                Source=self.sender,
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                        },
                    },
                }
            )
        except (BotoCoreError, ClientError) as error:
            print(f"Error sending email: {error}")
            raise

        return response