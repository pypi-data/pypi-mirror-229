
class SecretManager:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('secretsmanager')
        self.region = boto3_session.region_name

    def get_secret_value_response(self, secret_name):
        response = self.client.get_secret_value(
            SecretId=secret_name
        )
        # Decrypts secret using the associated KMS key.
        secret = response['SecretString']
        return secret
