import ast
import json
from .vmc_auth import VMCAuth

# from vmc_auth import VMCAuth
import requests
import sys
from datetime import datetime, timezone
import time


def create_sddc_json_v2(
    authentication: VMCAuth,
    strProdURL: str,
    org_id: str,
    name: str,
    region: str,
    host_count: int,
    host_type: str,
    cidr_block: str,
    skip_creating_vxlan: bool = False,
    vxlan_subnet: str = None,
    provider_type="AWS",
    aws_account_id=None,
    link_subnet_id=None,
    sddc_size="medium",
):
    myHeader = {"csp-auth-token": authentication.access_token}
    if host_count == 1:
        call_data = {
            "type": "DEPLOY",
            "resource_type": "deployment",
            "config": {
                "provider_type": provider_type,
                "name": name,
                "sddc_type": "OneNode",
                "deployment_type": "SingleAZ",
                "type": "DeployVmcAwsSddcConfig",
                "skip_creating_vxlan": skip_creating_vxlan,
                "vxlan_subnet": vxlan_subnet,
                "host_count": host_count,
                "sddc_size": sddc_size,
                "location": {"name": region, "code": region},
                "host_type": host_type,
                "network_config": {"cidr_block": cidr_block},
            },
        }
    else:
        call_data = {
            "type": "DEPLOY",
            "resource_type": "deployment",
            "config": {
                "provider_type": provider_type,
                "name": name,
                "sddc_type": "Default",
                "deployment_type": "SingleAZ",
                "type": "DeployVmcAwsSddcConfig",
                "skip_creating_vxlan": skip_creating_vxlan,
                "vxlan_subnet": vxlan_subnet,
                "host_count": host_count,
                "sddc_size": sddc_size,
                "location": {"name": region, "code": region},
                "host_type": host_type,
                "account_link_config": {
                    "aws_account_id": aws_account_id,
                    "subnet_id": [link_subnet_id],
                },
                "network_config": {"cidr_block": cidr_block},
            },
        }

    my_url = f"{strProdURL}/api/inventory/{org_id}/vmc-aws/operations"
    print(f"Endpoint: {my_url}")
    print(json.dumps(call_data, indent=4))
    resp = requests.post(my_url, json=call_data, headers=myHeader, timeout=20)

    print(resp.status_code)

    if resp.status_code != 200:
        try:
            json_response = resp.json()
        except:
            json_response = None

    if resp.status_code == 201 or resp.status_code == 202 or resp.status_code == 202:
        print(f"Create SDDC Started. Creation Task is: ")  # pull the task and print it.
        newTask = json_response["id"]
        print(f"{newTask}")
        return json_response
    elif resp.status_code == 200:
        print("Create Task Complete: Input Validated")
        validated = "{'input_validated' : True}"
        return ast.literal_eval(validated)
    elif resp.status_code == 400:
        print(f"Error Code {resp.status_code}: Bad Request, Bad URL or Quota Violation")
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        return None
    elif resp.status_code == 401:
        print(
            f"Error Code {resp.status_code}: You are unauthorized for this operation. See your administrator"
        )
        if "error_messages" in json_response:
            print(json_response["error_messages"])
        return None
    elif resp.status_code == 403:
        print(
            f"Error Code {resp.status_code}: You are forbidden to use this operation. See your administrator"
        )
        if "error_messages" in json_response:
            print(json_response["error_messages"])
        return None
    else:
        print(
            f"Error {resp.status_code} returned by call to {my_url}, payload: {json.dumps(call_data,indent=4)}"
        )


