"""
Copyright Amazon.com, Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
"""
import logging
import json
import argparse
import requests
from datetime import datetime, timezone
import time
import sys
import traceback
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)
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
from .vmc_vmc import *

# from .vmc.vmc_auth import VMCAuth
# from .vmc.vmc_csp import *

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

LOG.setLevel(logging.WARNING)
#LOG.setLevel(logging.DEBUG)

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
        LOG.debug("Attempting create_sddc_json_v2")
        authentication = VMCAuth(model.CSPProdURL)
        authentication.getAccessToken(model.AccessToken)
        if authentication.access_token is None:
            LOG.debug(f"VMCAuth failed. Model: {model}")
            return ProgressEvent.failed(
                HandlerErrorCode.InvalidCredentials,
                "Authentication to VMC was unsuccessful, unable to continue.",
                None,
            )
        validate_only = False
        json_response = create_sddc_json_v2(
            authentication,
            model.ProdURL,
            model.OrgID,
            model.Name,
            model.Region,
            model.NumHosts,
            model.HostType,
            model.ManagementSubnet,
            validate_only,
            model.VXLANSubnet,
            model.Provider,
            model.ConnectedAWSAccountID,
            model.ConnectedAWSSubnetID,
        )
        print(json.dumps(json_response, indent=4))
        if json_response is not None:
            sddcId = json_response["resource_id"]
            task_id = json_response["id"]
            model.ID = sddcId
            model.TaskID = task_id
            LOG.debug(f"Model name and subnet: {model.Name}, {model.ManagementSubnet}")

            # wait_for_task_v2(strProdUrl, authentication, orgId, sddcId, task_id)
            task_complete = check_task_status_v2(
                model.ProdURL, authentication, model.OrgID, sddcId, task_id
            )

            return _progress_event_callback(
                model=model,
            )

        else:
            LOG.debug("json_response is None from create_sddc_json_v2()")
            return ProgressEvent.failed(
                HandlerErrorCode.InvalidRequest,
                "No response from create_sddc_json_v2()",
                None,
            )

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
    LOG.debug(f"update_handler(), attempting to print model: {model}")

    LOG.debug(f"Progress status: {progress.status}")

    if _is_callback(
        callback_context,
    ):
        return _callback_helper(
            session, request, callback_context, model, is_update_handler=True
        )
    else:
        LOG.debug("No callback context present")

    sddc = None
    try:
        if model and model.ID:
            authentication = VMCAuth(model.CSPProdURL)
            authentication.getAccessToken(model.AccessToken)
            LOG.debug("About to invoke get_sddc_info_json()")
            sddc = get_sddc_info_json(
                model.ProdURL, model.OrgID, authentication.access_token, model.ID
            )
            if sddc is None:
                return _progress_event_failed(
                    handler_error_code=HandlerErrorCode.NotFound,
                    error_message="update_handler: Could not retrieve SDDC",
                )
            else:
                LOG.debug(f"SDDC State: {sddc['sddc_state']}")
                # SDDCs are never actually deleted, just hidden from the CSP UI. They can be found via API
                # If the SDDC is found, but in a state of 'DELETED', return the Not Found error code
                if sddc["sddc_state"] == "DELETED":
                    return _progress_event_failed(
                        handler_error_code=HandlerErrorCode.NotFound,
                        error_message="update_handler: SDDC was found, but in deleted state",
                    )
        else:
            return _progress_event_failed(
                handler_error_code=HandlerErrorCode.NotFound,
                error_message="update_handler: no model ID was found",
            )

    except Exception as e:
        LOG.debug(f"Exception {e}")
        return _progress_event_failed(
            handler_error_code=HandlerErrorCode.NotFound,
            error_message=str(e),
            traceback_content=traceback.format_exc(),
        )

    try:
        success = _update_sddc_helper(
            authentication=authentication, model=model, request=request, sddc=sddc
        )
        print(f"Update sddc helper succeeded? {success}")
        if not success:
            return _progress_event_failed(
                handler_error_code=HandlerErrorCode.InternalFailure,
                error_message="Failed to update SDDC",
            )

    except Exception as e:
        return _progress_event_failed(
            handler_error_code=HandlerErrorCode.InternalFailure,
            error_message=str(e),
            traceback_content=traceback.format_exc(),
        )

    return _progress_event_success(
        model=model,
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

    if _is_callback(
        callback_context,
    ):
        return _callback_helper(
            session, request, callback_context, model, is_delete_handler=True
        )

    authentication = VMCAuth(model.CSPProdURL)
    authentication.getAccessToken(model.AccessToken)
    if authentication.access_token is None:
        LOG.debug(f"VMCAuth failed. Model: {model}")
        return ProgressEvent.failed(
            HandlerErrorCode.InvalidCredentials,
            "Authentication to VMC was unsuccessful, unable to continue.",
            None,
        )
    if model:
        if model.ID:
            print(f"SDDC ID to Delete: [{model.ID}]")
            json_response = delete_sddc_json(
                model.ProdURL, authentication, model.OrgID, model.ID, False
            )
            if json_response:
                id = json_response["id"]
                LOG.debug(f"Delete task ID: {id}")
                model.DeleteTaskID = id

                return _progress_event_callback(
                    model=model,
                )

            else:
                LOG.debug("No id found in response from delete_sddc_json()")
                LOG.debug(f"json: {json_response}")
                return ProgressEvent.failed(
                    HandlerErrorCode.NotFound,
                    "No id found in response from delete_sddc_json()",
                    None,
                )

        else:
            LOG.debug("SDDC ID to Delete: [NOT FOUND] - returning FAILED status")
            return ProgressEvent.failed(
                HandlerErrorCode.NotFound, "SDDC ID was not found", None
            )
    else:
        LOG.debug("delete_handler() - model is None - returning FAILED status ")
        return ProgressEvent.failed(HandlerErrorCode.NotFound, "model is None", None)


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )

    LOG.debug(f"read_handler(), attempting to print model: {model}")

    LOG.debug(f"Progress status: {progress.status}")

    try:
        if model and model.ID:
            authentication = VMCAuth(model.CSPProdURL)
            authentication.getAccessToken(model.AccessToken)
            LOG.debug("About to invoke get_sddc_info_json()")
            sddc = get_sddc_info_json(
                model.ProdURL, model.OrgID, authentication.access_token, model.ID
            )
            if sddc is None:
                return _progress_event_failed(
                    handler_error_code=HandlerErrorCode.NotFound,
                    error_message="read_handler: Could not retrieve SDDC",
                )
            else:
                LOG.debug(f"SDDC State: {sddc['sddc_state']}")
                # SDDCs are never actually deleted, just hidden from the CSP UI. They can be found via API
                # If the SDDC is found, but in a state of 'DELETED', return the Not Found error code
                if sddc["sddc_state"] == "DELETED":
                    return _progress_event_failed(
                        handler_error_code=HandlerErrorCode.NotFound,
                        error_message="read_handler: SDDC was found, but in deleted state",
                    )
        else:
            return _progress_event_failed(
                handler_error_code=HandlerErrorCode.NotFound,
                error_message="read_handler: no model ID was found",
            )

    except Exception as e:
        LOG.debug(f"Exception {e}")
        return _progress_event_failed(
            handler_error_code=HandlerErrorCode.NotFound,
            error_message=str(e),
            traceback_content=traceback.format_exc(),
        )

    return _progress_event_success(
        model=model,
    )


