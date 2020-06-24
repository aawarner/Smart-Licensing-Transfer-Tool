"""
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

Filename: SL-Pull-Token-Transfer-Licenses-Between-VAs.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
         Justin Poole (jupoole@cisco.com)

"""

import json
import os
import sys
import requests


def getSLToken(username, password):
    """Pull Oauth2.0 token for CSSM login function."""
    url = "https://cloudsso.cisco.com/as/token.oauth2"

    with open("creds.json", "r") as f:
        creds = json.load(f)
        client_id = creds["client_id"]
        client_secret = creds["client_secret"]

    payload = (
        "client_id={client_id}&client_secret={client_secret}&username={username}"
        "&password={password}&grant_type=password".format(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
    )
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "cache-control": "no-cache",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    code = response.status_code
    if code == 400:
        print(
            "Authentication failed. Check USERNAME/PASSWORD environment variables and"
            " client ID/Secret for accuracy."
        )
        sys.exit()
    token = response.json()
    token = token["access_token"]
    print(token)
    return token


def getAvailableLicenses(token, smart_account, transfer_from_va):
    """View licenses in Virtual Account function. Comment out in main(): if not needed."""
    url = (
        "https://apx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/"
        "{sa}/licenses".format(sa=smart_account)
    )

    payload = json.dumps(
        {"virtualAccounts": [transfer_from_va], "limit": 50, "offset": 0}
    )
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer {token}".format(token=token),
        "cache-control": "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    result = response.json()
    print(result)


def transferLicenses(
        token,
        smart_account,
        transfer_from_va,
        transfer_to_va,
        license,
        licenseType,
        quantity,
    ):
    """Transfer licenses between Virtual Accounts function"""

    url = (
        "https://apx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/"
        "{sa}/virtual-accounts/{va}/licenses/transfer".format(
            sa=smart_account, va=transfer_from_va
        )
    )

    payload = json.dumps(
        {
            "licenses": [
                {
                    "license": license,
                    "licenseType": licenseType,
                    "quantity": quantity,
                    "targetVirtualAccount": transfer_to_va,
                }
            ]
        }
    )
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer {token}".format(token=token),
        "cache-control": "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    result = response.json()
    print(result)
    error = result["status"]
    if error == "ERROR":
        return error


def main():
    """Main code function"""
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if not username:
        print(
            "USERNAME environment variable not set. Set environment variable USERNAME "
            "and try again "
        )
        sys.exit()
    if not password:
        print(
            "PASSWORD environment variable not set. Set environment variable PASSWORD"
            " and try again "
        )
        sys.exit()

    token = getSLToken(username, password)

    files = os.listdir()

    if "licenses.json" not in files:

        smart_account = input("Enter the Smart Account Domain ID: ")
        transfer_from_va = input(
            "Enter the Virtual Account name you want to transfer licenses from: "
        )
        transfer_to_va = input(
            "Enter the Virtual Account name you want to transfer licenses to: "
        )
        license = input("Enter the license you want to transfer: ")
        licenseType = input("Enter the license type PERPETUAL|TERM: ")
        quantity = int(input("Enter the number of licenses you want to transfer: "))
        data = [
            {
                "smart_account": smart_account,
                "transfer_from_va": transfer_from_va,
                "transfer_to_va": transfer_to_va,
                "license": license,
                "licenseType": licenseType,
                "quantity": quantity
            }
        ]
    else:
        with open("licenses.json", "r") as f:
            data = json.load(f)

    for i in data:
        smart_account = i["smart_account"]
        transfer_from_va = i["transfer_from_va"]
        transfer_to_va = i["transfer_to_va"]
        license = i["license"]
        licenseType = i["licenseType"]
        quantity = i["quantity"]


        # getAvailableLicenses(token, smart_account, transfer_from_va)

        if quantity <= 998:
            transferLicenses(
                token,
                smart_account,
                transfer_from_va,
                transfer_to_va,
                license,
                licenseType,
                quantity,
            )
        else:
            while quantity >= 0:
                if quantity > 998:
                    limit = 998
                    error = transferLicenses(
                        token,
                        smart_account,
                        transfer_from_va,
                        transfer_to_va,
                        license,
                        licenseType,
                        limit,
                    )
                    if error == "ERROR":
                        break
                else:
                    error = transferLicenses(
                        token,
                        smart_account,
                        transfer_from_va,
                        transfer_to_va,
                        license,
                        licenseType,
                        quantity,
                    )
                    if error == "ERROR":
                        break
                quantity -= 998


if __name__ == main():
    main()
