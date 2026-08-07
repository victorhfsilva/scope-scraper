from pathlib import Path

import pytest

from src.core.csv_extractor import extract_asset


def _write_csv(path: Path, content: str) -> None:
	path.write_text(content, encoding="utf-8")


def test_extract_asset_returns_empty_when_no_header(tmp_path):
	csv_path = tmp_path / "scopes.csv"
	_write_csv(csv_path, "no header here\n")

	result = extract_asset(str(csv_path), "website", "target")

	assert result == set()


def test_extract_asset_filters_by_scope_and_category(tmp_path):
	csv_path = tmp_path / "scopes.csv"
	_write_csv(
		csv_path,
		"programName,inScope,targetCategory,target\n"
		"Acme,true,website,example.com\n"
		"Acme,false,website,ignored.com\n"
		"Acme,true,api,api.example.com\n"
		"Acme,true,website,example.com\n",
	)

	result = extract_asset(str(csv_path), "website", "target")

	assert result == {"example.com"}


def test_extract_asset_supports_preamble_before_header(tmp_path):
	csv_path = tmp_path / "scopes.csv"
	_write_csv(
		csv_path,
		"Some banner line\n"
		"Another line\n"
		"programName,inScope,targetCategory,identifier\n"
		"Acme,true,website,site.acme.com\n",
	)

	result = extract_asset(str(csv_path), "website", "identifier")

	assert result == {"site.acme.com"}


def test_extract_asset_ignores_empty_identifier(tmp_path):
	csv_path = tmp_path / "scopes.csv"
	_write_csv(
		csv_path,
		"programName,inScope,targetCategory,target\n"
		"Acme,true,website,\n"
		"Acme,true,website,valid.example\n",
	)

	result = extract_asset(str(csv_path), "website", "target")

	assert result == {"valid.example"}


@pytest.mark.parametrize("in_scope_value", ["TRUE", "True", "true"])
def test_extract_asset_treats_in_scope_case_insensitive(tmp_path, in_scope_value):
	csv_path = tmp_path / "scopes.csv"
	_write_csv(
		csv_path,
		"programName,inScope,targetCategory,target\n"
		f"Acme,{in_scope_value},website,example.com\n",
	)

	result = extract_asset(str(csv_path), "website", "target")

	assert result == {"example.com"}
