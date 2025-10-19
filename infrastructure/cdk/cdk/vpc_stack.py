from aws_cdk import RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from constructs import Construct


class VpcStack(Construct):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id)

        # VPC with public and private subnets across 2 AZs
        self.vpc = ec2.Vpc(
            self,
            'Vpc',
            vpc_name='sc-ai-insights-vpc',
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name='Private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name='Isolated',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        # VPC Flow Logs for monitoring
        log_group = logs.LogGroup(
            self,
            'VpcFlowLogGroup',
            log_group_name='sc-ai-insights-vpc-flow-logs',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK,
        )

        ec2.FlowLog(
            self,
            'VpcFlowLog',
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            traffic_type=ec2.FlowLogTrafficType.REJECT,
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group),
        )
