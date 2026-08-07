import csv

def extract_asset(file_path, asset_type, target_field="identifier"):
    assets = set()

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = None
        for line in csvfile:
            if line.startswith('identifier') or line.startswith('program_id'):
                reader = csv.DictReader([line] + csvfile.readlines())
                break

        if reader is None:
            return assets

        for row in reader:
            if row.get('eligible_for_submission', 'false').lower() == 'true':
                if row.get('asset_type', '').lower() == asset_type.lower():
                    identifier = row.get(target_field, '').strip()
                    if identifier:
                        assets.add(identifier)
    return assets

