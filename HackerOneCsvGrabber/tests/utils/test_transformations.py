import pytest

from src.utils import transformations


@pytest.mark.parametrize(
	"value,expected",
	[
		("Visit https://example.com/path?q=1", "https://example.com/path?q=1"),
		("See www.example.com/docs", "www.example.com/docs"),
		("Net 10.0.0.0/24 is here", "10.0.0.0/24"),
		("IP 192.168.1.10 is up", "192.168.1.10"),
		("domain: sub.example.co.uk", "sub.example.co.uk"),
		("no matches here", "no matches here"),
		("", ""),
		(None, None),
	],
)
def test_extract_url_or_ip(value, expected):
	assert transformations._extract_url_or_ip(value) == expected


@pytest.mark.parametrize(
	"value,expected",
	[
		("https://Example.com/Path", "example.com"),
		("http://example.com:8080/", "example.com"),
		("www.Example.com", "example.com"),
		("*.Example.com", "example.com"),
		("*.*.Example.com", "example.com"),
		("example.com.", "example.com"),
		("example.com?foo=bar", "example.com"),
		("example.com#frag", "example.com"),
		("  Example.com  ", "example.com"),
		("10.0.0.0/24", "10.0.0.0/24"),
		("Reach me at https://user@Sub.Example.com:443/home", "sub.example.com"),
	],
)
def test_clean_domain(value, expected):
	assert transformations.clean_domain(value) == expected


@pytest.mark.parametrize(
	"value,expected",
	[
		("http://192.168.0.1", "192.168.0.1"),
		("https://user@10.0.0.1:8443/path", "10.0.0.1"),
		("10.0.0.1/24", "10.0.0.1"),
		("10.0.0.1?x=1", "10.0.0.1"),
		("10.0.0.1#frag", "10.0.0.1"),
		("  8.8.8.8  ", "8.8.8.8"),
		("IP is 1.2.3.4 inside", "1.2.3.4"),
		("", ""),
	],
)
def test_clean_ip(value, expected):
	assert transformations.clean_ip(value) == expected


def test_get_ip_addresses_from_cidr():
	result = transformations.get_ip_addresses_from_cidr("192.168.1.0/30")
	assert result == ["192.168.1.1", "192.168.1.2"]
