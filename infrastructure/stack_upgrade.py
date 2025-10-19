#!/usr/bin/env python3
"""
Stack upgrade script for deploying code changes.
Uploads source to S3 and triggers CodeBuild to rebuild the container.
"""

import argparse
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import boto3


def get_stack_outputs(stack_name):
    """Fetch outputs from the deployed CDK stack."""
    cfn = boto3.client('cloudformation')
    try:
        response = cfn.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        outputs = {
            output['OutputKey']: output['OutputValue']
            for output in stack.get('Outputs', [])
        }
        return outputs
    except Exception as e:
        print(f'❌ Error fetching stack outputs: {e}')
        print(f'   Make sure the CDK stack "{stack_name}" is deployed')
        sys.exit(1)


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def create_source_archive(output_path):
    """Create a zip archive of the backend source code."""
    project_root = get_project_root()
    backend_dir = project_root / 'backend'
    infrastructure_dir = project_root / 'infrastructure'

    print(f'📦 Creating source archive from {project_root}...')

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add backend files
        for root, dirs, files in os.walk(backend_dir):
            # Skip unwanted directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    '__pycache__',
                    'venv',
                    'env',
                    '.pytest_cache',
                    'htmlcov',
                    'staticfiles',
                ]
            ]

            for file in files:
                # Skip unwanted files
                if file.endswith(
                    (
                        '.pyc',
                        '.pyo',
                        '.log',
                        '.sqlite3',
                        '.env',
                        '.env-example',
                    )
                ):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(project_root)
                zipf.write(file_path, arcname)
                print(f'  Added: {arcname}')

        # Add Dockerfile, buildspec, and entrypoint
        docker_backend_dir = infrastructure_dir / 'docker' / 'backend'
        dockerfile = docker_backend_dir / 'Dockerfile'
        buildspec = docker_backend_dir / 'buildspec.yml'
        entrypoint = docker_backend_dir / 'entrypoint.sh'

        zipf.write(dockerfile, 'Dockerfile')
        zipf.write(buildspec, 'buildspec.yml')
        zipf.write(entrypoint, 'entrypoint.sh')
        print('  Added: Dockerfile')
        print('  Added: buildspec.yml')
        print('  Added: entrypoint.sh')

    print(f'✅ Source archive created: {output_path}')


def upload_to_s3(file_path, bucket_name, key):
    """Upload file to S3."""
    s3 = boto3.client('s3')

    print(f'📤 Uploading to s3://{bucket_name}/{key}...')
    s3.upload_file(str(file_path), bucket_name, key)
    print('✅ Upload complete')


def trigger_codebuild(project_name, source_version):
    """Trigger CodeBuild project."""
    codebuild = boto3.client('codebuild')

    print(f'🔨 Triggering CodeBuild project: {project_name}...')

    response = codebuild.start_build(
        projectName=project_name, sourceVersion=source_version
    )

    build_id = response['build']['id']
    print(f'✅ Build started: {build_id}')
    print(
        f'   Monitor: https://console.aws.amazon.com/codesuite/codebuild/projects/{project_name}/build/{build_id}/'
    )

    return build_id


def force_ecs_deployment(cluster_name, service_name):
    """Force a new deployment of an ECS service."""
    ecs = boto3.client('ecs')

    print(f'🔄 Forcing new deployment of ECS service: {service_name}...')

    try:
        response = ecs.update_service(
            cluster=cluster_name,
            service=service_name,
            forceNewDeployment=True,
        )

        deployment_id = response['service']['deployments'][0]['id']
        print(f'✅ Deployment triggered: {deployment_id}')
        print(
            f'   Monitor: https://console.aws.amazon.com/ecs/v2/clusters/'
            f'{cluster_name}/services/{service_name}/health'
        )
        return True
    except Exception as e:
        print(f'❌ Failed to force deployment: {e}')
        return False


