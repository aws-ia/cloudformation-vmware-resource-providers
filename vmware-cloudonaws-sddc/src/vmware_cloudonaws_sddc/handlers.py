import logging
import json
import argparse
import requests;
from datetime import datetime, timezone;
import time;
import sys
from typing import Any, MutableMapping, Optional
from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
    identifier_utils,
)

from .models import ResourceHandlerRequest, ResourceModel
from .vmc_auth import VMCAuth
from .vmc_csp import *
#from .vmc.vmc_auth import VMCAuth
#from .vmc.vmc_csp import *

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

#LOG.setLevel(logging.CRITICAL)
LOG.setLevel(logging.DEBUG)

TYPE_NAME = "VMware::CloudOnAWS::SDDC"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint

CALLBACK_DELAY_SECONDS = 5

# Define a context for the callback logic.  The value for the 'status'
# key in the dictionary below is consumed in is_callback() and in
# _callback_helper(), that are invoked from a given handler.
CALLBACK_STATUS_IN_PROGRESS = {
    "status": OperationStatus.IN_PROGRESS,
}

@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    # TODO: put code here

    if _is_callback(
        callback_context,
    ):
        return _callback_helper(
            session,
            request,
            callback_context,
            model,
        )
    
    try:
        LOG.debug('Attempting create_sddc_json_v2')
        authentication = VMCAuth(model.CSPProdURL)
        authentication.getAccessToken(model.AccessToken)    
        if authentication.access_token is None:
            LOG.debug(f"VMCAuth failed. Model: {model}")
            return ProgressEvent.failed(HandlerErrorCode.InvalidCredentials, "Authentication to VMC was unsuccessful, unable to continue.", None)
        validate_only = False
        json_response = create_sddc_json_v2(authentication, model.ProdURL,model.OrgID, model.Name, model.Region, model.NumHosts, model.HostType, model.ManagementSubnet, validate_only,model.VXLANSubnet,model.Provider,model.AWSAccountID,model.AWSSubnetID)
        print(json.dumps(json_response, indent=4))
        if json_response is not None:
            sddcId = json_response['resource_id']
            task_id = json_response["id"]
            model.ID = sddcId
            model.TaskID = task_id
            LOG.debug(f"Model name and subnet: {model.Name}, {model.ManagementSubnet}")

            #wait_for_task_v2(strProdUrl, authentication, orgId, sddcId, task_id)
            task_complete = check_task_status_v2(model.ProdURL,authentication,model.OrgID,sddcId,task_id)

            return _progress_event_callback(model=model,)

        else:
            LOG.debug("json_response is None from create_sddc_json_v2()")
            return ProgressEvent.failed(HandlerErrorCode.InvalidRequest, "No response from create_sddc_json_v2()", None)
            
    except Exception as e:
        # exceptions module lets CloudFormation know the type of failure that occurred
        LOG.debug(f"Exception: {e}")
        return ProgressEvent.failed(HandlerErrorCode.InternalFailure, e, None)



@resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    # TODO: put code here
    
    return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=model,
            )


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=None,
    )
    
    LOG.debug("delete_handler(), trying to print model:")
    LOG.debug(model)
    authentication = VMCAuth(model.CSPProdURL)
    authentication.getAccessToken(model.AccessToken)
    if authentication.access_token is None:
        LOG.debug(f"VMCAuth failed. Model: {model}")
        return ProgressEvent.failed(HandlerErrorCode.InvalidCredentials, "Authentication to VMC was unsuccessful, unable to continue.", None)    
    if model:
        if model.ID:
            print(f'SDDC ID to Delete: [{model.ID}]')
            json_response = delete_sddc_json(model.ProdURL, authentication,model.OrgID,model.ID, False)
            if json_response:
                print(json_response)
        else:
            LOG.debug('SDDC ID to Delete: [NOT FOUND] - returning FAILED status')
            return ProgressEvent(
                status=OperationStatus.FAILED,
            )
    else:
        LOG.debug('delete_handler() - model is None - returning FAILED status ')
        return ProgressEvent(
                status=OperationStatus.FAILED,
            )
    
    return ProgressEvent(
            status=OperationStatus.SUCCESS,
            )


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    LOG.debug("read_handler(), attempting to print model:")
    print(model)

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )



@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    # TODO: put code here
    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModels=[],
    )


def _progress_event_callback(
    model: Optional[ResourceModel],
) -> ProgressEvent:
    """Return a ProgressEvent indicating a callback should occur next."""
    LOG.debug("_progress_event_callback()")

    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
        callbackContext=CALLBACK_STATUS_IN_PROGRESS,
        callbackDelaySeconds=CALLBACK_DELAY_SECONDS,
    )

def _is_callback(
    callback_context: MutableMapping[str, Any],
) -> bool:
    """Logic to determine whether or not a handler invocation is new."""
    LOG.debug("_is_callback()")

    # If there is a callback context status set, then assume this is a
    # handler invocation (e.g., Create handler) for a previous request
    # that is still in progress.
    if callback_context.get("status") == CALLBACK_STATUS_IN_PROGRESS["status"]:
        LOG.debug("_is_callback() = True")
        return True
    else:
        LOG.debug("_is_callback() = False")
        return False
    
def _progress_event_success(
    model: Optional[ResourceModel] = None
) -> ProgressEvent:
    LOG.debug("_progress_event_success()")
    LOG.debug(model)

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )

def _progress_event_failed(
    handler_error_code: HandlerErrorCode,
    error_message: str,
    traceback_content: Any = None,
) -> ProgressEvent:
    LOG.debug("_progress_event_failed()")

    return ProgressEvent.failed("400", "SDDC deployment failed")

def _callback_helper(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
    model: Optional[ResourceModel],
    is_delete_handler: bool = False,
) -> ProgressEvent:
    """Define a callback logic used for resource stabilization."""
    LOG.debug("_callback_helper()")

    authentication = VMCAuth(model.CSPProdURL)
    authentication.getAccessToken(model.AccessToken)
    task_complete = check_task_status_v2(model.ProdURL,authentication,model.OrgID,model.ID,model.TaskID)
    if task_complete == "READY":
        LOG.debug("About to return _progress_event_success")
        LOG.debug(model)
        return _progress_event_success(
            model=model,
        )
    if task_complete == "FAILED":
        return _progress_event_failed
    
    return _progress_event_callback(
        model=model
    )