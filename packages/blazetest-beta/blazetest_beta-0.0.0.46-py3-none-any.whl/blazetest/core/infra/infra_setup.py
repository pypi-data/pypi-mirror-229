from blazetest.core.infra.tools import InfraSetupTool, PulumiInfraSetup
from blazetest.core.utils.exceptions import UnsupportedInfraSetupTool


SUPPORTED_INFRA_SETUP_TOOLS = {
    "pulumi": PulumiInfraSetup,
}


class InfraSetup:
    """
    Infrastructure setup class, used to deploy the artifacts to
    the cloud provider (currently, only AWS is supported)
    """

    def __init__(
        self,
        aws_region: str,
        stack_name: str,
        s3_bucket_name: str,
        ecr_repository_name: str,
        loki_api_key: str,
        tags: str,
        setup_tool: str = "pulumi",
        debug: bool = False,
    ):
        if setup_tool not in SUPPORTED_INFRA_SETUP_TOOLS:
            raise UnsupportedInfraSetupTool(
                f"{setup_tool} is not supported for deploying, "
                f"supported: {','.join(list(SUPPORTED_INFRA_SETUP_TOOLS.keys()))}"
            )

        self.infra: InfraSetupTool = SUPPORTED_INFRA_SETUP_TOOLS[setup_tool](
            aws_region=aws_region,
            stack_name=stack_name,
            s3_bucket_name=s3_bucket_name,
            ecr_repository_name=ecr_repository_name,
            loki_api_key=loki_api_key,
            tags=tags,
            debug=debug,
        )

    def deploy(self):
        """
        Deploys the given infrastructure to the cloud provider using given setup tool
        """
        return self.infra.deploy()