def wait_for_ecs_deployment(cluster_name, service_name):
    """Wait for ECS service deployment to complete."""
    ecs = boto3.client('ecs')
    max_attempts = 60
    delay = 10

    print()
    print('⏳ Waiting for ECS deployment to stabilize...')
    print('   (New task must start and old task must drain)')

    for attempt in range(max_attempts):
        try:
            response = ecs.describe_services(
                cluster=cluster_name, services=[service_name]
            )

            if not response['services']:
                print('❌ Service not found')
                return False

            service = response['services'][0]
            deployments = service['deployments']

            # Check if only one deployment (PRIMARY) exists and it's stable
            if len(deployments) == 1:
                deployment = deployments[0]
                if deployment['status'] == 'PRIMARY':
                    running_count = deployment['runningCount']
                    desired_count = deployment['desiredCount']

                    if running_count == desired_count:
                        print()
                        print('✅ ECS deployment complete!')
                        print(
                            f'   Running tasks: '
                            f'{running_count}/{desired_count}'
                        )
                        return True

            # Show progress
            if attempt == 0:
                print('   Deploying', end='', flush=True)
            else:
                print('.', end='', flush=True)

            time.sleep(delay)

        except Exception as e:
            print(f'\n❌ Error checking deployment status: {e}')
            return False

    print('\n⚠️  Deployment wait timed out after 10 minutes')
    print('   Deployment may still be in progress. Check AWS Console.')
    return False


def upgrade_backend(
    bucket_name, codebuild_project, cluster_name, service_name
):
    """Upgrade backend by uploading source and triggering CodeBuild."""
    import tempfile

    # Create source archive
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        archive_path = tmp.name

    try:
        create_source_archive(archive_path)

        # Upload to S3 (always use same key, S3 versioning tracks history)
        s3_key = 'source/backend.zip'
        upload_to_s3(archive_path, bucket_name, s3_key)

        # Get the version ID of the uploaded object
        s3 = boto3.client('s3')
        response = s3.head_object(Bucket=bucket_name, Key=s3_key)
        version_id = response.get('VersionId', '')

        # Trigger CodeBuild with version ID
        build_id = trigger_codebuild(
            codebuild_project, source_version=version_id
        )

        print('🎉 Backend build triggered successfully!')
        print(f'   Build ID: {build_id}')
        print('   Check AWS Console for build progress')
        print()
        print('⏳ Waiting for build to complete before forcing deployment...')
        print('   (This may take a few minutes)')

        # Wait for CodeBuild to finish
        codebuild = boto3.client('codebuild')
        max_attempts = 40
        delay = 15

        for attempt in range(max_attempts):
            try:
                response = codebuild.batch_get_builds(ids=[build_id])
                if not response['builds']:
                    print('⚠️  Build not found')
                    return False

                build = response['builds'][0]
                status = build['buildStatus']

                if status == 'SUCCEEDED':
                    print('✅ Build completed successfully!')
                    print()
                    # Force ECS deployment with new image
                    if not force_ecs_deployment(cluster_name, service_name):
                        return False
                    # Wait for deployment to complete
                    if not wait_for_ecs_deployment(cluster_name, service_name):
                        return False
                    break
                elif status in ['FAILED', 'FAULT', 'TIMED_OUT', 'STOPPED']:
                    print(f'❌ Build failed with status: {status}')
                    return False
                elif status == 'IN_PROGRESS':
                    if attempt == 0:
                        print('   Building', end='', flush=True)
                    else:
                        print('.', end='', flush=True)
                    time.sleep(delay)
                else:
                    print(f'   Build status: {status}')
                    time.sleep(delay)
            except Exception as e:
                print(f'\n⚠️  Error checking build status: {e}')
                print(
                    '   You may need to manually force ECS deployment '
                    'after build completes'
                )
                return False
        else:
            print('\n⚠️  Build wait timed out after 10 minutes')
            print(
                '   You may need to manually force ECS deployment '
                'after build completes'
            )
            return False

        return True

    finally:
        # Clean up temp file
        if os.path.exists(archive_path):
            os.remove(archive_path)