@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=None,
    )

    LOG.debug(f"list_handler progress status: {progress.status}")

    try:
        resource_model_list = []
        model = request.desiredResourceState
        LOG.debug(f"model: {model}")
        resource_model_list = _get_resource_model_list(model)
        LOG.debug(f"model list: {resource_model_list}")

    except Exception as e:
        return _progress_event_failed(
            handler_error_code=HandlerErrorCode.InternalFailure,
            error_message=str(e),
            traceback_content=traceback.format_exc(),
        )

    return _progress_event_success(
        models=resource_model_list,
        is_list_handler=True,
    )


def _get_resource_model_list(
    model: ResourceModel,
) -> List[ResourceModel]:
    LOG.debug("_get_resource_model_list()")
    resource_model_list = []

    authentication = VMCAuth(model.CSPProdURL)
    authentication.getAccessToken(model.AccessToken)
    LOG.debug(f"_get_resource_model_list token: {authentication.access_token}")
    LOG.debug(f"_get_resource_model_list model: {model}")
    sddc_list = get_sddcs_json(model.ProdURL, model.OrgID, authentication.access_token)

    LOG.debug(f"sddc_list size: {len(sddc_list)}")
    for sddc in sddc_list:
        LOG.debug(f"SDDC Name: {sddc['name']}, SDDC ID: {sddc['id']}")
        try:
            resource_model_list_item = ResourceModel(
                AccessToken=model.AccessToken,
                ID=sddc["id"],
                Name=sddc["name"],
                OrgID=sddc["org_id"],
                DeploymentType=None,
                ManagementSubnet=sddc["resource_config"]["vpc_info"]["vpc_cidr"],
                VXLANSubnet=None,
                Region=sddc["resource_config"]["region"],
                HostType=None,
                NumHosts=None,
                Provider=sddc["provider"],
                ConnectedAWSAccountID=None,
                ConnectedAWSSubnetID=None,
                ConnectedAWSVPC=None,
                ProdURL=model.ProdURL,
                CSPProdURL=model.CSPProdURL,
                TaskID=None,
                DeleteTaskID=None,
                vCenterURL=sddc["resource_config"]["vc_url"],
                NSXPublicURL=sddc["resource_config"]["nsx_reverse_proxy_url"],
            )
        except Exception as e:
            LOG.debug(f"Cannot create ResourceModel object: Exception: {e}")
            return ProgressEvent.failed(HandlerErrorCode.InternalFailure, e, None)

        resource_model_list.append(resource_model_list_item)

    LOG.debug(f"resource model list: {resource_model_list}")
    return resource_model_list


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
    model: Optional[ResourceModel] = None,
    models: Any = None,
    is_delete_handler: bool = False,
    is_list_handler: bool = False,
) -> ProgressEvent:
    LOG.debug("_progress_event_success()")
    LOG.debug(model)

    if not model and not models and not is_delete_handler and not is_list_handler:
        raise ValueError(
            "Model, or models, or is_delete_handler, or is_list_handler unset",
        )

    elif is_delete_handler and is_list_handler:
        raise ValueError(
            "Specify either is_delete_handler or is_list_handler, not both",
        )

    elif is_delete_handler:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
        )
    elif is_list_handler:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModels=models,
        )
    else:
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

    return ProgressEvent.failed(handler_error_code, error_message)


