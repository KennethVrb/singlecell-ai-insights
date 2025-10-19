from aws_cdk import CfnOutput, CfnParameter, Stack

from cdk.cdn_stack import CdnStack
from cdk.codebuild_stack import CodeBuildStack
from cdk.database_stack import DatabaseStack
from cdk.ecs_stack import EcsStack
from cdk.frontend_stack import FrontendStack
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

        # ECS - Application runtime
        self.ecs = EcsStack(
            self,
            'Ecs',
            vpc=self.vpc.vpc,
            db_security_group=self.database.db_security_group,
            db_secret=self.database.connection_secret,
            ecr_repository=self.codebuild.ecr_repository,
            aws_region=aws_region,
        )

        # Frontend - S3 bucket for static files
        self.frontend = FrontendStack(self, 'Frontend')

        # CDN - CloudFront distributions
        self.cdn = CdnStack(
            self,
            'Cdn',
            alb=self.ecs.alb,
            frontend_bucket=self.frontend.frontend_bucket,
        )

        # === OUTPUTS ===
        CfnOutput(
            self,
            'SourceBucketName',
            value=self.codebuild.source_bucket.bucket_name,
            description='S3 bucket storing backend source zips',
        )

        CfnOutput(
            self,
            'CodeBuildProjectName',
            value=self.codebuild.build_project.project_name,
            description='CodeBuild project building backend images',
        )

        CfnOutput(
            self,
            'LoadBalancerUrl',
            value=f'http://{self.ecs.alb.load_balancer_dns_name}',
            description='Application Load Balancer URL',
        )

        CfnOutput(
            self,
            'ReportsBucketName',
            value=self.ecs.reports_bucket.bucket_name,
            description='S3 bucket for MultiQC reports',
        )

        CfnOutput(
            self,
            'EcsClusterName',
            value=self.ecs.cluster.cluster_name,
            description='ECS cluster name',
        )

        CfnOutput(
            self,
            'EcsServiceName',
            value=self.ecs.service.service_name,
            description='ECS service name',
        )

        CfnOutput(
            self,
            'ApplicationUrl',
            value=f'https://{self.cdn.distribution.domain_name}',
            description=(
                'Application URL (CloudFront) - Frontend on /, API on /api'
            ),
        )

        CfnOutput(
            self,
            'FrontendBucketName',
            value=self.frontend.frontend_bucket.bucket_name,
            description='S3 bucket for frontend static files',
        )