def get_aws_account_and_region():
    """Get AWS account ID and region from AWS CLI."""
    try:
        # Get account ID
        result = subprocess.run(
            [
                'aws',
                'sts',
                'get-caller-identity',
                '--query',
                'Account',
                '--output',
                'text',
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        account = result.stdout.strip()

        # Get region
        result = subprocess.run(
            ['aws', 'configure', 'get', 'region'],
            capture_output=True,
            text=True,
            check=True,
        )
        region = result.stdout.strip()

        return account, region
    except subprocess.CalledProcessError as e:
        print(f'❌ Failed to get AWS credentials: {e}')
        print('   Make sure AWS CLI is configured: aws configure')
        return None, None


def deploy_frontend(frontend_bucket, app_url):
    """Build and deploy frontend to S3."""
    project_root = get_project_root()
    frontend_dir = project_root / 'frontend'

    if not frontend_dir.exists():
        print('❌ Frontend directory not found')
        return False

    print('🎨 Building frontend...')
    print(f'   Frontend dir: {frontend_dir}')
    print(f'   API URL: {app_url}')
    print()

    # Set environment variable for build
    env = os.environ.copy()
    env['VITE_API_BASE_URL'] = app_url

    try:
        # Install dependencies
        print('📦 Installing dependencies...')
        subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            check=True,
            capture_output=True,
        )
        print('✅ Dependencies installed')
        print()

        # Build frontend
        print('🔨 Building production bundle...')
        subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            env=env,
            check=True,
        )
        print('✅ Build complete')
        print()

        # Upload to S3
        dist_dir = frontend_dir / 'dist'
        if not dist_dir.exists():
            print('❌ Build output directory not found')
            return False

        print(f'📤 Uploading to s3://{frontend_bucket}...')
        subprocess.run(
            [
                'aws',
                's3',
                'sync',
                str(dist_dir),
                f's3://{frontend_bucket}/',
                '--delete',
            ],
            check=True,
        )
        print('✅ Upload complete')
        print()

        print('🎉 Frontend deployed successfully!')
        print(f'   Access at: {app_url}')
        return True

    except subprocess.CalledProcessError as e:
        print(f'❌ Frontend deployment failed: {e}')
        return False


