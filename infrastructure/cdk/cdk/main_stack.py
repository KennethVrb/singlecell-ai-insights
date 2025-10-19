from aws_cdk import CfnParameter, Stack

from cdk.codebuild_stack import CodeBuildStack
from cdk.vpc_stack import VpcStack


class MainStack(Stack):
    def __init__(self, scope, construct_id, env, **kwargs):
        super().__init__(scope, construct_id, env=env, **kwargs)

        aws_region = env.region
        aws_account = env.account

        # === INPUT PARAMETERS ===

        # VPC Configuration
        vpc_max_azs = CfnParameter(
            self,
            'VpcMaxAzs',
            type='Number',
            default=1,  # Setting as 1 for cost-effectiveness/hackathon
            allowed_values=['1', '2', '3'],
            description='Number of Availability Zones for VPC',
        )

        vpc_nat_gateways = CfnParameter(
            self,
            'VpcNatGateways',
            type='Number',
            default=1,  # Setting as 1 for cost-effectiveness/hackathon
            allowed_values=['1', '2'],
            description='Number of NAT Gateways (1=shared, 2=HA)',
        )

        # S3 Bucket Names
        CfnParameter(
            self,
            'ReportsBucketName',
            default='sc-ai-insights-reports',
            description='S3 bucket for MultiQC reports',
        )

        # === CREATE CHILD STACKS ===

        # VPC - Foundation
        self.vpc = VpcStack(
            self,
            'Vpc',
            max_azs=vpc_max_azs.value_as_number,
            nat_gateways=vpc_nat_gateways.value_as_number,
        )

        # CodeBuild - Build pipeline
        self.codebuild = CodeBuildStack(
            self,
            'CodeBuild',
            aws_region=aws_region,
            aws_account=aws_account,
        )

        # === OUTPUTS ===

        # in future this will output things like the cloudfront uri.
        # This should only output information needed externally
