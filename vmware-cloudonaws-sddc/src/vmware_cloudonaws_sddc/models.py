# DO NOT modify this file by hand, changes will be overwritten
from dataclasses import dataclass

from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
)
from cloudformation_cli_python_lib.recast import recast_object
from cloudformation_cli_python_lib.utils import deserialize_list

import sys
from inspect import getmembers, isclass
from typing import (
    AbstractSet,
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

T = TypeVar("T")


def set_or_none(value: Optional[Sequence[T]]) -> Optional[AbstractSet[T]]:
    if value:
        return set(value)
    return None


@dataclass
class ResourceHandlerRequest(BaseResourceHandlerRequest):
    # pylint: disable=invalid-name
    desiredResourceState: Optional["ResourceModel"]
    previousResourceState: Optional["ResourceModel"]
    typeConfiguration: Optional["TypeConfigurationModel"]


@dataclass
class ResourceModel(BaseModel):
    AccessToken: Optional[str]
    Name: Optional[str]
    Region: Optional[str]
    DeploymentType: Optional[str]
    HostType: Optional[str]
    NumHosts: Optional[int]
    Provider: Optional[str]
    ConnectedAWSAccountID: Optional[str]
    ConnectedAWSVPC: Optional[str]
    ConnectedAWSSubnet: Optional[str]
    ManagementSubnet: Optional[str]
    VXLANSubnet: Optional[str]
    ID: Optional[str]
    OrgID: Optional[str]
    AWSAccountID: Optional[str]
    AWSSubnetID: Optional[str]
    ProdURL: Optional[str]
    CSPProdURL: Optional[str]
    TaskID: Optional[str]
    vCenterURL: Optional[str]
    NSXPublicURL: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_ResourceModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_ResourceModel"]:
        if not json_data:
            return None
        dataclasses = {n: o for n, o in getmembers(sys.modules[__name__]) if isclass(o)}
        recast_object(cls, json_data, dataclasses)
        return cls(
            AccessToken=json_data.get("AccessToken"),
            Name=json_data.get("Name"),
            Region=json_data.get("Region"),
            DeploymentType=json_data.get("DeploymentType"),
            HostType=json_data.get("HostType"),
            NumHosts=json_data.get("NumHosts"),
            Provider=json_data.get("Provider"),
            ConnectedAWSAccountID=json_data.get("ConnectedAWSAccountID"),
            ConnectedAWSVPC=json_data.get("ConnectedAWSVPC"),
            ConnectedAWSSubnet=json_data.get("ConnectedAWSSubnet"),
            ManagementSubnet=json_data.get("ManagementSubnet"),
            VXLANSubnet=json_data.get("VXLANSubnet"),
            ID=json_data.get("ID"),
            OrgID=json_data.get("OrgID"),
            AWSAccountID=json_data.get("AWSAccountID"),
            AWSSubnetID=json_data.get("AWSSubnetID"),
            ProdURL=json_data.get("ProdURL"),
            CSPProdURL=json_data.get("CSPProdURL"),
            TaskID=json_data.get("TaskID"),
            vCenterURL=json_data.get("vCenterURL"),
            NSXPublicURL=json_data.get("NSXPublicURL"),
        )


# work around possible type aliasing issues when variable has same name as a model
_ResourceModel = ResourceModel


@dataclass
class TypeConfigurationModel(BaseModel):

    @classmethod
    def _deserialize(
        cls: Type["_TypeConfigurationModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_TypeConfigurationModel"]:
        if not json_data:
            return None
        return cls(
        )


# work around possible type aliasing issues when variable has same name as a model
_TypeConfigurationModel = TypeConfigurationModel


