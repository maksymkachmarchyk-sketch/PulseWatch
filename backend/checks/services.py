
import requests
import time
import socket
import ipaddress

from urllib.parse import urlsplit
from .models import CheckResult


class SSRFBlockedError(Exception):
    pass


def validate_public_url(url):
    try:
        parsed_url = urlsplit(url)

        if parsed_url.scheme not in ('http', 'https'):
            raise SSRFBlockedError('Only HTTP and HTTPS URLs are allowed.')

        if not parsed_url.hostname:
            raise SSRFBlockedError('Invalid URL hostname.')

        if parsed_url.username or parsed_url.password:
            raise SSRFBlockedError('URLs with credentials are not allowed.')

        port = parsed_url.port

        if port is not None and port not in (80, 443):
            raise SSRFBlockedError('This port is not allowed.')

        hostname = parsed_url.hostname.rstrip('.').lower()

        if hostname == 'localhost' or hostname.endswith('.localhost'):
            raise SSRFBlockedError('Localhost addresses are not allowed.')

        try:
            ip = ipaddress.ip_address(hostname)
            addresses = [ip]
        except ValueError:
            try:
                results = socket.getaddrinfo(
                    hostname,
                    None,
                    type=socket.SOCK_STREAM
                )
            except socket.gaierror:
                raise SSRFBlockedError('Could not resolve hostname.')

            addresses = [
                ipaddress.ip_address(result[4][0].split('%')[0])
                for result in results
            ]

        if not addresses:
            raise SSRFBlockedError('No IP addresses found.')

        for address in addresses:
            if not address.is_global:
                raise SSRFBlockedError(
                    'Private or reserved IP addresses are not allowed.'
                )

    except ValueError:
        raise SSRFBlockedError('Invalid URL or port.')


def is_success(status_code):
    return 200 <= status_code <= 299


def check_website(url, timeout):
    try:
        validate_public_url(url)

        start = time.perf_counter()

        with requests.Session() as session:
            session.trust_env = False

            response = session.get(
                url,
                timeout=timeout,
                allow_redirects=False
            )

        end = time.perf_counter()

        response_time = (end - start) * 1000

        return {
            'status_code': response.status_code,
            'response_time': round(response_time, 2),
            'is_success': is_success(response.status_code),
            'error_message': ''
        }

    except SSRFBlockedError as error:
        return {
            'status_code': None,
            'response_time': None,
            'is_success': False,
            'error_message': str(error)
        }

    except requests.exceptions.Timeout:
        return {
            'status_code': None,
            'response_time': None,
            'is_success': False,
            'error_message': 'Timeout'
        }

    except requests.exceptions.ConnectionError:
        return {
            'status_code': None,
            'response_time': None,
            'is_success': False,
            'error_message': 'Connection Error'
        }

    except requests.exceptions.RequestException:
        return {
            'status_code': None,
            'response_time': None,
            'is_success': False,
            'error_message': 'Request Error'
        }


def run_check(monitor):
    url = monitor.url
    timeout = monitor.timeout

    result = check_website(url, timeout)

    check_result = CheckResult.objects.create(
        monitor=monitor,
        status_code=result['status_code'],
        response_time=result['response_time'],
        is_success=result['is_success'],
        error_message=result['error_message']
    )

    return check_result
