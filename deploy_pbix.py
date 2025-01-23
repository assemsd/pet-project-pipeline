import argparse
import sys
import json
import urllib.parse
import urllib.request


def get_access_token(tenant_id, client_id, secret_id):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

    data = {
        'client_id': client_id,
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
        'client_secret': secret_id,
        'grant_type': 'client_credentials'
    }

    encoded_data = urllib.parse.urlencode(data).encode('utf-8')

    req = urllib.request.Request(url, data=encoded_data, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.load(response)
            access_token = response_data.get('access_token')
            print('Access Token:', access_token)
            return access_token
    except urllib.error.HTTPError as e:
        error_message = e.read().decode('utf-8')
        print('Failed to retrieve token:', error_message)
        return None


def deploy_pbix(workspace_id, pbix_file_path, access_token):
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    with open(pbix_file_path, 'rb') as pbix_file:
        file_data = pbix_file.read()

    req = urllib.request.Request(url, data=file_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f'Successfully deployed the report to workspace {workspace_id}')
            else:
                error_message = response.read().decode("utf-8")
                print(f"Response status code: {response.status}")
                print(f"Failed to deploy the report: {error_message}")
    except urllib.error.HTTPError as e:
        print(f"HTTPError occurred:")
        print(f"URL: {e.url}")
        print(f"Code: {e.code}")
        print(f"Reason: {e.reason}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, help="Workspace ID")
    parser.add_argument('--filePath', required=True, help="Path to PBIX file")
    parser.add_argument('--tenant_id', required=True, help="Tenant ID")
    parser.add_argument('--client_id', required=True, help="Client ID")
    parser.add_argument('--secret_id', required=True, help="Secret ID")

    args = parser.parse_args()

    access_token = get_access_token(args.tenant_id, args.client_id, args.secret_id)

    if access_token:
        deploy_pbix(args.workspace, args.filePath, access_token)
