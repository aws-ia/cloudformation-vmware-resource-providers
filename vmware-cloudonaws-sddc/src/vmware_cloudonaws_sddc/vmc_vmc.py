import json
import requests

#In order to use the following function, all the functions in this file will have to be modified to use.  
def vmc_error_handling(fxn_response):
    code = fxn_response.status_code
    print (f'API call failed with status code {code}.')
    if code == 400:
        print(f'Error {code}: "Bad Request"')
        print("Request was improperly formatted or contained an invalid parameter.")
    elif code == 401:
        print(f'Error {code}: "The user is not authorized to use the API"')
        print("It's likely your refresh token is out of date or otherwise incorrect.")
    elif code == 403:
        print(f'Error {code}: "The user is forbidden to use the API"')
        print("The client does not have sufficient privileges to execute the request.")
        print("The API is likely in read-only mode, or a request was made to modify a read-only property.")
        print("It's likely your refresh token does not provide sufficient access.")
    elif code == 404:
        print(f'Error {code}: "Organization with this identifier is not found."')
        print("Please confirm the ORG ID and SDDC ID entries in your config.ini are correct.")
    elif code == 409:
        print(f'Error {code}: "The request could not be processed due to a conflict"')
        print("The request can not be performed because it conflicts with configuration on a different entity, or because another client modified the same entity.")
        print("If the conflict arose because of a conflict with a different entity, modify the conflicting configuration. If the problem is due to a concurrent update, re-fetch the resource, apply the desired update, and reissue the request.")
    elif code == 429:
        print(f'Error {code}: "The user has sent too many requests"')
    elif code == 500:
        print(f'Error {code}: "An unexpected error has occurred while processing the request"')
    elif code == 503:
        print(f'Error {code}: "Service Unavailable"')
        print("The request can not be performed because the associated resource could not be reached or is temporarily busy. Please confirm the ORG ID and SDDC ID entries in your config.ini are correct.")
    elif code == 504:
        print(f'Error {code}: "Gateway Error"')
        print("The request can not be performed because there is a problem with the network path. Check your VPN, etc.")
    else:
        print(f'Error: {code}: Unknown error')
    try:
        json_response = fxn_response.json()
        if 'message' in json_response:
            print(json_response['message'])
    except:
        print("No additional information in the error response.")
    return None

def get_sddcs_json(strProdURL, orgID, sessiontoken):
    """Returns list of all SDDCs in an Org via json"""
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = f"{strProdURL}/vmc/api/orgs/{orgID}/sddcs"
    print(myURL)
    response = requests.get(myURL, headers=myHeader)
    json_response = response.json()
    print(f"list response {response.status_code}")
    if response.status_code == 200:
        return json_response
    else:
        vmc_error_handling(response)

def get_sddc_info_json (strProdURL, orgID, sessiontoken, sddcID):
    """Returns SDDC info in JSON format. Returns None if error"""
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = f"{strProdURL}/vmc/api/orgs/{orgID}/sddcs/{sddcID}"
    print(myURL)
    response = requests.get(myURL, headers=myHeader)
    print(response.status_code)
    json_response = response.json()
    if response.status_code == 200:
        return json_response
    else:
        print("There was an error. Check the syntax.")
        print(f'API call failed with status code {response.status_code}. URL: {myURL}.')
        if 'error_messages' in json_response:
            print(json_response['error_messages'])
        return None        