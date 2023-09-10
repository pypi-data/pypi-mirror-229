import httpx

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
                raise Exception('Invalid email!')
            elif response.status_code == 200:
                # Returns the user with class User
                return User(response.json(), Package(response.json()['package'], response.json()['extra']))

