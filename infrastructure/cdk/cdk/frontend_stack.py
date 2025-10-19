from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct


class FrontendStack(Construct):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id)

        # S3 bucket for frontend static files
        self.frontend_bucket = s3.Bucket(
            self,
            'FrontendBucket',
            bucket_name='sc-ai-insights-frontend',
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True,
            ),
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )
