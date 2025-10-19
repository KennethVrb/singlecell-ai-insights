#!/usr/bin/env python3
"""
Stack upgrade script for deploying code changes.
Uploads source to S3 and triggers CodeBuild to rebuild the container.
"""

import argparse
import os
import subprocess
import sys
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

        # Add Dockerfile and buildspec
        dockerfile = infrastructure_dir / 'docker' / 'backend' / 'Dockerfile'
        buildspec = infrastructure_dir / 'docker' / 'backend' / 'buildspec.yml'

        zipf.write(dockerfile, 'Dockerfile')
        zipf.write(buildspec, 'buildspec.yml')
        print('  Added: Dockerfile')
        print('  Added: buildspec.yml')

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


def upgrade_backend(bucket_name, codebuild_project):
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


def deploy_infrastructure(cdk_dir):
    """Deploy CDK infrastructure stack."""
    print('🏗️  Deploying CDK infrastructure...')

    # Get AWS account and region
    account, region = get_aws_account_and_region()
    if not account or not region:
        return False

    print(f'   Account: {account}')
    print(f'   Region: {region}')
    print()

    # Set environment variables for CDK
    env = os.environ.copy()
    env['CDK_DEFAULT_ACCOUNT'] = account
    env['CDK_DEFAULT_REGION'] = region

    try:
        subprocess.run(
            ['cdk', 'deploy', '--require-approval', 'never'],
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
        help='Deploy CDK infrastructure stack',
    )
    parser.add_argument(
        '--backend',
        action='store_true',
        help='Build and deploy backend (CodeBuild + ECS)',
    )
    parser.add_argument(
        '--stack-name',
        default='ScAICodeBuildStack',
        help='CDK stack name (default: ScAICodeBuildStack)',
    )

    args = parser.parse_args()

    # If no flags specified, show help
    if not args.infrastructure and not args.backend:
        parser.print_help()
        print()
        print('Examples:')
        print('./stack_upgrade.py --infrastructure # Deploy CDK stack')
        print('./stack_upgrade.py --backend # Build backend image')
        print(
            './stack_upgrade.py --infrastructure --backend  '
            '# Deploy everything'
        )
        sys.exit(1)

    project_root = get_project_root()
    cdk_dir = project_root / 'infrastructure' / 'cdk'

    try:
        # Deploy infrastructure first if requested
        if args.infrastructure:
            success = deploy_infrastructure(cdk_dir)
            if not success:
                sys.exit(1)
            print()

        # Deploy backend if requested
        if args.backend:
            # Fetch stack outputs
            print(f'📋 Fetching outputs from stack: {args.stack_name}')
            outputs = get_stack_outputs(args.stack_name)

            # Extract required values from stack outputs
            source_bucket = outputs.get('SourceBucketName')
            codebuild_project = outputs.get('CodeBuildProjectName')

            if not source_bucket or not codebuild_project:
                print(
                    '❌ Error: Could not find required outputs in stack. '
                    'Deploy infrastructure first.'
                )
                sys.exit(1)

            print()
            upgrade_backend(source_bucket, codebuild_project)

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
