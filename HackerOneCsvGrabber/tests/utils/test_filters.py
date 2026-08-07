import pytest

from src.utils.filters import is_valid_domain, is_valid_ip, is_valid_cidr


@pytest.mark.parametrize(
	"value",
	[
		"example.com",
		"sub.example.com",
		"example.co.uk",
		"https://example.com",
		"https://user:pass@example.com/path?query#frag",
		"http://example.com:8080/path",
		"ftp://sub.domain.io",
		"www.example.com",
	],
)
def test_is_valid_domain_accepts_valid_domains(value):
	assert is_valid_domain(value) is True


@pytest.mark.parametrize(
	"value",
	[
		"",
		"   ",
		None,
		"localhost",
		"example",
		"example.",
		".example.com",
		"-example.com",
		"example-.com",
		"http://256.1.1.1",
		"127.0.0.1",
		"http://127.0.0.1",
		"example.123",
		"exa_mple.com",
	],
)
def test_is_valid_domain_rejects_invalid_domains(value):
	assert is_valid_domain(value) is False


@pytest.mark.parametrize(
	"value",
	[
		"0.0.0.0",
		"8.8.8.8",
		"255.255.255.255",
		"http://192.168.0.1",
		"https://user@10.0.0.1:8443/path",
	],
)
def test_is_valid_ip_accepts_valid_ipv4(value):
	assert is_valid_ip(value) is True


@pytest.mark.parametrize(
	"value",
	[
		"",
		"   ",
		None,
		"256.0.0.1",
		"1.2.3",
		"1.2.3.4.5",
		"1.2.3.999",
		"abc.def.ghi.jkl",
		"http://example.com",
		"http://1.2.3.4.5",
	],
)
def test_is_valid_ip_rejects_invalid_ipv4(value):
	assert is_valid_ip(value) is False


@pytest.mark.parametrize(
	"value",
	[
		"192.168.0.0/24",
		"10.0.0.0/8",
		"0.0.0.0/0",
		"255.255.255.255/32",
		"http://172.16.0.0/12",
		"https://user@192.168.1.0/24?foo=bar",
	],
)
def test_is_valid_cidr_accepts_valid_cidr(value):
	assert is_valid_cidr(value) is True


@pytest.mark.parametrize(
	"value",
	[
		"",
		"   ",
		None,
		"192.168.0.0",
		"192.168.0.0/",
		"192.168.0.0/33",
		"192.168.0.0/-1",
		"192.168.0.0/abc",
		"256.168.0.0/24",
		"http://example.com/24",
	],
)
def test_is_valid_cidr_rejects_invalid_cidr(value):
	assert is_valid_cidr(value) is False