def get_sddc_deployments_json(strProdURL, authentication: VMCAuth, orgid):
    myHeader = {"csp-auth-token": authentication.access_token}
    myURL = f"{strProdURL}/api/inventory/{orgid}/core/deployments?filter=type.code,in:vmc-aws&sort=creator.timestamp,desc&include_deleted_resources=true"
    response = requests.get(myURL, headers=myHeader, timeout=20)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_sddc_tasks_json(strProdURL, authentication: VMCAuth, orgid, sddcid, task_id):
    myHeader = {"csp-auth-token": authentication.access_token}
    # myURL = f"{strProdURL}/vmc/api/orgs/{orgid}/tasks?$filter=(resource_id eq {sddcid})"
    myURL = f"{strProdURL}/api/operation/{orgid}/core/operations/{task_id}"
    try:
        response = requests.get(myURL, headers=myHeader, timeout=20)
    except Exception as e:
        print(f"get_sddc_tasks_json error: {e}")
        return None

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_sddc_task_progress_json(
    strProdURL, authentication: VMCAuth, orgid, sddcid, task_id
):
    myHeader = {"csp-auth-token": authentication.access_token}
    myURL = f"{strProdURL}/vmc/api/orgs/{orgid}/tasks/{task_id}"
    try:
        response = requests.get(myURL, headers=myHeader, timeout=20)
    except Exception as e:
        print(f"get_sddc_task_progress_json: {e}")
        return None

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_sddc_task_details_json(
    strProdURL, authentication: VMCAuth, orgid, sddcid, task_id, retrieve_progress=False
) -> dict:
    task_info = {}
    json_response_task = get_sddc_tasks_json(
        strProdURL, authentication, orgid, sddcid, task_id
    )
    if json_response_task:
        task_info["state"] = json_response_task["state"]
        if retrieve_progress:
            if "provider_assigned_id" in json_response_task.keys():
                json_response_progress = get_sddc_task_progress_json(
                    strProdURL,
                    authentication,
                    orgid,
                    sddcid,
                    json_response_task["provider_assigned_id"],
                )
                if json_response_progress:
                    task_info["progress_percent"] = json_response_progress[
                        "progress_percent"
                    ]
                    task_info["estimated_remaining_minutes"] = json_response_progress[
                        "estimated_remaining_minutes"
                    ]

        # task_info["phase"] = json_response["state"]["phase"]
        # task_info["sub_phase"] = json_response["state"]["sub_phase"]
        return task_info
    else:
        print(f"No task details found for task ID {task_id}")
        return None


def check_task_status_v2(strProdURL, authentication: VMCAuth, orgId, sddcId, taskId):
    task_details = get_sddc_task_details_json(
        strProdURL, authentication, orgId, sddcId, taskId, retrieve_progress=True
    )

    if task_details is None:
        return "IN_PROGRESS"

    if "state" not in task_details:
        return "IN_PROGRESS"

    if "phase" not in task_details["state"]:
        return "IN_PROGRESS"

    phase = task_details["state"]["phase"]

    if phase == "FAILED" or phase == "READY":
        return phase
    else:
        return "IN_PROGRESS"


def wait_for_task_v2(strProdURL, authentication: VMCAuth, orgId, sddcId, task_id):
    MAX_RETRIEVAL_ATTEMPTS = 10
    SLEEP_TIME_SECONDS = 30

    task_details = get_sddc_task_details_json(
        strProdURL, authentication, orgId, sddcId, task_id, retrieve_progress=True
    )

    task_not_ready = True
    details_ctr = 0
    while task_not_ready and details_ctr < MAX_RETRIEVAL_ATTEMPTS:
        if task_details is None:
            task_not_ready = True
        elif "state" not in task_details:
            task_not_ready = True
        else:
            task_not_ready = False
            break

        details_ctr += 1
        print(
            f"Attempting to retrieve task ({details_ctr}/{MAX_RETRIEVAL_ATTEMPTS})..."
        )
        time.sleep(10)
        authentication.check_access_token_expiration()
        task_details = get_sddc_task_details_json(
            strProdURL, authentication, orgId, sddcId, task_id
        )
        print(task_details)

    if not task_details:
        print("Could not retrieve task details.")
    else:
        task_not_ready = True
        while task_not_ready:
            if "phase" not in task_details["state"]:
                print("Waiting for phase to become available...")
                task_not_ready = True
            else:
                task_not_ready = False

            time.sleep(10)

        phase = task_details["state"]["phase"]
        while phase != "READY" and phase != "FAILED":
            print(f"{datetime.now()} - {task_details}")
            authentication.check_access_token_expiration()
            task_details = get_sddc_task_details_json(
                strProdURL,
                authentication,
                orgId,
                sddcId,
                task_id,
                retrieve_progress=True,
            )
            if task_details is None:
                phase = "CHECK_FAILED"
            elif "state" not in task_details:
                phase = "STATE_NOT_FOUND"
            elif "phase" not in task_details["state"]:
                phase = "PHASE_NOT_FOUND"
            else:
                phase = task_details["state"]["phase"]

            print(f"Pausing for {SLEEP_TIME_SECONDS} seconds")
            time.sleep(SLEEP_TIME_SECONDS)

        print(f"SDDC ID: {sddcId}")


