import re

def is_valid_domain(domain):
    if not domain:
        return False

    value = domain.strip()
    if not value:
        return False

    scheme_match = re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', value)
    if scheme_match:
        remainder = value[scheme_match.end():]
    else:
        remainder = value

    if '@' in remainder:
        remainder = remainder.split('@', 1)[1]

    host = remainder.split('/', 1)[0].split('?', 1)[0].split('#', 1)[0]
    host = host.split(':', 1)[0]

    if not host or '.' not in host:
        return False

    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    if not re.match(domain_pattern, host):
        return False

    parts = host.split('.')
    if all(part.isdigit() for part in parts):
        return False

    return True

def is_valid_ip(address):
    if not address:
        return False

    value = address.strip()
    if not value:
        return False

    scheme_match = re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', value)
    if scheme_match:
        remainder = value[scheme_match.end():]
    else:
        remainder = value

    if '@' in remainder:
        remainder = remainder.split('@', 1)[1]

    host = remainder.split('/', 1)[0].split('?', 1)[0].split('#', 1)[0]
    host = host.split(':', 1)[0]

    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, host):
        parts = host.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

def is_valid_cidr(cidr):
    if not cidr:
        return False

    value = cidr.strip()
    if not value:
        return False

    scheme_match = re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', value)
    if scheme_match:
        remainder = value[scheme_match.end():]
    else:
        remainder = value

    if '@' in remainder:
        remainder = remainder.split('@', 1)[1]

    segment = remainder.split('?', 1)[0].split('#', 1)[0]
    if '/' not in segment:
        return False

    host_port, rest = segment.split('/', 1)
    prefix_length = rest.split('/', 1)[0]
    host = host_port.split(':', 1)[0]

    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, host):
        return False

    parts = host.split('.')
    if not all(0 <= int(part) <= 255 for part in parts):
        return False

    if not prefix_length.isdigit():
        return False

    return 0 <= int(prefix_length) <= 32