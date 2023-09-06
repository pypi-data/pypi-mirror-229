import base64
import json
from typing import Dict

import pulumi
import pulumi_aws as aws
from pulumi_docker import RegistryArgs, DockerBuildArgs, Image


class AWSWorkflow:
    """
    The Workflow class is used to deploy an image to Amazon Elastic Container Registry (ECR)
    and an AWS Lambda function to an AWS CloudFormation stack.

    Attributes:
        project_path (str): The path to the project directory which will be the context for Docker image.
        docker_file_path (str): The path to the Dockerfile which will be used to build the project.
        ecr_repository_name (str): The name of the ECR repository to deploy the image to.
        s3_bucket_name (str): The name of the S3 bucket to use.
        stack_name (str): The name of the CloudFormation stack to deploy the Lambda function to.
        loki_user (str): Loki User name
        loki_host (str): Loki host address name
        loki_api_key (str): Loki API Key
        tags (str): Tags to pass to the lambda

    Properties:
        ecr_repository (aws.ecr.Repository): The ECR repository object.
        lambda_function (aws.lambda_.Function): The Lambda function object.
        image (Image): The image object.
        s3_bucket (aws.s3.Bucket): The S3 bucket object.
        env_vars (Dict): A dictionary of environment variables to set for the Lambda function.

    Methods:
        deploy(): Initializes the ECR repository, S3 bucket, image, and Lambda function, and deploys them.

        create_s3_bucket(): Creates the S3 bucket.
        create_ecr_repository(): Creates the ECR repository.
        create_ecr_repository_image(): Creates the image and builds it using Docker.
        create_lambda_function(): Creates the Lambda function.

        get_lambda_iam_policy(): Retrieves IAM Policy for attaching to IAM Role
        get_lambda_iam_role(): Retrieves IAM Role for attaching to Lambda
        get_policy_attachment(): Attaches IAM Policy to IAM Role
    """

    ecr_repository: aws.ecr.Repository
    lambda_function: aws.lambda_.Function
    image: Image
    s3_bucket: aws.s3.Bucket

    LAMBDA_FUNCTION_MEMORY_SIZE = 4096
    LAMBDA_FUNCTION_TIMEOUT = 300

    def __init__(
        self,
        project_path: str,
        docker_file_path: str,
        stack_name: str,
        s3_bucket_name: str,
        ecr_repository_name: str,
        loki_user: str,
        loki_host: str,
        loki_api_key: str,
        tags: str,
        env_vars: Dict[str, str],
    ):
        self.project_path = project_path
        self.docker_file_path = docker_file_path
        self.ecr_repository_name = ecr_repository_name
        self.s3_bucket_name = s3_bucket_name
        self.stack_name = stack_name
        self.loki_user = loki_user
        self.loki_host = loki_host
        self.loki_api_key = loki_api_key
        self.tags = tags
        self.env_vars = env_vars

    def deploy(self):
        self.create_s3_bucket()
        self.create_ecr_repository()
        self.create_ecr_repository_image()
        self.create_lambda_function()

    def create_ecr_repository(self):
        self.ecr_repository = aws.ecr.Repository(
            self.ecr_repository_name,
            tags={"Name": self.ecr_repository_name},
        )

    def create_s3_bucket(self):
        self.s3_bucket = self.get_s3_bucket(bucket_name=self.s3_bucket_name)

    def create_ecr_repository_image(self):
        image_name = self.ecr_repository.repository_url
        registry_info = self.ecr_repository.registry_id.apply(self.__get_registry_info)

        self.image = Image(
            f"{self.stack_name}-image",
            build=DockerBuildArgs(
                context=self.project_path,
                dockerfile=self.docker_file_path,
                platform="linux/amd64",
            ),
            image_name=image_name.apply(lambda x: f"{x}:{self.stack_name}"),
            registry=registry_info,
        )

    def create_lambda_function(self):
        iam_role = self.get_lambda_iam_role()
        iam_policy = self.get_lambda_iam_policy()

        role_policy_attachment = aws.iam.RolePolicyAttachment(
            f"{self.stack_name[:15]}-policy-attachment",
            role=iam_role.name,
            policy_arn=iam_policy.arn,
        )

        # TODO: use lambda extension or other way to paste the environment variables into AWS Lambda
        self.lambda_function = aws.lambda_.Function(
            self.stack_name,
            description="Lambda function for execution of PyTest tests in parallel",
            package_type="Image",
            image_uri=self.image.image_name,
            role=iam_role.arn,
            memory_size=self.LAMBDA_FUNCTION_MEMORY_SIZE,
            timeout=self.LAMBDA_FUNCTION_TIMEOUT,
            environment=aws.lambda_.FunctionEnvironmentArgs(
                variables={
                    "S3_BUCKET": self.s3_bucket.id,
                    "LOKI_USER": self.loki_user,
                    "LOKI_HOST": self.loki_host,
                    "LOKI_API_KEY": self.loki_api_key,
                    **self.env_vars,
                },
            ),
            tags=self.get_lambda_tags(self.tags),
            opts=pulumi.ResourceOptions(
                depends_on=[
                    self.ecr_repository,
                    self.image,
                    self.s3_bucket,
                    role_policy_attachment,
                ],
            ),
        )

    def get_lambda_iam_policy(self) -> aws.iam.Policy:
        policy = self.s3_bucket.arn.apply(
            lambda arn: {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:PutObject",
                        ],
                        "Resource": f"{arn}/*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:PutRetentionPolicy",
                            "logs:DescribeLogStreams",
                        ],
                        "Resource": [
                            "arn:aws:logs:*:*:*",
                        ],
                    },
                ],
            }
        )
        return aws.iam.Policy(
            resource_name=f"{self.stack_name[:15]}-policy",
            policy=policy,
        )

    def get_lambda_iam_role(self) -> aws.iam.Role:
        return aws.iam.Role(
            resource_name=f"{self.stack_name[:15]}-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

    @staticmethod
    def __get_registry_info(registry_id) -> RegistryArgs:
        """
        Generates authentication information to access the repository to build and publish the image.
        :param registry_id: Registry ID
        :return: pulumi_docker.ImageRegistry
        """
        credentials = aws.ecr.get_credentials(registry_id=registry_id)
        decoded = base64.b64decode(credentials.authorization_token).decode()

        parts = decoded.split(":")
        if len(parts) != 2:
            raise Exception("Invalid credentials")

        return RegistryArgs(
            server=credentials.proxy_endpoint, username=parts[0], password=parts[1]
        )

    @staticmethod
    def get_s3_bucket(bucket_name: str) -> aws.s3.Bucket:
        return aws.s3.Bucket(bucket_name)

    @staticmethod
    def get_lambda_tags(lambda_tags: str) -> Dict:
        tags = {}
        if lambda_tags:
            tag_values = lambda_tags.split(",")
            for tag_value in tag_values:
                tag = tag_value.split("=")
                tags[tag[0]] = tag[1]
        return tags