def delete_sddc_json(strProdURL, authentication: VMCAuth, orgID, sddcID, force):
    """Returns task for the delete process, or None if error"""
    myHeader = {"csp-auth-token": authentication.access_token}
    myURL = f"{strProdURL}/vmc/api/orgs/{orgID}/sddcs/{sddcID}/"
    if force:
        myURL = myURL + "?force=true"

    print(f"DELETE URL: {myURL}")
    response = requests.delete(myURL, headers=myHeader, timeout=20)
    json_response = response.json()
    print(response.status_code)
    print(json_response)
    if response.status_code == 202:
        print("Delete task created. Task ID:")
        newTask = json_response["id"]
        print(f"{newTask}")
        return json_response
    elif response.status_code == 400:
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        else:
            print("The SDDC is not in a state that is valid for deletion")
        return None
    elif response.status_code == 401:
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        else:
            print("Current user is unauthorized for this operation.")
        return None
    elif response.status_code == 403:
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
            print("Access not allowed to the operation for the current user")
        return None
    elif response.status_code == 404:
        print("Cannot find the SDDC with given identifier")
        return None
    else:
        print(f"Unexpected response: {response.status_code}")
        return None

################################################################################
### Copyright (C) 2019-2022 VMware, Inc.  All rights reserved.
### SPDX-License-Identifier: BSD-2-Clause
################################################################################
def watch_sddc_task_json(strProdURL, authentication: VMCAuth, orgID, taskid):
    myHeader = {"csp-auth-token": authentication.access_token}
    myURL = f"{strProdURL}/vmc/api/orgs/{orgID}/tasks/{taskid}"
    response = requests.get(myURL, headers=myHeader, timeout=20)
    print(f"URL: {myURL}, HEADER: {myHeader}, WATCH response: {response.status_code}")
    try:
        json_response = response.json()
    except Exception as e:
        print(f"JSON error: {e}")
        return None

    if response.status_code == 200:
        # do the right thing
        return json_response
    elif response.status_code == 401:
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        else:
            print("User is unauthorized for current operation")
        return None
    elif response.status_code == 403:
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        else:
            print("User is forbidden from current action")
        return None
    elif response.status_code == 404:
        print("Cannot find the task with given identifier")
        if "error_messages" in json_response:
            print(json_response["error_messages"][0])
        return None
    else:
        print("Unexpected error")
        return None
    return None

################################################################################
### Copyright (C) 2019-2022 VMware, Inc.  All rights reserved.
### SPDX-License-Identifier: BSD-2-Clause
################################################################################
def printTask(event_name: str, task) -> None:
    taskid = task["id"]
    print(f"{event_name} Task Started: {taskid}")
    print(f'Created: {task["created"]}')
    print(f'Updated: {task["updated"]}')
    print(f'Updated by User ID: {task["updated_by_user_id"]}')
    print(f'User ID: {task["user_id"]}')
    print(f'User Name: {task["user_name"]}')
    print(f'Version: {task["version"]}')
    print(f'Updated by User Name: {task["updated_by_user_name"]}')
    print(f'Progress: {task["progress_percent"]}%')
    print(f'Minutes remaining: {task["estimated_remaining_minutes"]}')
    #
    # Now the inline parts:
    #
    print(f"Status: {task['status']}")
    print(f"Sub-Status: {task['sub_status']}")
    print(f"Resource: {task['resource_type']}")
    print(f"Resource ID: {task['resource_id']}")
    print(f"Task Type: {task['task_type']}")
    print(f"Error Message: {task['error_message']}")

    return

################################################################################
### Copyright (C) 2019-2022 VMware, Inc.  All rights reserved.
### SPDX-License-Identifier: BSD-2-Clause
################################################################################
def watchSDDCTask(**kwargs):
    """watch task and print out status"""
    strProdURL = kwargs["strProdURL"]
    orgID = kwargs["ORG_ID"]
    authentication = kwargs["authentication"]
    taskID = kwargs["taskID"]

    status = "STARTED"
    while status != "FINISHED" and status != "FAILED" and status != "CANCELED":
        json_response = watch_sddc_task_json(strProdURL, authentication, orgID, taskID)
        status = json_response["status"]
        if json_response == None:
            sys.exit(1)
        # else, print out the task
        task = json_response["id"]
        now_utc = datetime.now(timezone.utc)
        print(
            f'Information on Task {task} @ {now_utc.isoformat().replace("+00:00", "Z")}'
        )
        printTask("Watch Task", json_response)
        print("")
        time.sleep(5)
        authentication.check_access_token_expiration()

    return None
