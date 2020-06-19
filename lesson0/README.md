# GuardDuty Test
[Amazon GuardDuty](https://aws.amazon.com/guardduty/).

aws guardduty list-detectors

aws guardduty delete-detector --detector-id TBD

aws ec2 describe-flow-logs



```
mkdir ~/environment/csoa/

aws s3 mb s3://csoa-0-$(aws sts get-caller-identity --output text --query 'Account')
cd ~/environment/csoa/
touch test-guardduty.yml
touch GuardDutyThreatIntelSet.txt
touch GuardDutyIpSet.txt
touch vpc-flowlogs.yml
```

Populate the above files.

```
cd ~/environment/csoa/
aws s3 sync ~/environment/csoa/ s3://csoa-0-$(aws sts get-caller-identity --output text --query 'Account')
```

Create the CloudFormation stack for Enabling VPC.


```
aws cloudformation create-stack --stack-name vpc-2azs --capabilities CAPABILITY_NAMED_IAM --disable-rollback --template-body file:///home/ec2-user/environment/aws-security-workshop/lesson0/vpc-2azs.yml
```

Create the CloudFormation stack for Enabling VPC Flow Logs.


```
aws cloudformation create-stack --stack-name vpc-flow-logs-s3 --capabilities CAPABILITY_NAMED_IAM --disable-rollback --template-body file:///home/ec2-user/environment/aws-security-workshop/lesson0/vpc-flow-logs-s3.yml --parameters ParameterKey=ParentVPCStack,ParameterValue=vpc-2azs
```

Create the CloudFormation stack for Enabling GuardDuty.

```
aws cloudformation create-stack --stack-name test-guardduty --capabilities CAPABILITY_NAMED_IAM --disable-rollback --template-body file:///home/ec2-user/environment/aws-security-workshop/lesson0/test-guardduty.yml --parameters ParameterKey=ThreatIntelSetUrl,ParameterValue=https://s3.amazonaws.com/csoa-0-$(aws sts get-caller-identity --output text --query 'Account')/GuardDutyIpSet.txt ParameterKey=IpSetUrl,ParameterValue=https://s3.amazonaws.com/csoa-0-$(aws sts get-caller-identity --output text --query 'Account')/GuardDutyThreatIntelSet.txt
```

A ThreatIntelSet consists of known malicious IP addresses. You can provide a list of these IP Addresses in a TXT file. An IP set is a list of trusted IP addresses that have been whitelisted for secure communication with your AWS environment. You can provide a list of these IP Addresses in a TXT file. 

# Pricing
Amazon GuardDuty is priced along two dimensions. The dimensions are based on the quantity of AWS CloudTrail Events analyzed (per 1,000,000 events) and the volume of Amazon VPC Flow Log and DNS Log data analyzed (per GB). For more information, see [Amazon GuardDuty Pricing](https://aws.amazon.com/guardduty/pricing/).
