# VMware::CloudOnAWS::SDDC

Manage a VMware Cloud on AWS SDDC

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "VMware::CloudOnAWS::SDDC",
    "Properties" : {
        "<a href="#accesstoken" title="AccessToken">AccessToken</a>" : <i>String</i>,
        "<a href="#name" title="Name">Name</a>" : <i>String</i>,
        "<a href="#region" title="Region">Region</a>" : <i>String</i>,
        "<a href="#deploymenttype" title="DeploymentType">DeploymentType</a>" : <i>String</i>,
        "<a href="#hosttype" title="HostType">HostType</a>" : <i>String</i>,
        "<a href="#numhosts" title="NumHosts">NumHosts</a>" : <i>Integer</i>,
        "<a href="#provider" title="Provider">Provider</a>" : <i>String</i>,
        "<a href="#connectedawsaccountid" title="ConnectedAWSAccountID">ConnectedAWSAccountID</a>" : <i>String</i>,
        "<a href="#connectedawsvpc" title="ConnectedAWSVPC">ConnectedAWSVPC</a>" : <i>String</i>,
        "<a href="#connectedawssubnetid" title="ConnectedAWSSubnetID">ConnectedAWSSubnetID</a>" : <i>String</i>,
        "<a href="#managementsubnet" title="ManagementSubnet">ManagementSubnet</a>" : <i>String</i>,
        "<a href="#vxlansubnet" title="VXLANSubnet">VXLANSubnet</a>" : <i>String</i>,
        "<a href="#orgid" title="OrgID">OrgID</a>" : <i>String</i>,
        "<a href="#produrl" title="ProdURL">ProdURL</a>" : <i>String</i>,
        "<a href="#cspprodurl" title="CSPProdURL">CSPProdURL</a>" : <i>String</i>,
    }
}
</pre>

### YAML

<pre>
Type: VMware::CloudOnAWS::SDDC
Properties:
    <a href="#accesstoken" title="AccessToken">AccessToken</a>: <i>String</i>
    <a href="#name" title="Name">Name</a>: <i>String</i>
    <a href="#region" title="Region">Region</a>: <i>String</i>
    <a href="#deploymenttype" title="DeploymentType">DeploymentType</a>: <i>String</i>
    <a href="#hosttype" title="HostType">HostType</a>: <i>String</i>
    <a href="#numhosts" title="NumHosts">NumHosts</a>: <i>Integer</i>
    <a href="#provider" title="Provider">Provider</a>: <i>String</i>
    <a href="#connectedawsaccountid" title="ConnectedAWSAccountID">ConnectedAWSAccountID</a>: <i>String</i>
    <a href="#connectedawsvpc" title="ConnectedAWSVPC">ConnectedAWSVPC</a>: <i>String</i>
    <a href="#connectedawssubnetid" title="ConnectedAWSSubnetID">ConnectedAWSSubnetID</a>: <i>String</i>
    <a href="#managementsubnet" title="ManagementSubnet">ManagementSubnet</a>: <i>String</i>
    <a href="#vxlansubnet" title="VXLANSubnet">VXLANSubnet</a>: <i>String</i>
    <a href="#orgid" title="OrgID">OrgID</a>: <i>String</i>
    <a href="#produrl" title="ProdURL">ProdURL</a>: <i>String</i>
    <a href="#cspprodurl" title="CSPProdURL">CSPProdURL</a>: <i>String</i>
</pre>

## Properties

#### AccessToken

VMware CSP Access Token

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Name

Name of the SDDC

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Region

AWS Region where the SDDC will be deployed

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### DeploymentType

SDDC Deployment Type - Single, multi or stretched

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### HostType

i3.metal, i3en.metal, i4i.metal

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### NumHosts

Number of hosts to deploy

_Required_: Yes

_Type_: Integer

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Provider

AWS,ZEROCLOUD

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### ConnectedAWSAccountID

AWS Account ID which will be connected to the SDDC

_Required_: No

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### ConnectedAWSVPC

VPC ID which will be connected to the SDDC

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### ConnectedAWSSubnetID

Subnet ID which will be connected to the SDDC

_Required_: No

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### ManagementSubnet

CIDR Block which will be used for SDDC Management

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### VXLANSubnet

CIDR block assigned to the default segment

_Required_: No

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### OrgID

Organization ID

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### ProdURL

Production URL for VMware Cloud on AWS i.e. https://vmc.vmware.com

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### CSPProdURL

Production URL for the VMware Cloud Console i.e. https://console.cloud.vmware.com

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the ID.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### ID

SDDC ID

#### TaskID

Provisioning Task ID

#### DeleteTaskID

Delete Task ID

#### vCenterURL

vCenter URL

#### NSXPublicURL

NSX Public URL

