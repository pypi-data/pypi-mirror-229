# 프로젝트 제목

**간략한 설명**: 
AWS 의 boto3 를 Wrapping 하여 손쉽게 DynamoDB, S3, SecretManager 등의 서비스를 활용할 수 있도록 만든 라이브러리입니다.
추가적으로 DynamoDB의 경우 One-Big-Table 구조를 차용하여, 하나의 테이블에서 여러개의 파티션을 관리할 수 있도록 구현하였습니다.
또한 S3의 경우 파일을 올리면 URL로 자동으로 뽑아주는 등의 유용한 기능들이 포함되어 있습니다.
추가적으로 AWS API Gateway 와 Lambda 의 연결을 원활하게 해주는 핸들러 유틸이 포함되어 있습니다.
## 시작하기

```bash
pip install sawsi
```

## 주의사항
DynamoDB 의 경우 Pure 한 구성이 아닌, ORM 형식으로 데이터 구조를 변형하여 저장하기 때문에, 기존 사용하던 DB에 덮어 사용시 충돌이 생길 수 있으니 새로운 DDB 객체를 생성하여 사용함을 권장드립니다.

## 프로젝트 사용방법

메인 SAWSI API 사용 방법
```python
from awssi.aws.dynamodb.api import DyanmoFDBAPI
db_api = DyanmoFDBAPI('ddb_name')
items = db_api.fdb_generate_items('partition_name')
for item in items:
  print(item)
  
# 위와 같은 방법으로 S3, SMS, CodeCommit, SecretManager API 를 사용하실 수 있습니다.
```

유틸리티성 핸들러, 함수, 해시 등 기능
```python
from sawsi.shared import error_util
from sawsi.shared import handler_util

# 아래 핸들러는 share.error_util.AppError 에러가 발생할시에, 자동으로
# 에러를 response 객체에 담아 코드와 메시지로 구분하여 전송합니다.
@handler_util.aws_handler_wrapper(
    error_receiver=lambda errmsg: print(errmsg),  # 이 Lambda 함수를 슬랙 Webhook 등으로 대체하면 에러 발생시 모니터링이 가능합니다.
    content_type='application/json',  # 기본적으로 JSON 타입을 반환합니다.
    use_traceback=True,  # 에러 발생시 상세 값을 응답에 전달할지 유무입니다.
)
def some_api_aws_lambda_handler(event, context):
    """
    AWS LAMBDA에서 API Gateway 를 통해 콜한 경우
    """
    # API Gateway 로부터 Lambda 에 요청이 들어오면 다음과 같이 body 와 headers 를 분리하여 dict 형태로 반환합니다.
    body = handler_util.get_body(event, context)
    headers = handler_util.get_headers(event, context)
    
    # 아래부터는 사용자가 직접 응용하여 핸들러를 구성, 다른 함수들로 라우팅합니다.
    cmd = body['cmd']
    if cmd == 'member.request_login':
        import member
        return member.request_login(
            mid=body['mid'],
            mpw=body['pwd'],
        )
    
    # 핸들러 CMD 에 해당하는 CMD 값이 없을 경우 에러 발생
    raise error_util.SYSTEM_NO_SUCH_CMD
```

배포 자동화 기능 사용
AWS CodeCommit 및 CodeBuild, CodePipeline 를 세팅했다는 가정 하에,
build_spec.yml 파일을 다음과 같이 작성하여 AWS CodeCommit 에 커밋시 
자동으로 원하는 Lambda 에 배포가 되도록 만들 수 있습니다.
> build_spec.yml 파일 구성 (AWS CodeBuild 설정에서 파일명 지정 가능)
```yaml
version: 0.2
# AWS Codebuild 환경 > 이미지 구성 > amazon/aws-lambda-python:3.7
# https://hub.docker.com/r/amazon/aws-lambda-python/tags 참고해서 정할 것

env:
  variables:
    ARN_BASE: "arn:aws:lambda:ap-northeast-2:<YOUR_IAM_ID>"
    # 아래에 배포할 Lambda 속성들을 리스트업합니다.
    LAMBDAS: |
      [
        {"name": "function_name", "handler": "main.handler"},
        {"name": "function_name_schduler", "handler": "scheduler.handler"}
      ]

    # 필요하면 추가..
    RUNTIME: "python3.7"
    MEM_SIZE: "2048"

phases:
  install:
    commands:
      - echo Installing required tools...
      - yum install unzip -y
      - yum install -y zip
      - yum install -y jq
      # x86_64 혹은 arm 중에 선택합니다.
      - curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#      - curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
      - mkdir awscliv2
      - unzip awscliv2.zip -d awscliv2
      - ./awscliv2/aws/install
      - aws --version
      - rm -rf awscliv2
      - rm -rf awscliv2.zip

  build:
    commands:
      - echo Build started on `date`
      - echo Zipping the project...
      - zip -r function.zip .
      - cp function.zip ../function.zip
      - rm -rf python
      - mkdir python
      - echo `date` > python/version.txt
      - pip install -r requirements.txt -t python
      - zip -r python.zip python
      - cp python.zip ../python.zip
  post_build:
     commands:
       - |
          for row in $(echo "${LAMBDAS}" | jq -r '.[] | @base64'); do
            _jq() {
              echo ${row} | base64 --decode | jq -r ${1}
            }
    
            LAMBDA_FUNCTION_NAME=$(_jq '.name')
            HANDLER=$(_jq '.handler')
            LAMBDA_LAYER_NAME=${LAMBDA_FUNCTION_NAME}_layer
    
            LAYER_VERSION=$(aws lambda publish-layer-version --layer-name $LAMBDA_LAYER_NAME --zip-file fileb://python.zip --query Version --output text)
            
            # 기존 레이어 가져오기
            EXISTING_LAYERS=$(aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --query 'Layers[*].Arn' --output text)
            
            # 기존 레이어와 새 레이어 합치기
            ALL_LAYERS="$EXISTING_LAYERS $ARN_BASE:layer:$LAMBDA_LAYER_NAME:$LAYER_VERSION"
            
            sleep 1
            aws lambda update-function-configuration --function-name $LAMBDA_FUNCTION_NAME --layers $ALL_LAYERS --runtime $RUNTIME --handler $HANDLER --memory-size $MEM_SIZE
            sleep 1
            aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://function.zip
            sleep 1
            aws lambda publish-version --function-name $LAMBDA_FUNCTION_NAME
          done

artifacts:
  files:
    - function.zip
  discard-paths: yes
```