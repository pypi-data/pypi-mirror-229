import dataclasses
import re
from typing import Dict

from blazetest.core.utils.exceptions import ConfigurationValidationException


@dataclasses.dataclass
class ValidationBase:
    @staticmethod
    def get_validators() -> Dict:
        return {}

    def __post_init__(self):
        fields = dataclasses.fields(self)
        messages = []
        for field in fields:
            value = getattr(self, field.name)
            validator = self.get_validators().get(field.name)
            if not validator:
                continue

            is_valid, message = validator(value)
            if not is_valid:
                messages.append(message)

        if messages:
            raise ConfigurationValidationException(messages)


def stack_name_is_valid(stack_name):
    if len(stack_name) > 96 or len(stack_name) < 3:
        return (
            False,
            "Stack name should be >=3 and 56 (64 - 8 (Session UUID length)) characters long",
        )

    pattern = r"^[a-zA-Z][a-zA-Z0-9-_]+$"
    if not re.match(pattern, stack_name):
        return (
            False,
            "The stack name does not meet the naming conventions. See "
            "https://docs.aws.amazon.com/AWSCloudFormation/"
            "latest/UserGuide/cfn-using-console-create-stack-parameters.html",
        )

    return True, ""


def ecr_repository_name_is_valid(ecr_repository_name):
    if len(ecr_repository_name) > 224 or len(ecr_repository_name) < 2:
        return (
            False,
            "ECR Repository should be >=2 and <= 248 (256 - 8 (Session UUID length)) characters long",
        )

    pattern = r"^[a-z][a-z0-9-_]+$"
    if not re.match(pattern, ecr_repository_name):
        return (
            False,
            "The ECR repository does not meet the naming conventions. See "
            "https://docs.aws.amazon.com/AmazonECR/latest/userguide/Repositories.html",
        )

    return True, ""


def s3_bucket_name_is_valid(s3_bucket_name):
    pattern = r"^(?!.*(\.\.|-\.|\.-|--|\.\d|-\d|\d-))[a-z0-9.-]{3,63}$"
    if re.match(pattern, s3_bucket_name):
        return True, ""
    else:
        return (
            False,
            "S3 Bucket name does not meet the naming conventions; "
            "See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html",
        )