def _update_sddc_helper(
    authentication: VMCAuth,
    model: ResourceModel,
    request: ResourceHandlerRequest,
    sddc: str,
) -> bool:
    LOG.debug(
        f"_update_sddc_helper(): Requested name: {model.Name}, SDDC current name: {sddc['name']}"
    )

    myHeader = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "csp-auth-token": authentication.access_token,
    }
    myURL = (
        model.ProdURL
        + "/vmc/api/orgs/"
        + model.OrgID
        + "/sddcs/"
        + sddc["resource_config"]["sddc_id"]
    )
    LOG.debug(f"API URL: {myURL}")

    payload = {"name": model.Name}

    json_data = json.dumps(payload)
    response = requests.patch(myURL, headers=myHeader, data=json_data, timeout=20)
    if response.status_code == 200:
        return True
    else:
        LOG.debug(
            f"Could not update SDDC. Response status code: {response.status_code}. Response message: {response.text}. Payload: {json_data}"
        )
        return False


def _callback_helper(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
    model: Optional[ResourceModel],
    is_delete_handler: bool = False,
    is_update_handler: bool = False,
) -> ProgressEvent:
    """Define a callback logic used for resource stabilization."""
    LOG.debug("_callback_helper()")

    authentication = VMCAuth(model.CSPProdURL)
    authentication.getAccessToken(model.AccessToken)
    if is_delete_handler:
        LOG.debug(
            f"delete_handler: OrgID: {model.OrgID}, DeleteTaskID: {model.DeleteTaskID}"
        )
        json_response = watch_sddc_task_json(
            model.ProdURL, authentication, model.OrgID, model.DeleteTaskID
        )
        if json_response:
            task_complete = json_response["status"]
            LOG.debug(f"Delete task status: {task_complete}")
            if task_complete == "FINISHED":
                LOG.debug("About to return _progress_event_success for DELETE")
                LOG.debug(model)
                return _progress_event_success(is_delete_handler=True)

            if task_complete == "FAILED" or task_complete == "CANCELED":
                return _progress_event_failed(
                    handler_error_code=HandlerErrorCode.NotFound,
                    error_message="callback helper: Task status failed or canceled",
                )

        return _progress_event_callback(model=model)

    elif is_update_handler:
        LOG.debug("_callback_helper(): UPDATE handler")
        return _progress_event_success(
            model=model,
        )
    else:
        task_complete = check_task_status_v2(
            model.ProdURL, authentication, model.OrgID, model.ID, model.TaskID
        )
        if task_complete == "READY":
            LOG.debug("About to return _progress_event_success ")
            LOG.debug(model)
            return _progress_event_success(
                model=model,
            )

        if task_complete == "FAILED":
            return _progress_event_failed(
                handler_error_code=HandlerErrorCode.InternalFailure,
                error_message="_callback_helper: Task is a status of failed",
            )

        return _progress_event_callback(model=model)
