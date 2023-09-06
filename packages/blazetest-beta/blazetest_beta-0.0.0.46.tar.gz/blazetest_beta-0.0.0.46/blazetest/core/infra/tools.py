from abc import ABC, abstractmethod
import logging
from pulumi import automation as auto
from pulumi.automation import LocalWorkspaceOptions, ProjectBackend, ProjectSettings

from blazetest.core.config import CWD, LOKI_HOST, LOKI_USER, DOCKER_FILE_PATH
from blazetest.core.deployment.aws import AWSWorkflow

logger = logging.getLogger(__name__)


class InfraSetupTool(ABC):
    def __init__(
        self,
        aws_region: str,
        stack_name: str,
        s3_bucket_name: str,
        ecr_repository_name: str,
        loki_api_key: str,
        tags: str,
        debug: bool,
    ):
        self.aws_region = aws_region
        self.stack_name = stack_name
        self.s3_bucket_name = s3_bucket_name
        self.ecr_repository_name = ecr_repository_name
        self.loki_api_key = loki_api_key
        self.tags = tags
        self.debug = debug

    @abstractmethod
    def deploy(self) -> None:
        pass


class PulumiInfraSetup(InfraSetupTool):
    """
    Uses Pulumi (https://www.pulumi.com/docs/) Automation API to build and deploy artifacts to the cloud.
    """

    def __init__(
        self,
        aws_region: str,
        stack_name: str,
        s3_bucket_name: str,
        ecr_repository_name: str,
        loki_api_key: str,
        tags: str,
        debug: bool,
    ):
        super().__init__(
            aws_region=aws_region,
            stack_name=stack_name,
            s3_bucket_name=s3_bucket_name,
            ecr_repository_name=ecr_repository_name,
            loki_api_key=loki_api_key,
            tags=tags,
            debug=debug,
        )

    def deploy(self) -> None:
        # TODO: User should pass env variable himself
        env_vars = {}

        workflow = AWSWorkflow(
            project_path=CWD,
            docker_file_path=DOCKER_FILE_PATH,
            stack_name=self.stack_name,
            s3_bucket_name=self.s3_bucket_name,
            ecr_repository_name=self.ecr_repository_name,
            loki_host=LOKI_HOST,
            loki_user=LOKI_USER,
            loki_api_key=self.loki_api_key,
            env_vars=env_vars,
            tags=self.tags,
        )

        stack = auto.create_stack(
            stack_name=self.stack_name,
            project_name="blazetest",
            program=workflow.deploy,
            opts=LocalWorkspaceOptions(
                project_settings=ProjectSettings(
                    name="blazetest",
                    backend=ProjectBackend(url="file:\\/\\/~"),
                    runtime="python",
                ),
            ),
        )

        logger.info("Installing plugins")

        # TODO: updated automatically to the stable version
        stack.workspace.install_plugin("aws", "v5.42.0")
        stack.workspace.install_plugin("docker", "v4.3.1")

        stack.set_config("aws:region", auto.ConfigValue(value=self.aws_region))
        stack.refresh(on_output=self.log_pulumi_event, show_secrets=False)

        logger.info("Deploying..")
        workflow_result = stack.up(  # noqa
            show_secrets=False, on_output=self.log_pulumi_event, debug=self.debug
        )

        logger.info(
            "Deploying has finished.",
        )

    EVENTS_TO_SUPRESS_OUTPUT = [
        "Pushing",
        "Waiting",
        "Preparing",
        "Pushed",
        "updating...",
        "digest",
        "writing image",
    ]

    def log_pulumi_event(self, event: str):
        if (
            any([message in event for message in self.EVENTS_TO_SUPRESS_OUTPUT])
            or event.strip == ""
        ):
            return
        logger.info(event)
