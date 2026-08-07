
# HackerOne CSV Grabber

![HackerOneCsvGrabber](./img/HackerOneCsvGrabber.png)

<div align="center">

![last commit](https://img.shields.io/github/last-commit/tyto-sec/HackerOneCsvGrabber) ![created](https://img.shields.io/github/created-at/tyto-sec/HackerOneCsvGrabber) ![language](https://img.shields.io/github/languages/top/tyto-sec/HackerOneCsvGrabber) ![workflow](https://img.shields.io/github/actions/workflow/status/tyto-sec/HackerOneCsvGrabber/tests.yml) ![stars](https://img.shields.io/github/stars/tyto-sec/HackerOneCsvGrabber) 

</div>



> `HackerOneCsvGrabber` is a specialized Python tool that processes one or more CSV files exported from HackerOne's scope page to extract and organize in-scope assets. It automatically cleans domains, validates formats, expands IP ranges, and generates comprehensive asset reports.

<br>

## Features

*   **CSV Batch Processing:** Handles all CSV files within a specified input directory.
*   **Multi-Asset Extraction:** Extracts URLs, wildcards, IPs, CIDR ranges, app IDs, and source code repositories.
*   **IP Range Expansion:** Converts CIDR notation to individual IP addresses.
*   **Comprehensive Validation:** Uses regex patterns to validate domains, IPs, and CIDR ranges.
*   **Deduplication:** All outputs are deduplicated and sorted alphabetically.
*   **Scope Filtering:** Only extracts entries where `eligible_for_submission` is `true`.

<br>

## Installation

Install as a command-line tool:

```bash
pip install .
HackerOneCsvGrabber --help
```

Or run directly from source:

```bash
python3 -m main --input <path> --output <path>
```

<br>

## Usage

```bash
HackerOneCsvGrabber --input ./scope --output ./results
```

**Arguments:**
- `--input PATH`: Directory containing HackerOne CSV files
- `--output PATH`: Output directory for extracted assets
- `--version`: Show version information
- `-h, --help`: Display help message with full documentation

### Example

```bash
HackerOneCsvGrabber --input ./hackerone_exports --output ./targets
```

<br>


## Output Files

The tool generates the following files in the output directory:

| File | Description |
|------|-------------|
| `rough_urls.txt` | Raw URLs extracted from CSV |
| `rough_wildcards.txt` | Raw wildcard domains (e.g., `*.example.com`) |
| `cleaned_urls.txt` | Validated domains with protocols/ports removed |
| `wildcards_domains.txt` | Cleaned wildcard domains |
| `rough_ip_addresses.txt` | Individual IP addresses |
| `rough_ip_ranges.txt` | IP ranges in CIDR notation |
| `expanded_ip_addresses.txt` | All IPs from expanded CIDR ranges + individual IPs |
| `source_code_repos.txt` | Source code repository URLs |
| `apple_store_app_ids.txt` | Apple App Store identifiers |
| `google_play_app_ids.txt` | Google Play Store identifiers |

<br>

## Input CSV Format

The script expects CSV files with the following columns:

| Column | Description |
|--------|-------------|
| **`identifier`** | The target string (domain, URL, IP, app ID) |
| **`eligible_for_submission`** | Boolean flag (`true`/`false`) - only `true` entries are extracted |
| **`asset_type`** | Type of asset (url, wildcard, ip_address, cidr, apple_store_app_id, etc.) |

<br>

## Testing

The project includes comprehensive unit tests:

```bash
pytest
```

**Test Coverage:**
- Domain cleaning and normalization
- URL and CIDR parsing
- Asset validation (domains, IPs, CIDR ranges)
- File writing and deduplication

<br>

## License

See [LICENSE](LICENSE) file for details.

<br>

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

```bash
pytest
```



