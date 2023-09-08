import socket
import godaddypy
from .tools import env


def get_dns_client(
        api_key = env("DNS_API_KEY"), 
        api_secret = env("DNS_API_SECRET"),
    ):
    dns_acct = godaddypy.Account(api_key=api_key, api_secret=api_secret)
    return godaddypy.Client(dns_acct)


def register_dns(
        domain = env("DOMAIN"), 
        subdomain = env("SUBDOMAIN"), 
        ip_address = env("IP_ADDRESS"),
    ):
    dns = get_dns_client()
    if subdomain == "www": 
        # Update the main record if www is the default subdomain for Odoo.
        record = {'data': ip_address, 'name': '@', 'ttl': 3600, 'type': 'A'}
        dns.update_record(domain, record)
    record = {'data': ip_address, 'name': subdomain, 'ttl': 3600, 'type': 'A'}
    dns.update_record(domain, record)


def test_dns(
        domain = env("DOMAIN"), 
        expected_ip = env("IP_ADDRESS"),
    ) -> bool:
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        return expected_ip in ip_addresses
    except socket.gaierror:
        return False

