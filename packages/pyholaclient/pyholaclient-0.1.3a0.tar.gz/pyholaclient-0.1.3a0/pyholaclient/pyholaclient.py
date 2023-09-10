import httpx
import string
import random

class Package:
    def __init__(self, default: list, extra: list):
        self.default = default
        self.extra = extra
        self.name = default['name']
        self.ram = default['ram']
        self.cpu = default['cpu']
        self.disk = default['disk']
        self.servers = default['servers']
        self.databases = default['databases']
        self.backups = default['backups']
        self.allocations = default['allocations']
        self.extra_ram = extra['ram']
        self.extra_cpu = extra['cpu']
        self.extra_disk = extra['disk']
        self.extra_servers = extra['servers']
        self.extra_databases = extra['databases']
        self.extra_backups = extra['backups']
        self.extra_allocations = extra['allocations']


class User:
    def __init__(self, user: dict, package: Package):
        self.package = package
        self.user = user['userinfo']
        self.email = self.user['attributes']['email']
        self.first_name = self.user['attributes']['first_name']
        self.last_name = self.user['attributes']['last_name']  
        self.username = self.user['attributes']['username']
        self.language = self.user['attributes']['language']
        self.id = self.user['attributes']['id']
        self.external_id = self.user['attributes']['external_id']
        self.root_admin = self.user['attributes']['root_admin']
        self.twofa_enabled = self.user['attributes']['2fa']
        self.uuid = self.user['attributes']['uuid']
        self.created_at = self.user['attributes']['created_at']
        self.updated_at = self.user['attributes']['updated_at']
        self.relationships = self.user['attributes']['relationships']
        self.attributes = self.user['attributes']
        self.coins = user['coins']

class Coupon:
    def __init__(self, coins: int, ram: int, disk: int, cpu: int, servers: int, backups: int, allocation: int, database: int, code: str = None):
        self.code = code
        self.coins = coins
        self.ram = ram
        self.disk = disk
        self.cpu = cpu
        self.servers = servers
        self.backups = backups
        self.allocation = allocation
        self.database = database
    

class HolaClient:
    def __init__(self, api_url, api_key):
        """
        Path: holaclient/holaclient.py     
        """
        self.api_url = api_url
        self.api_key = api_key
    def user_info(self, email):
        """
        Fetches user info from the API
        Params:
        email (str): email of the user
        Returns:

        """
        # Check if api_url and api_key are set
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/api/userinfo/?email={email}"
        headers = {'Authorization': f"{self.api_key}"}
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 301:
                # Returns if the API key is invalid
                raise Exception('Invalid API Key!')
            elif response.status_code == 400:
                # Returns when the email is invalid
                raise Exception('Email is Invalid or Not Found')
            elif response.status_code == 200:
                # Returns the user with class User
                return User(response.json(), Package(response.json()['package'], response.json()['extra']))
    def user_package(self, email):
        """
        Fetches package of a user from the API
        Params:
        email (str): email of the user
        Returns:
        Package Name: str
        """
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/api/package/?email={email}"
        headers = {'Authorization': f"{self.api_key}"}
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 301:
                # Returns if the API key is invalid
                raise Exception('Invalid API Key!')
            elif response.status_code == 400:
                # Returns when the email is invalid
                raise Exception('Email is Invalid or Not Found')
            elif response.status_code == 200:
                # Returns the user with class User
                data = response.json()
                return data['package']
    def set_coins(self, email: str, coins: int):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')

        url = f"{self.api_url}/api/setcoins/"
        headers = {'Authorization': self.api_key}
        payload = {'email': email, 'coins': coins}

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return True
                    else:
                        raise Exception('API request was not successful')
                elif response.status_code == 400:
                    raise Exception('Email is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')
    def create_coupon(self, coins: int, ram: int, disk: int, cpu: int, servers: int, backups: int, allocation: int, database: int, code: str = None):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        if not code:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        url = f"{self.api_url}/api/createcoupon/"
        headers = {'Authorization': self.api_key}
        payload = {
            'coins': coins,
            'ram': ram,
            'disk': disk,
            'cpu': cpu,
            'servers': servers,
            'backups': backups,
            'allocation': allocation,
            'database': database,
            'code': code
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return Coupon(coins, ram, disk, cpu, servers, backups, allocation, database, code)
                    else:
                        raise Exception('API request was not successful')
                elif response.status_code == 400:
                    raise Exception('Email is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')
