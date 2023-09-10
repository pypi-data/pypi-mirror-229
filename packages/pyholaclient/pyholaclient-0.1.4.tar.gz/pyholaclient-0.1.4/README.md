# PyHolaClient
A HolaClient API Wrapper using Python!

[![Upload Python Package](https://github.com/VienDC/PyHolaClient/actions/workflows/python-publish.yml/badge.svg)](https://github.com/VienDC/PyHolaClient/actions/workflows/python-publish.yml)

Installation
To install just run
```bash
pip install pyholaclient
```

Usage:
```python
import pyholaclient

# Initialize the HolaClient with your API URL and API Key
client = pyholaclient.HolaClient('http://localhost', '123')

# Example 1: Get user information
user_info = client.user_info('example@gmail.com')
print("User Info:")
print(f"Email: {user_info.email}")
print(f"First Name: {user_info.first_name}")
print(f"Last Name: {user_info.last_name}")
print(f"Username: {user_info.username}")

# Example 2: Get user package 
package_name = client.user_package('example@gmail.com')
print("\nUser Email:")
print(f"Package Name: {package_name}")

# Example 3: Set user coins
status = client.set_coins('example@gmail.com', 100)
print("\nSet User Coins:")
print(f"Status: {'Success' if status else 'Failed'}")

# Example 4: Create a coupon
coupon = client.create_coupon(100, 1024, 1024, 1, 1, 1, 1, 1)
print("\nCreate Coupon:")
print(f"Coins: {coupon.coins}")
print(f"RAM: {coupon.ram} MB")
print(f"Disk: {coupon.disk} GB")
print(f"CPU: {coupon.cpu}%")
print(f"Servers: {coupon.servers}")
print(f"Backups: {coupon.backups}")
print(f"Allocations: {coupon.allocation}")
print(f"Databases: {coupon.database}")
```