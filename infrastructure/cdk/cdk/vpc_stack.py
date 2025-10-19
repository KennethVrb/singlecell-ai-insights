from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VpcStack(Construct):
    def __init__(
        self, scope, construct_id, max_azs=2, nat_gateways=1, **kwargs
    ):
        super().__init__(scope, construct_id)

        # VPC with public and private subnets across AZs
        self.vpc = ec2.Vpc(
            self,
            'Vpc',
            vpc_name='sc-ai-insights-vpc',
            max_azs=max_azs,
            nat_gateways=nat_gateways,
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
        ec2.FlowLog(
            self,
            'VpcFlowLog',
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            traffic_type=ec2.FlowLogTrafficType.REJECT,
        )
