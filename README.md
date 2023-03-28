> Note: This module is in alpha state and is likely to contain bugs and updates may introduce breaking changes. It is not recommended for production use at this time.

# VMware::CloudOnAWS::SDDC

This resource type manages a VMware Cloud on AWS [Software Defined Data Centre (SDDC)][1]

## Prerequisites

* [AWS Account][2]
* [AWS CLI][3]
* [VMware Cloud Organization][4] and [Access Token][5]

## AWS Management Console

To get started:

1. Sign in to the [AWS Management Console][6] with your account and navigate to CloudFormation.

1. Select "Public extensions" from the left hand pane and filter Publisher by "Third Party".

1. Use the search bar to filter by the "VMware" prefix.

    Note: All official VMware Cloud on AWS resources begin with `VMware::CloudOnAWS` and specify that they are `Published by AWS Community`.

1. Select the desired resource name to view more information about its schema, and click **Activate**.

1. On the **Extension details** page, specify:

    * Extension name
    * Execution role ARN
    * Automatic updates for minor version releases

1. After activating the extension, you can now [create your AWS stack][7] that includes any of the activated VMware Cloud resources.

For more information about available commands and workflows, see the official [AWS documentation][8].

## Supported regions

VMware Cloud on AWS CloudFormation resources are available on the CloudFormation Public Registry in the following regions:

| Code            | Name                      |
|-----------------|---------------------------|
| us-east-1       | US East (N. Virginia)     |
| us-east-2       | US East (Ohio)            |
| us-west-1       | US West (N. California)   |
| us-west-2       | US West (Oregon)          |
| ap-south-1      | Asia Pacific (Mumbai)     |
| ap-northeast-1  | Asia Pacific (Tokyo)      |
| ap-northeast-2  | Asia Pacific (Seoul)      |
| ap-southeast-1  | Asia Pacific (Singapore)  |
| ap-southeast-2  | Asia Pacific (Sydney)     |
| ca-central-1    | Canada (Central)          |
| eu-central-1    | Europe (Frankfurt)        |
| eu-west-1       | Europe (Ireland)          |
| eu-west-2       | Europe (London)           |
| eu-west-3       | Europe (Paris)            |
| eu-north-1      | Europe (Stockholm)        |
| sa-east-1       | South America (São Paulo) |

**Note**: To privately register a resource in any other region, use the provided packages.

## Syntax and Properties Reference

For more details on how to structure a CloudFormation template that makes use of the VMware Cloud on AWS SDDC resource type, and the available properties, click [here][9].

## Examples

### Create an SDDC

First, add the VMware Cloud Access Token and Org ID as secrets in AWS Secrets Manager.

```Bash
aws secretsmanager create-secret \
  --region us-west-2 \
  --name MyVMCOrg \
  --secret-string '{"AccessToken":"INSERTACCESSTOKEN","OrgID":"INSERTORGID"}'
```

Then use the following Cloudformation Template to create an SDDC:

```yaml
---
AWSTemplateFormatVersion: '2010-09-09'
Description: Creates a VMware Cloud on AWS SDDC
Resources:
  MySDDC:
    Type: VMware::CloudOnAWS::SDDC
    Properties:
        AccessToken: '{{resolve:secretsmanager:MyVMCOrg:SecretString:AccessToken}}'
        OrgID: '{{resolve:secretsmanager:MyVMCOrg:SecretString:OrgID}}'
        Name: mySDDC
        ManagementSubnet: 10.2.0.0/23
        VXLANSubnet: 172.16.0.0/24   
        Region: us-east-1
        HostType: i3.metal
        NumHosts: 1
        Provider: AWS
        ProdURL: https://vmc.vmware.com
        CSPProdURL: https://console.cloud.vmware.com
        ConnectedAWSAccountID: a134c59b-42e7-25ce-ebc4-425449c2ea2a
        ConnectedAWSSubnetID: subnet-01ab23c4de56f78e
```

[1]: https://vmc.techzone.vmware.com/vmc-arch/docs/introduction/vmc-aws-a-technical-overview#sec377-sub5
[2]: https://aws.amazon.com/account/
[3]: https://aws.amazon.com/cli/
[4]: https://docs.vmware.com/en/VMware-Cloud-services/services/Using-VMware-Cloud-Services/GUID-B1E70315-D91E-4618-86C8-3ED7A3AD2E19.html
[5]: https://docs.vmware.com/en/VMware-Cloud-services/services/Using-VMware-Cloud-Services/GUID-E2A3B1C1-E9AD-4B00-A6B6-88D31FCDDF7C.html
[6]: https://aws.amazon.com/console/
[7]: https://console.aws.amazon.com/cloudformation/home
[8]: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html
[9]: ./docs/README.md
