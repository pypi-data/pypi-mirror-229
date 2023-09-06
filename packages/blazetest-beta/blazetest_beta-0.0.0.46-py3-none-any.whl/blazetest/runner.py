import logging
import time
from typing import Optional

import click

from blazetest import __version__
from blazetest.core.infra.infra_setup import InfraSetup
from blazetest.core.license.manager import LicenseManager
from blazetest.core.project_config.project_config import ProjectConfiguration
from blazetest.core.run_test.runner_facade import TestRunner
from blazetest.core.run_test.result_model import TestSessionResult
from blazetest.core.utils.logging_config import setup_logging
from blazetest.core.utils.utils import (
    create_build_folder,
    generate_uuid,
    set_environment_variables,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-config",
    "--config-path",
    help="Configuration path to the TOML file for the CLI. "
    "If not specified -> searches the project's root folder for the file blazetest.toml. "
    "If not found -> raises an error.",
)
@click.option(
    "-ak",
    "--aws-access-key-id",
    help="AWS Access Key ID which is used to deploy artifacts.",
)
@click.option(
    "-as",
    "--aws-secret-access-key",
    help="AWS Secret Access Key which is used to deploy artifacts.",
)
@click.option(
    "-k",
    "--license-key",
    help="License key for Blazetest CLI. Either --license-key or --license-file should be specified."
    "License key has a higher priority if both are specified.",
)
@click.option(
    "-l",
    "--license-file",
    help="License file for Blazetest CLI. Either --license-key or --license-file should be specified."
    "License file has a lower priority if both are specified.",
)
@click.option(
    "-t",
    "--tags",
    help="Tags specified for the AWS Lambda function. The tags will be attached to created Lambda function instance.",
)
@click.option(
    "-lo",
    "--logs",
    default="enabled",
    type=click.Choice(["enabled", "disabled"]),
    help="Default is enabled. When logs are enabled, they are shown in the console stdout. "
    "When they are set to disabled, the logs are not shown during CLI execution, but saved to blazetest.log, "
    "which will be located in the project's root.",
)
@click.option(
    "-lk",
    "--loki",
    help="Loki API Key. If provided, logs are sent to the Loki",
)
@click.option(
    "-io",
    "--invoke-only",
    is_flag=True,
    help="If specified, it searches for the Lambda with the specified stack name and invokes it. "
    "If not found, raises an exception.",
)
@click.option(
    "-d",
    "--diag",
    is_flag=True,
    help="If specified, executes one trial test to make sure everything works. The tests are not collected, "
    "instead dummy test is sent to Lambda.",
)
@click.option("-de", "--debug", is_flag=True, help="Enables debugging output.")
@click.option("-v", "--version", is_flag=True, help="Prints Blazetest CLI version.")
def run_tests(
    config_path: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    license_key: str,
    license_file: str,
    tags: str,
    logs: str,
    loki: str,
    invoke_only: bool,
    diag: bool,  # noqa
    debug: bool,
    version: bool,
):
    """
    Runs tests using the pytest library and parallel Lambda functions.
    It deploys the necessary AWS resources (ECR, Lambda, and S3 bucket) using Pulumi.
    It also accepts any additional arguments passed to the command, which will be passed to pytest as arguments.

    Args:
        config_path (str): Path to the TOML configuration file.
        aws_access_key_id (str): AWS access key id.
        aws_secret_access_key (str): AWS secret access key.
        license_key (str): License key.
        license_file (str): Path to the license file.
        tags (str): Tags in the format key1=value,key2=value. Will be attached to created Lambda function instance.
        logs (str): Defaults to enabled, possible values: enabled, disabled.
        loki (str): Loki API Key. If provided, logs are sent to the Loki
        invoke_only (bool): If true, invokes the function with provided stack name without deploying
        diag (bool): If true, runs only one dummy test without collection. Runs it on Lambda.
        debug (bool): flag that enables debugging output if true
        version (bool): prints Blazetest CLI version
    """
    version_string = f"Blazetest version: {__version__}"

    if version:
        print(version_string)
        return

    session_uuid = generate_uuid()
    setup_logging(
        debug=debug,
        stdout_enabled=logs != "disabled",
        loki_api_key=loki,
        session_uuid=session_uuid,
    )

    logger.info(version_string)
    logger.info(f"Session UUID: {session_uuid}")

    # Get project configuration from Blazetest TOML
    config = ProjectConfiguration.from_toml(config_path)

    # License checking
    licence_manager = LicenseManager(
        license_key=license_key,
        license_file=license_file,
        config_license_key=config.license_key,
        config_license_file=config.license_file,
    )

    expiration_date = licence_manager.check_license()
    logger.info(f"License expiration date: {expiration_date}")
    logger.info(f"Config initialized: {config}")

    # Collecting tests
    test_runner = TestRunner(
        config=config,
        uuid=session_uuid,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    test_node_ids = test_runner.get_collected_tests()
    if len(test_node_ids) == 0:
        logger.error("Ending session as there are no tests to run")
        return
    logger.info(f"Found {len(test_node_ids)} tests to run")

    flaky_enabled = False
    if licence_manager.flaky_test_retry_enabled():
        logger.info("Flaky test retry feature is on")
        if config.failed_test_retry > 0:
            flaky_enabled = True
    else:
        if config.failed_test_retry > 0:
            logger.warning(
                "Flaky test retry feature is not available within this license"
            )

    set_environment_variables(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # TODO: save previous session uuids and stack names to invoke the latest session : needed?
    if not invoke_only:
        # Creating build folder for blazetest files
        create_build_folder()

        # Using Pulumi to do the deployment, create ECR, Lambda and S3 bucket
        infra_setup = InfraSetup(
            aws_region=config.aws.region,
            stack_name=config.aws.get_stack_name(uuid=session_uuid[:8]),
            ecr_repository_name=config.aws.get_ecr_repository_name(
                uuid=session_uuid[:8]
            ),
            s3_bucket_name=config.aws.get_s3_bucket_name(uuid=session_uuid[:8]),
            tags=tags if tags else None,
            loki_api_key=loki,
            setup_tool="pulumi",
            debug=debug,
        )

        infra_setup.deploy()

        logger.info("Waiting 10s before invoking tests...")
        time.sleep(10)

    test_session_result: Optional[TestSessionResult] = test_runner.run_tests(
        node_ids=test_node_ids,
        flaky_test_retry_enabled=flaky_enabled,
    )

    if test_session_result is not None:
        test_session_result.log_results(failed_test_retry_enabled=flaky_enabled)
