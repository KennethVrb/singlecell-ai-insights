from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class EcsStack(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        vpc,
        db_security_group,
        db_secret,
        ecr_repository,
        aws_region,
        cloudfront_domain=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id)

        # Django secret key
        django_secret = secretsmanager.Secret(
            self,
            'DjangoSecret',
            secret_name='sc-ai-insights-django-secret',
            description='Django secret key',
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{}',
                generate_string_key='secret_key',
                exclude_characters='"\\',
                password_length=50,
            ),
            removal_policy=RemovalPolicy.RETAIN,
        )

        # S3 bucket for reports
        self.reports_bucket = s3.Bucket(
            self,
            'ReportsBucket',
            bucket_name='sc-ai-insights-reports',
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=['*'],
                    allowed_headers=['*'],
                    max_age=3000,
                )
            ],
        )

        # ECS Cluster
        self.cluster = ecs.Cluster(
            self,
            'Cluster',
            cluster_name='sc-ai-insights-cluster',
            vpc=vpc,
            container_insights=True,  # @aws-cdk/aws-ecs:containerInsights
        )

        # Task execution role
        task_execution_role = iam.Role(
            self,
            'TaskExecutionRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'service-role/AmazonECSTaskExecutionRolePolicy'
                )
            ],
        )

        # Grant access to read secrets
        db_secret.grant_read(task_execution_role)
        django_secret.grant_read(task_execution_role)

        # Task role for application
        task_role = iam.Role(
            self,
            'TaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        )

        # Grant S3 access
        self.reports_bucket.grant_read_write(task_role)

        # Grant HealthOmics access
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'omics:ListRuns',
                    'omics:GetRun',
                    'omics:GetWorkflow',
                ],
                resources=['*'],
            )
        )

        # Grant Bedrock access
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'bedrock:InvokeModel',
                    'bedrock:InvokeModelWithResponseStream',
                ],
                resources=['*'],
            )
        )

        # Grant S3 read access to HealthOmics output bucket
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    's3:GetObject',
                    's3:ListBucket',
                ],
                resources=[
                    'arn:aws:s3:::kv-healthomics-output',
                    'arn:aws:s3:::kv-healthomics-output/*',
                ],
            )
        )

        # CloudWatch log group
        log_group = logs.LogGroup(
            self,
            'ServiceLogGroup',
            log_group_name='sc-ai-insights-backend',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            'TaskDefinition',
            memory_limit_mib=2048,
            cpu=1024,
            execution_role=task_execution_role,
            task_role=task_role,
        )

        # Container definition
        container = task_definition.add_container(
            'DjangoContainer',
            image=ecs.ContainerImage.from_ecr_repository(
                ecr_repository, tag='latest'
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix='backend', log_group=log_group
            ),
            environment={
                'DJANGO_DEBUG': 'False',
                'DJANGO_ALLOWED_HOSTS': '*',
                'DJANGO_CSRF_TRUSTED_ORIGINS': (
                    f'https://{cloudfront_domain}' if cloudfront_domain else ''
                ),
                'DJANGO_CORS_ALLOWED_ORIGINS': (
                    f'https://{cloudfront_domain}' if cloudfront_domain else ''
                ),
                'JWT_COOKIE_SAMESITE': 'None',
                'JWT_COOKIE_SECURE': 'True',
                'AWS_REGION': aws_region,
                'REPORTS_BUCKET': self.reports_bucket.bucket_name,
                'AWS_S3_PRESIGN_TTL': '3600',
            },
            secrets={
                'DJANGO_SECRET_KEY': ecs.Secret.from_secrets_manager(
                    django_secret, 'secret_key'
                ),
                'DB_HOST': ecs.Secret.from_secrets_manager(db_secret, 'host'),
                'DB_PORT': ecs.Secret.from_secrets_manager(db_secret, 'port'),
                'DB_NAME': ecs.Secret.from_secrets_manager(
                    db_secret, 'dbname'
                ),
                'DB_USER': ecs.Secret.from_secrets_manager(
                    db_secret, 'username'
                ),
                'DB_PASSWORD': ecs.Secret.from_secrets_manager(
                    db_secret, 'password'
                ),
            },
            health_check=ecs.HealthCheck(
                command=[
                    'CMD-SHELL',
                    'curl -f http://localhost:8000/api/health/ || exit 1',
                ],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Security group for ECS service
        service_security_group = ec2.SecurityGroup(
            self,
            'ServiceSecurityGroup',
            vpc=vpc,
            description='Security group for ECS service',
            allow_all_outbound=True,
        )

        # Allow ECS to connect to RDS
        db_security_group.add_ingress_rule(
            peer=service_security_group,
            connection=ec2.Port.tcp(5432),
            description='Allow ECS service to access RDS',
        )

        # Application Load Balancer
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            'LoadBalancer',
            vpc=vpc,
            internet_facing=True,
            load_balancer_name='sc-ai-insights-alb',
        )

        # ALB security group - allow HTTP/HTTPS
        self.alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), 'Allow HTTP from anywhere'
        )
        self.alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(443), 'Allow HTTPS from anywhere'
        )

        # Target group
        target_group = elbv2.ApplicationTargetGroup(
            self,
            'TargetGroup',
            vpc=vpc,
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path='/api/health/',
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            ),
            deregistration_delay=Duration.seconds(30),
        )

        # HTTP listener
        self.alb.add_listener(
            'HttpListener',
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group],
        )

        # Allow ALB to reach ECS service
        service_security_group.add_ingress_rule(
            peer=self.alb.connections.security_groups[0],
            connection=ec2.Port.tcp(8000),
            description='Allow ALB to reach ECS service',
        )

        # Fargate service
        self.service = ecs.FargateService(
            self,
            'Service',
            service_name='sc-ai-insights-service',
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=1,
            min_healthy_percent=100,
            max_healthy_percent=200,
            assign_public_ip=False,
            security_groups=[service_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            health_check_grace_period=Duration.seconds(120),
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            enable_execute_command=True,
        )

        # Attach service to target group
        self.service.attach_to_application_target_group(target_group)

        # Auto scaling
        scaling = self.service.auto_scale_task_count(
            max_capacity=4, min_capacity=1
        )

        scaling.scale_on_cpu_utilization(
            'CpuScaling',
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        scaling.scale_on_memory_utilization(
            'MemoryScaling',
            target_utilization_percent=80,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
