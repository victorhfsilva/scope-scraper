from pathlib import Path

from src.core.txt_loader import save_asset_to_file


def test_save_asset_to_file_writes_sorted_assets(tmp_path: Path):
	output_file = tmp_path / "assets.txt"
	assets = {"b.example.com", "a.example.com", "c.example.com"}

	save_asset_to_file(assets, str(output_file), "domains")

	content = output_file.read_text(encoding="utf-8")
	assert content == "a.example.com\nb.example.com\nc.example.com\n"


def test_save_asset_to_file_prints_summary(tmp_path: Path, capsys):
	output_file = tmp_path / "ips.txt"
	assets = {"1.1.1.1", "8.8.8.8"}

	save_asset_to_file(assets, str(output_file), "ips")

	captured = capsys.readouterr()
	assert (
		captured.out
		== f"Extracted {len(assets)} unique ips to {output_file}\n"
	)
