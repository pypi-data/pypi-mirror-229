import boto3
from sawsi.aws import shared


class CodeCommitAPI:
    """
    S3 를 활용하는 커스텀 ORM 클래스
    """
    def __init__(self, credentials=None, region=shared.DEFAULT_REGION):
        """
        :param credentials: {
            "aws_access_key_id": "str",
            "aws_secret_access_key": "str",
            "region_name": "str",
            "profile_name": "str",
        }
        """
        self.boto3_session = shared.get_boto_session(credentials)
        self.cache = {}
        self.client = boto3.client('codecommit', region_name=region)

    def get_file(self, repository_name, commit_specifier, file_path):
        # 커밋 기반으로 파일 가쟈오기
        response = self.client.get_file(
            repositoryName=repository_name,
            commitSpecifier=commit_specifier,
            filePath=file_path
        )
        return response


if __name__ == '__main__':
    code_commit = CodeCommitAPI()
    r = code_commit.get_file('product_pipe_serverless', 'cdb53f7e0f357964544a8c274687e31281556ad1', 'aws/shared.py')
    fileContent = r['fileContent']
    print(fileContent.decode())