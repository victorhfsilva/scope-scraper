import csv

def extract_asset(file_path, target_category, target_field):
    assets = set()
    target_category_lower = target_category.lower()

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = None
        for line in csvfile:
            if line.startswith('programName,'):
                reader = csv.DictReader([line] + csvfile.readlines())
                break

        if reader is None:
            return assets

        for row in reader:
            in_scope = (row.get('inScope') or 'false').strip().lower()
            if in_scope != 'true':
                continue

            if (row.get('targetCategory') or '').strip().lower() != target_category_lower:
                continue

            identifier = (row.get(target_field) or '').strip()
            if identifier:
                assets.add(identifier)

    return assets

