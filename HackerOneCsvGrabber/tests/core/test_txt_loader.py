from src.core.txt_loader import save_asset_to_file


def test_writes_sorted_assets(tmp_path):
	output_file = tmp_path / "assets.txt"
	assets = {"b.example.com", "a.example.com", "c.example.com"}

	save_asset_to_file(assets, output_file, "URLs")

	content = output_file.read_text(encoding="utf-8")
	assert content == "a.example.com\nb.example.com\nc.example.com\n"


def test_prints_summary_message(capsys, tmp_path):
	output_file = tmp_path / "assets.txt"
	assets = {"one", "two"}

	save_asset_to_file(assets, output_file, "IPs")

	captured = capsys.readouterr().out.strip()
	expected = f"Extracted {len(assets)} unique IPs to {output_file}"
	assert captured == expected
