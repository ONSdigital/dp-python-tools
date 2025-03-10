# Creating secrets locally

Secrets can be created locally for testing using [Localstack](https://docs.localstack.cloud) and AWS CLI

Follow Localstack's [installation documentation](https://docs.localstack.cloud/getting-started/installation/) then use the AWS CLI like you would normally:

```bash
aws secretsmanager create-secret --name "<SECRET NAME>" --secret-string '<SECRET VALUE>' --profile localstack
```

E.g.

```bash
aws secretsmanager create-secret --name "this_would_be_a_string" --secret-string "a string value" --profile localstack
aws secretsmanager create-secret --name "this_would_also_be_a_string" --secret-string '{"this_would_also_be_a_string": "actual parsed value"}' --profile localstack
```

