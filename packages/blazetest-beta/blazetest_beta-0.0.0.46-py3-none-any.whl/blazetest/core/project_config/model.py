import dataclasses
from typing import List, Dict

from blazetest.core.project_config.validators import (
    ValidationBase,
    ecr_repository_name_is_valid,
    stack_name_is_valid,
    s3_bucket_name_is_valid,
)


@dataclasses.dataclass
class PytestConfig(ValidationBase):
    collection_args: List[str] = dataclasses.field(default_factory=lambda: [])
    execution_args: List[str] = dataclasses.field(default_factory=lambda: [])


@dataclasses.dataclass
class AWSConfig(ValidationBase):
    region: str
    stack_name: str = "blazetest-stack"
    s3_bucket: str = "blazetest-s3"
    ecr_repository_name: str = "blazetest-repo"

    def get_stack_name(self, uuid: str):
        return f"{self.stack_name}-{uuid}"

    def get_s3_bucket_name(self, uuid: str):
        return f"{self.s3_bucket}-{uuid}"

    def get_ecr_repository_name(self, uuid: str):
        return f"{self.ecr_repository_name}-{uuid}"

    def get_validators(self) -> Dict:
        return {
            "ecr_repository_name": ecr_repository_name_is_valid,
            "stack_name": stack_name_is_valid,
            "s3_bucket": s3_bucket_name_is_valid,
        }


@dataclasses.dataclass
class BlazetestConfig(ValidationBase):
    aws: AWSConfig
    pytest: PytestConfig
    license_key: str = None
    license_file: str = None
    failed_test_retry: int = 0
