#!/usr/bin/python
from __future__ import print_function
import socket
import json
import sys
import os
import requests
import base64
import time
from testutils import TestUtils


def main(args):

    if len(args) < 2:
        print("Please provide environment, then retry.\nExiting...")
        sys.exit(0)

    utilsObj = TestUtils()

    chronos_url = args[(len(args) - 1)]
    chronos_common_access_url = [chronos_url,
                                 chronos_url + '/scheduler/jobs',
                                 chronos_url + '/scheduler/graph/csv']

    headers = utilsObj.get_authorization_header()

    for app_url in chronos_common_access_url:
        print ("\nExecuting Test for {} endpoint \n".format(app_url))
        utilsObj.test_proxy_user_valid_permissions_read(app_url, headers)

    time.sleep(10)

    json_data = utilsObj.create_json_data("/sample_chronos_data.json")

    app_url = chronos_url + '/scheduler/iso8601'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_create(app_url, headers, json_data)

    time.sleep(10)

    json_data = utilsObj.create_json_data("/sample_dependency.json")
    app_url = chronos_url + '/scheduler/dependency'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_create(app_url, headers, json_data)

    app_url = chronos_url + '/scheduler/job/internal-test-team-sample-chronos-job'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_create(app_url, headers, json_data)

    app_url = chronos_url + '/scheduler/job/stat/internal-test-team-sample-chronos-job'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_read(app_url, headers)

    app_url = chronos_url + '/scheduler/job/internal-test-team-sample-chronos-job'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_delete(app_url, headers, json_data)

    app_url = chronos_url + '/scheduler/job/internal-test-team-dependency'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_valid_permissions_delete(app_url, headers, json_data)

    json_data = "notjson"
    app_url = chronos_url + '/scheduler/iso8601'
    print ("\nExecuting Test for Invalid Body \n")
    utilsObj.test_proxy_user_invalid_body(app_url, headers, json_data)

    json_data = utilsObj.create_json_data("/sample_chronos_data.json")
    json_data['name'] = "test"  # Invalid Body
    app_url = chronos_url + '/scheduler/iso8601'
    print ("\nExecuting Test for {} endpoint \n".format(app_url))
    utilsObj.test_proxy_user_invalid_body(app_url, headers, json_data)


if __name__ == "__main__":
    main(sys.argv)
