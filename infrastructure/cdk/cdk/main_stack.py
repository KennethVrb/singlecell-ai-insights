from aws_cdk import CfnParameter, Stack

from cdk.codebuild_stack import CodeBuildStack
from cdk.database_stack import DatabaseStack
from cdk.vpc_stack import VpcStack


class MainStack(Stack):
    def __init__(self, scope, construct_id, env, **kwargs):
        super().__init__(scope, construct_id, env=env, **kwargs)

        aws_region = env.region
        aws_account = env.account

        # === INPUT PARAMETERS ===

        # Database Configuration
        db_name = CfnParameter(
            self,
            'DatabaseName',
            default='singlecell_ai',
            description='Database name',
        )

        db_username = CfnParameter(
            self,
            'DatabaseUsername',
            default='postgres',
            description='Database master username',
        )

        db_instance_class = CfnParameter(
            self,
            'DatabaseInstanceClass',
            default='m5.large',
            allowed_values=['m5.large', 'm5.xlarge', 'm5.2xlarge'],
            description='Database instance type',
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
        self.vpc = VpcStack(self, 'Vpc')

        # Database - PostgreSQL RDS
        self.database = DatabaseStack(
            self,
            'Database',
            vpc=self.vpc.vpc,
            db_name=db_name.value_as_string,
            db_username=db_username.value_as_string,
            instance_class=db_instance_class.value_as_string,
        )

        # CodeBuild - Build pipeline
        self.codebuild = CodeBuildStack(
            self,
            'CodeBuild',
            aws_region=aws_region,
            aws_account=aws_account,
        )

        # === OUTPUTS ===
        # Future: Add outputs for external resources (e.g., CloudFront URL)
