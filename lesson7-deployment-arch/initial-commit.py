from __future__ import print_function
from urllib2 import build_opener, HTTPHandler, Request
from botocore.exceptions import ClientError
import boto3
import json
import httplib
import os

def handler(event, context):
    print("log -- Event: %s " % json.dumps(event))
    codecommit = boto3.client('codecommit')
    
    # Variables
    repo = event['ResourceProperties']['Repo']
    repoConfig = event['ResourceProperties']['RepoConfig']
    masterbranch = 'master'
    devbranch = 'development'

    if event['RequestType'] == 'Create':
        print("log -- Create Event ")
        try:

            # Read in files for Dockerfile Analysis
            buildspecPath = os.environ['LAMBDA_TASK_ROOT'] + "/buildspec_dockerfile.yml"
            buildspec = open(buildspecPath).read()
            hadolintConfigPath = os.environ['LAMBDA_TASK_ROOT'] + "/hadolint.yml"
            hadolintConfig = open(hadolintConfigPath).read()

            # Read in files for Secrets Analysis
            buildspecPathSecrets = os.environ['LAMBDA_TASK_ROOT'] + "/buildspec_secrets.yml"
            buildspecSecrets = open(buildspecPathSecrets).read()
            secretsConfigPath = os.environ['LAMBDA_TASK_ROOT'] + "/secrets_config.json"
            secretsConfig = open(secretsConfigPath).read()

            # Read in files for Vulnerability Scanning 
            buildspecPathVuln = os.environ['LAMBDA_TASK_ROOT'] + "/buildspec_vuln.yml"
            buildspecVuln = open(buildspecPathVuln).read()

            # Read in files for Push Stage
            buildspecPathPush = os.environ['LAMBDA_TASK_ROOT'] + "/buildspec_push.yml"
            buildspecPush = open(buildspecPathPush).read()

            # Read in file for Python app
            DockerfilePath = os.environ['LAMBDA_TASK_ROOT'] + "/Dockerfile"
            Dockerfile = open(DockerfilePath).read()
            AppPath = os.environ['LAMBDA_TASK_ROOT'] + "/index.py"
            App = open(AppPath).read()
            ReqPath = os.environ['LAMBDA_TASK_ROOT'] + "/requirements.txt"
            Req = open(ReqPath).read()

            # Add Dockerfile buildspec file to configs repo
            commit = codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                fileContent=buildspec,
                filePath='buildspec_dockerfile.yml',
                commitMessage='Initial Commit',
                name='Your Lambda Helper'
            )

            commit2 = codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                parentCommitId=commit['commitId'],
                fileContent=hadolintConfig,
                filePath='hadolint.yml',
                commitMessage='Added Hadolint Configuration',
                name='Your Lambda Helper'
            )

            commit3 = codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                parentCommitId=commit2['commitId'],
                fileContent=buildspecSecrets,
                filePath='buildspec_secrets.yml',
                commitMessage='Added Secrets BuildSpec file',
                name='Your Lambda Helper'
            )

            commit4 = codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                parentCommitId=commit3['commitId'],
                fileContent=secretsConfig,
                filePath='secrets_config.json',
                commitMessage='Added Secrets Configuration file',
                name='Your Lambda Helper'
            )

            commit5 = codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                parentCommitId=commit4['commitId'],
                fileContent=buildspecVuln,
                filePath='buildspec_vuln.yml',
                commitMessage='Added Build Spec for Vulnerability Scanning Stage',
                name='Your Lambda Helper'
            )

            codecommit.put_file(
                repositoryName=repoConfig,
                branchName=masterbranch,
                parentCommitId=commit5['commitId'],
                fileContent=buildspecPush,
                filePath='buildspec_push.yml',
                commitMessage='Added Push BuildSpec file',
                name='Your Lambda Helper'
            )

            # Add Dockerfile to application repo
            commita = codecommit.put_file(
                repositoryName=repo,
                branchName=devbranch,
                fileContent=Dockerfile,
                filePath='Dockerfile',
                commitMessage='Initial Commit',
                name='Your Lambda Helper'
            )

            commitb = codecommit.put_file(
                repositoryName=repo,
                branchName=devbranch,
                parentCommitId=commita['commitId'],
                fileContent=App,
                filePath='/app/index.py',
                commitMessage='Added Python App file',
                name='Your Lambda Helper'
            )

            codecommit.put_file(
                repositoryName=repo,
                branchName=devbranch,
                parentCommitId=commitb['commitId'],
                fileContent=Req,
                filePath='requirements.txt',
                commitMessage='Added requirements file',
                name='Your Lambda Helper'
            )

            codecommit.create_branch(
                repositoryName=repo,
                branchName=masterbranch,
                commitId=commita['commitId']
            )

            codecommit.update_default_branch(
                repositoryName=repo,
                defaultBranchName=devbranch
            )
            response = sendResponse(event, context, "SUCCESS", { "Message": "Initial commits - Success" })
        except ClientError as e:
            print(e)
        response = sendResponse(event, context, "SUCCESS", { "Message": "Initial commits - Error" })
    elif event['RequestType'] == 'Update':
        print("log -- Update Event")
        try:
            response = sendResponse(event, context, "SUCCESS", { "Message": "Initial commits - Success" })
        except ClientError as e:
            print(e)
            response = sendResponse(event, context, "SUCCESS", { "Message": "Initial commits - Error" })
    elif event['RequestType'] == 'Delete':
        print("log -- Delete Event")
        response = sendResponse(event, context, "SUCCESS", { "Message": "Deletion successful!" })
    else:
        print("log -- FAILED")
        response = sendResponse(event, context, "FAILED", { "Message": "Unexpected event received from CloudFormation" })
    return response

def sendResponse(event, context, responseStatus, responseData):
    responseBody = json.dumps({
        "Status": responseStatus,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": responseData
    })
    opener = build_opener(HTTPHandler)
    request = Request(event['ResponseURL'], data=responseBody)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(responseBody))
    request.get_method = lambda: 'PUT'
    response = opener.open(request)
    print("Status code: {}".format(response.getcode()))
    print("Status message: {}".format(response.msg))
    return responseBody