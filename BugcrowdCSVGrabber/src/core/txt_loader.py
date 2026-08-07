def save_asset_to_file(assets, output_file, asset_type):
    with open(output_file, 'w', encoding='utf-8') as f:
        for asset in sorted(assets):
            f.write(f"{asset}\n")

        print(f"Extracted {len(assets)} unique {asset_type} to {output_file}")