#!/usr/bin/env python3
import aws_cdk as cdk
from knowlio.knowlio_stack import KnowlioStack
from aws_cdk import Environment, aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as actions
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_cloudformation as cfn

# Define the app
app = cdk.App()

# Retrieve environment configurations from cdk.json context
stages = app.node.get_context("stages")

# Define a new stack to wrap the pipeline creation
# Explicitly set the environment for the pipeline stack
pipeline_env = Environment(account=stages[0]['account'], region=stages[0]['region'])
stack = cdk.Stack(app, "KnowlioPipelineStack", env=pipeline_env)

# CodePipeline Artifacts
source_output = codepipeline.Artifact()
build_output = codepipeline.Artifact()

# Define CodePipeline within the stack
pipeline = codepipeline.Pipeline(
    stack,
    "KnowlioPipeline",
    pipeline_name="KnowlioPipeline",
)

# Add Source Stage
pipeline.add_stage(
    stage_name="Source",
    actions=[
        actions.GitHubSourceAction(
            action_name="GitHubSource",
            owner="vishalln",
            repo="knowlio",
            oauth_token=cdk.SecretValue.secrets_manager("github-token-knowlio-4"),
            output=source_output,
            branch="master",
        )
    ],
)

# Add Build Stage
pipeline.add_stage(
    stage_name="Build",
    actions=[
        actions.CodeBuildAction(
            action_name="CodeBuild",
            project=codebuild.PipelineProject(
                stack,
                "BuildProject",
                build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            ),
            input=source_output,
            outputs=[build_output],
        )
    ],
)

# List of stack classes to deploy
stacks_to_deploy = [
    (KnowlioStack, "KnowlioStack")  # You can add other stacks here in the future
]

# Deploy Resources for each stack in Beta and Prod using the directly fetched stages
for stack_class, stack_name in stacks_to_deploy:
    for stage in stages:
        full_stack_name = f"{stack_name}-{stage['stage']}-{stage['region']}"
        # Define a deployment stage in the pipeline
        deploy_stage = pipeline.add_stage(stage_name=f"Deploy-{full_stack_name}")

        # Create the stack instance dynamically
        stack_instance = stack_class(
            app,
            f"{full_stack_name}",
            env=cdk.Environment(
                account=stage["account"],
                region=stage["region"]
            ),
        )
        
        # Add CloudFormation deployment action
        deploy_stage.add_action(actions.CloudFormationCreateUpdateStackAction(
            action_name=f"Deploy-{full_stack_name}",
            stack_name=full_stack_name,
            template_path=build_output.at_path(f"{full_stack_name}.template.json"),
            admin_permissions=True,
            extra_inputs=[build_output],
            region=stage["region"],
            account=stage["account"],
        ))


app.synth()
