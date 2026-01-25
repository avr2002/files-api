# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "aws-cdk-lib>=2.233.0",
#     "constructs>=10.4.4",
# ]
# ///
"""
Creating an IAM Role for GitHub OIDC to allow GitHub Actions to assume the role and deploy CDK stack.

Usage: ./run cdk-deploy:github_oidc_stack <github-repo:owner/repo> <create-oidc-provider:true|false>

^^^When running for the first time, set --create-oidc-provider to true (false by default) to create the
OIDC provider for your AWS account. The OIDC provider can be created only once per AWS account.

Information on GitHub OIDC provider:

- official docs by GitHub: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- aws blog: https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/
- where to find the GitHub Actions thumbprints for the OIDC provider: https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/
- video on setting this up: https://www.youtube.com/watch?v=USIVWqXVv_U
- mlops-club github: https://github.com/mlops-club/aws-oidc-github-actions-demo/blob/main/__main__.py
"""

import os
import re

import aws_cdk as cdk
from aws_cdk import Stack, aws_iam as iam
from constructs import Construct


class GitHubActionsOIDCRoleStack(Stack):
    """Stack to create an IAM Role for GitHub OIDC."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # # define parameter or context variable for GitHub repository name and owner for the cdk app
        # github_repo_parameter = cdk.CfnParameter(
        #     self,
        #     "GitHubRepo",
        #     type="String",
        #     description="GitHub repository name in the format 'owner/repo'. E.g., 'amitvraj/my-repo'",
        #     allowed_pattern=".+/.+",
        #     default=None,  # User must provide value
        # )

        # Use context variable for GitHub repository name and owner
        github_repo = self.node.try_get_context("github_repo")
        if not github_repo:
            raise ValueError("GitHub repository must be provided in the context in the format 'owner/repo'.")

        if github_repo:
            # Match the pattern 'owner/repo'
            if not re.match(r"^[^/]+/[^/]+$", github_repo):
                raise ValueError("GitHub repository must be in the format 'owner/repo'.")

        # Check if we should create a new OIDC provider or use an existing one
        create_oidc_provider_str = self.node.try_get_context("create_oidc_provider")

        # Context values from CLI are strings, so we need to check the string value
        if create_oidc_provider_str.lower() == "false":
            oidc_provider_arn = f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com"
            # Import existing OIDC provider
            # github_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            #     self,
            #     id="GitHubOIDCProvider",
            #     open_id_connect_provider_arn=oidc_provider_arn,
            # )
        else:
            # Create a new OIDC provider - This can be ONLY ONE per AWS account
            github_provider = iam.OidcProviderNative(
                self,
                id="GitHubOIDCProvider",
                oidc_provider_name="GitHubActionsOIDCProvider",
                url="https://token.actions.githubusercontent.com",
                client_ids=["sts.amazonaws.com"],
                thumbprints=[
                    # https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/
                    "6938fd4d98bab03faadb97b34396831e3780aea1",
                    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
                ],
                # ^^^These thumbprints are now not needed as AWS manages them automatically
                # ref: https://github.blog/changelog/2023-07-13-github-actions-oidc-integration-with-aws-no-longer-requires-pinning-of-intermediate-tls-certificates/
            )
            oidc_provider_arn = github_provider.oidc_provider_arn

        # Create the IAM Role for OIDC Identity Provider to assume and we will scope it to the specific GitHub repository
        github_oidc_role = iam.Role(
            self,
            id="GitHubActionsOIDCRole",
            role_name=f"GitHubActionsOIDCRole-{github_repo.replace('/', '-')}",
            description="IAM Role for GitHub Actions to assume via OIDC for deploying CDK stack.",
            assumed_by=iam.FederatedPrincipal(
                # federated=f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com",
                federated=oidc_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_repo}:*",
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )

        # Attach necessary policies to the role (e.g., AdministratorAccess, PowerUserAccess, or custom policies)
        github_oidc_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("PowerUserAccess"))

        # Output the ARN of the IAM Role
        cdk.CfnOutput(
            self,
            "GitHubActionsOIDCRoleARNOutput",
            value=github_oidc_role.role_arn,
            description="ARN of the IAM Role for GitHub Actions OIDC",
        )


###############
# --- App --- #
###############

# CDK App
app = cdk.App()

cdk.Tags.of(app).add("project", "github-oidc-integration")
cdk.Tags.of(app).add("managed-by", "cdk")


GitHubActionsOIDCRoleStack(
    app,
    construct_id="GitHubActionsOIDCRoleStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=cdk.Environment(account='123456789012', region='us-east-1'),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()
