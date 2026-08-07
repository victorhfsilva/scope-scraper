import textwrap

from src.core.csv_extractor import extract_asset


def _write_csv(tmp_path, content):
	csv_file = tmp_path / "scopes.csv"
	csv_file.write_text(textwrap.dedent(content), encoding="utf-8")
	return csv_file


def test_extracts_only_matching_asset_type_and_eligible(tmp_path):
	csv_file = _write_csv(
		tmp_path,
		"""
		identifier,eligible_for_submission,asset_type
		example.com,true,url
		ignored.com,false,url
		10.0.0.1/24,true,ip_range
		api.example.com,true,url
		""",
	)

	assets = extract_asset(str(csv_file), "url")

	assert assets == {"example.com", "api.example.com"}

def test_ignores_ineligible_assets(tmp_path):
    csv_file = _write_csv(
        tmp_path,
        """
        identifier,eligible_for_submission,asset_type
        example.com,false,url
        api.example.com,true,url
        """,
    )
    assets = extract_asset(str(csv_file), "url")
    assert assets == {"api.example.com"}
	
def test_handles_empty_csv(tmp_path):
    csv_file = _write_csv(
        tmp_path,
        """
        identifier,eligible_for_submission,asset_type
        """,
    )

    assets = extract_asset(str(csv_file), "url")

    assert assets == set()
	
def test_handles_no_eligible_assets(tmp_path):
    csv_file = _write_csv(
        tmp_path,
        """
        identifier,eligible_for_submission,asset_type
        example.com,false,url
        """,
    )
    assets = extract_asset(str(csv_file), "url")
    assert assets == set()


def test_returns_empty_set_when_no_matching_asset_type(tmp_path):
	csv_file = _write_csv(
		tmp_path,
		"""
		identifier,eligible_for_submission,asset_type
		example.com,true,url
		10.0.0.1/24,true,ip_range
		""",
	)

	assets = extract_asset(str(csv_file), "wildcard")

	assert assets == set()