def deploy_infrastructure(cdk_dir, stack_prefix='ScAI', parameters=None):
    """Deploy infrastructures."""
    print('🏗️  Deploying infrastructures...')

    # Get AWS account and region
    account, region = get_aws_account_and_region()
    if not account or not region:
        return False

    print(f'   Account: {account}')
    print(f'   Region: {region}')
    print(f'   Stack Prefix: {stack_prefix}')
    if parameters:
        print(f'   Parameters: {parameters}')
    print()

    # Set environment variables for CDK
    env = os.environ.copy()
    env['CDK_DEFAULT_ACCOUNT'] = account
    env['CDK_DEFAULT_REGION'] = region
    env['CDK_STACK_PREFIX'] = stack_prefix

    try:
        cmd = ['cdk', 'deploy', '--all', '--require-approval', 'never']

        # Add parameters if provided (prefix with stack name)
        if parameters:
            for key, value in parameters.items():
                param = f'{stack_prefix}Stack:{key}={value}'
                cmd.extend(['--parameters', param])

        subprocess.run(
            cmd,
            cwd=cdk_dir,
            env=env,
            check=True,
        )
        print()
        print('✅ Infrastructure deployment complete!')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ CDK deployment failed: {e}')
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Deploy infrastructure and application components'
    )
    parser.add_argument(
        '--infrastructure',
        action='store_true',
        help='Deploy platform infrastructures (VPC, DB, ECS, etc.)',
    )
    parser.add_argument(
        '--backend',
        action='store_true',
        help='Build and push backend Docker image',
    )
    parser.add_argument(
        '--frontend',
        action='store_true',
        help='Build and deploy frontend to S3',
    )
    parser.add_argument(
        '--stack-prefix',
        default='ScAI',
        help='Stack name prefix (default: ScAI)',
    )
    parser.add_argument(
        '--param',
        action='append',
        metavar='KEY=VALUE',
        help='CloudFormation parameter (can be used multiple times)',
    )

    args = parser.parse_args()

    # Parse parameters
    parameters = {}
    if args.param:
        for param in args.param:
            if '=' not in param:
                print(f'❌ Invalid parameter format: {param}')
                print('   Use: --param KEY=VALUE')
                sys.exit(1)
            key, value = param.split('=', 1)
            parameters[key] = value

    # If no flags specified, show help
    if not args.infrastructure and not args.backend and not args.frontend:
        parser.print_help()
        print()
        print('Examples:')
        print('  ./stack_upgrade.py --infrastructure')
        print('  ./stack_upgrade.py --backend')
        print('  ./stack_upgrade.py --frontend')
        print('  ./stack_upgrade.py --infrastructure --backend --frontend')
        print('  ./stack_upgrade.py --infrastructure --param VpcMaxAzs=2')
        print(
            '  ./stack_upgrade.py --infrastructure --param VpcMaxAzs=2 '
            '--param VpcNatGateways=2'
        )
        sys.exit(1)

    project_root = get_project_root()
    cdk_dir = project_root / 'infrastructure' / 'cdk'

    try:
        # Deploy infrastructure if requested
        if args.infrastructure:
            success = deploy_infrastructure(
                cdk_dir, args.stack_prefix, parameters if parameters else None
            )
            if not success:
                sys.exit(1)
            print()

        # Deploy backend if requested
        if args.backend:
            # Fetch stack outputs
            stack_name = f'{args.stack_prefix}Stack'
            print(f'📋 Fetching outputs from stack: {stack_name}')
            outputs = get_stack_outputs(stack_name)

            # Extract required values from stack outputs
            source_bucket = outputs.get('SourceBucketName')
            codebuild_project = outputs.get('CodeBuildProjectName')
            cluster_name = outputs.get('EcsClusterName')
            service_name = outputs.get('EcsServiceName')

            if not all(
                [source_bucket, codebuild_project, cluster_name, service_name]
            ):
                print(
                    '❌ Error: Could not find required outputs in stack. '
                    'Deploy infrastructure first.'
                )
                print(f'   Found outputs: {list(outputs.keys())}')
                sys.exit(1)

            print()
            success = upgrade_backend(
                source_bucket, codebuild_project, cluster_name, service_name
            )
            if not success:
                print(
                    '⚠️  Backend deployment may be incomplete. '
                    'Check AWS Console.'
                )
                sys.exit(1)
            else:
                print()
                print('🎉 Backend deployment complete!')
                print(f'   API available at: {outputs.get("ApplicationUrl")}')

        # Deploy frontend if requested
        if args.frontend:
            # Fetch stack outputs
            stack_name = f'{args.stack_prefix}Stack'
            print(f'📋 Fetching outputs from stack: {stack_name}')
            outputs = get_stack_outputs(stack_name)

            # Extract required values
            frontend_bucket = outputs.get('FrontendBucketName')
            app_url = outputs.get('ApplicationUrl')

            if not frontend_bucket or not app_url:
                print(
                    '❌ Error: Could not find required outputs in stack. '
                    'Deploy infrastructure first.'
                )
                print(f'   Found outputs: {list(outputs.keys())}')
                sys.exit(1)

            print()
            success = deploy_frontend(frontend_bucket, app_url)
            if not success:
                print('⚠️  Frontend deployment failed.')
                sys.exit(1)

        print()
        print('🎉 All deployments complete!')

    except subprocess.CalledProcessError as e:
        print(f'❌ Command failed: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
