import re
from ipaddress import ip_network


def _extract_url_or_ip(value):
    if not value:
        return value

    url_match = re.search(r'[a-zA-Z][a-zA-Z0-9+\-.]*://[^\s]+', value)
    if url_match:
        return url_match.group(0)

    www_match = re.search(r'www\.[^\s]+', value)
    if www_match:
        return www_match.group(0)

    cidr_match = re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b', value)
    if cidr_match:
        return cidr_match.group(0)

    ip_match = re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', value)
    if ip_match:
        return ip_match.group(0)

    domain_match = re.search(r'\b[a-zA-Z0-9][a-zA-Z0-9\-\.]*\.[a-zA-Z]{2,}\b', value)
    if domain_match:
        return domain_match.group(0)

    return value


def clean_domain(domain):
    domain = _extract_url_or_ip(domain)
    domain = domain.strip()
    if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}$', domain):
        return domain
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^(\*\.|\*|www\.)+', '', domain)
    if '@' in domain:
        domain = domain.split('@', 1)[1]
    domain = domain.split('/')[0]
    domain = domain.split(':')[0]
    if domain.endswith('.'):
        domain = domain[:-1]
    domain = domain.split('?')[0]
    domain = domain.split('#')[0]
    
    return domain.strip().lower()

def clean_ip(address):
    value = _extract_url_or_ip(address)
    value = value.strip()
    if not value:
        return value

    scheme_match = re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', value)
    if scheme_match:
        value = value[scheme_match.end():]

    if '@' in value:
        value = value.split('@', 1)[1]

    value = value.split('/', 1)[0]
    value = value.split('?', 1)[0]
    value = value.split('#', 1)[0]

    value = value.split(':', 1)[0]

    return value.strip()

def get_ip_addresses_from_cidr(cidr):
    network = ip_network(cidr, strict=False)
    return [str(ip) for ip in network.hosts()]