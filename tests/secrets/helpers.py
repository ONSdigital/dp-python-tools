import random
import string
import uuid
from datetime import datetime, timedelta
from typing import List, Optional


# Lifted from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def create_random_string(
    length: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    choices: Optional[List[str]] = [string.ascii_uppercase, string.digits],
) -> str:
    if length is None:
        if min_length is None and max_length is None:
            raise ValueError("No values were supplied")

        length = random.randint(min_length, max_length)

    return "".join(random.choices("".join(choices), k=length))


# Half lifted from here https://stackoverflow.com/questions/553303/how-to-generate-a-random-date-between-two-other-dates
def create_random_date(
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
):
    if start_date is None and end_date is None:
        end_date = datetime.now()

    if start_date is None and end_date is not None:
        days_ago = random.randint(1, 365)
        start_date = end_date - timedelta(days=days_ago)
    elif start_date is not None and end_date is None:
        end_date = datetime.now()

    if start_date > end_date:
        days_ago = random.randint(1, 365)
        end_date = start_date + timedelta(days=days_ago)

    delta = end_date - start_date
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start_date + timedelta(seconds=random_second)


# Secret response from here https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/get_secret_value.html
def create_secret(
    name: str,
    secret_string: Optional[str] = None,
    secret_bytes: Optional[str] = None,
    version_id: Optional[str] = None,
    created_at: Optional[str] = None,
    arn: Optional[str] = None,
    version_stages: Optional[List[str]] = ["AWSCURRENT"],
) -> dict:
    return {
        "ARN": arn
        if arn is not None
        else f"arn:aws:secretsmanager:eu-west-2:000000000000:secret:{name}-{create_random_string(length=5, choices=[string.ascii_lowercase, string.ascii_uppercase])}",
        "Name": name,
        "VersionId": version_id if version_id is not None else uuid.uuid4(),
        "SecretBinary": secret_bytes,
        "SecretString": secret_string,
        "VersionStages": version_stages,
        "CreatedDate": created_at if created_at is not None else create_random_date(),
    }


# Definition in response lifted from https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/batch_get_secret_value.html
def create_error(secret_id: str, error_code: str, message: str) -> dict:
    return {"SecretId": secret_id, "ErrorCode": error_code, "Message": message}
