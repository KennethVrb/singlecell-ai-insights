from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from constructs import Construct


class CdnStack(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        alb,
        frontend_bucket,
        **kwargs,
    ):
        super().__init__(scope, construct_id)

        # Backend origin request policy (forward everything)
        backend_origin_policy = cloudfront.OriginRequestPolicy(
            self,
            'BackendOriginRequestPolicy',
            origin_request_policy_name='sc-ai-backend-policy',
            cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
            header_behavior=cloudfront.OriginRequestHeaderBehavior.all(),
            query_string_behavior=(
                cloudfront.OriginRequestQueryStringBehavior.all()
            ),
        )

        # Single CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self,
            'Distribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    frontend_bucket
                ),
                viewer_protocol_policy=(
                    cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                ),
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={
                '/api/*': cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(
                        alb,
                        protocol_policy=(
                            cloudfront.OriginProtocolPolicy.HTTP_ONLY
                        ),
                        http_port=80,
                    ),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=backend_origin_policy,
                    viewer_protocol_policy=(
                        cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                    ),
                ),
                '/admin/*': cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(
                        alb,
                        protocol_policy=(
                            cloudfront.OriginProtocolPolicy.HTTP_ONLY
                        ),
                        http_port=80,
                    ),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=backend_origin_policy,
                    viewer_protocol_policy=(
                        cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                    ),
                ),
                '/static/*': cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(
                        alb,
                        protocol_policy=(
                            cloudfront.OriginProtocolPolicy.HTTP_ONLY
                        ),
                        http_port=80,
                    ),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                    origin_request_policy=backend_origin_policy,
                    viewer_protocol_policy=(
                        cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                    ),
                ),
            },
            default_root_object='index.html',
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path='/index.html',
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path='/index.html',
                ),
            ],
            comment='Unified distribution for frontend and backend',
        )
