from aws_cdk import Duration, RemovalPolicy, SecretValue
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class DatabaseStack(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        db_name='singlecell_ai',
        db_username='postgres',
        instance_class='m5.large',
        **kwargs,
    ):
        super().__init__(scope, construct_id)

        # Security group for RDS
        self.db_security_group = ec2.SecurityGroup(
            self,
            'DatabaseSecurityGroup',
            vpc=vpc,
            description='Security group for RDS PostgreSQL',
            allow_all_outbound=False,
        )

        # Generate database password in Secrets Manager
        self.db_secret = secretsmanager.Secret(
            self,
            'DatabaseSecret',
            secret_name='sc-ai-insights-db-credentials',
            description='Database credentials for SingleCell AI Insights',
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=f'{{"username":"{db_username}"}}',
                generate_string_key='password',
                exclude_characters='/@" \\\'',
                password_length=32,
            ),
            removal_policy=RemovalPolicy.RETAIN,
        )

        # CloudWatch log group for RDS logs
        logs.LogGroup(
            self,
            'DatabaseLogGroup',
            log_group_name='sc-ai-insights-database',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # RDS PostgreSQL instance
        self.db_instance = rds.DatabaseInstance(
            self,
            'Database',
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_17_6
            ),
            instance_type=ec2.InstanceType(instance_class),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[self.db_security_group],
            database_name=db_name,
            credentials=rds.Credentials.from_secret(self.db_secret),
            allocated_storage=20,
            max_allocated_storage=30,
            storage_encrypted=True,
            backup_retention=Duration.days(1),
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,
            publicly_accessible=False,
            multi_az=False,
            cloudwatch_logs_exports=['postgresql'],
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Store connection info in secret
        self.connection_secret = secretsmanager.Secret(
            self,
            'DatabaseConnectionSecret',
            secret_name='sc-ai-insights-db-connection',
            description='Database connection details',
            secret_object_value={
                'host': SecretValue.unsafe_plain_text(
                    self.db_instance.db_instance_endpoint_address
                ),
                'port': SecretValue.unsafe_plain_text(
                    self.db_instance.db_instance_endpoint_port
                ),
                'dbname': SecretValue.unsafe_plain_text(db_name),
                'username': self.db_secret.secret_value_from_json('username'),
                'password': self.db_secret.secret_value_from_json('password'),
            },
            removal_policy=RemovalPolicy.RETAIN,
        )
