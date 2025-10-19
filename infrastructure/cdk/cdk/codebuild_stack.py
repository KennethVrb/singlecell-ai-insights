from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct


class CodeBuildStack(Construct):
    def __init__(self, scope, construct_id, aws_region, aws_account, **kwargs):
        super().__init__(scope, construct_id)

        ecr_registry = f'{aws_account}.dkr.ecr.{aws_region}.amazonaws.com'

        # S3 bucket for source code
        self.source_bucket = s3.Bucket(
            self,
            'SourceBucket',
            bucket_name='sc-ai-insights-source',
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )

        # ECR repository for backend Docker images
        self.ecr_repository = ecr.Repository(
            self,
            'BackendRepository',
            repository_name='sc-ai-insights-backend',
            removal_policy=RemovalPolicy.RETAIN,
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description='Keep last 10 images',
                    max_image_count=10,
                    rule_priority=1,
                )
            ],
        )

        # CodeBuild project
        self.build_project = codebuild.Project(
            self,
            'BackendBuildProject',
            project_name='sc-ai-insights-backend-build',
            description='Build Django backend Docker image',
            source=codebuild.Source.s3(
                bucket=self.source_bucket, path='source/backend.zip'
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    'ECR_REGISTRY': codebuild.BuildEnvironmentVariable(
                        value=ecr_registry
                    ),
                    'ECR_BACKEND_REPOSITORY': (
                        codebuild.BuildEnvironmentVariable(
                            value=self.ecr_repository.repository_uri
                        )
                    ),
                    'AWS_DEFAULT_REGION': codebuild.BuildEnvironmentVariable(
                        value=aws_region
                    ),
                },
            ),
            build_spec=codebuild.BuildSpec.from_source_filename(
                'buildspec.yml'
            ),
            timeout=Duration.minutes(30),
            cache=codebuild.Cache.local(
                codebuild.LocalCacheMode.DOCKER_LAYER,
                codebuild.LocalCacheMode.SOURCE,
            ),
        )

        # Grant CodeBuild permissions to read from S3
        self.source_bucket.grant_read(self.build_project)

        # Grant CodeBuild permissions to push to backend ECR
        self.ecr_repository.grant_pull_push(self.build_project)

        # Grant CodeBuild permissions to pull Python base image from ECR
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'ecr:BatchGetImage',
                    'ecr:GetDownloadUrlForLayer',
                    'ecr:BatchCheckLayerAvailability',
                ],
                resources=[
                    f'arn:aws:ecr:{aws_region}:{aws_account}:repository/python'
                ],
            )
        )

        # Add ECR authorization token permission
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'ecr:GetAuthorizationToken',
                ],
                resources=['*'],
            )
        )
