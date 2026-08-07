# Bugcrowd CSV Grabber

![BugcrowdCsvGrabber](./img/BugcrowdCsvGrabber.png)

<div align="center">

![last commit](https://img.shields.io/github/last-commit/tyto-sec/BugcrowdCSVGrabber) ![created](https://img.shields.io/github/created-at/tyto-sec/BugcrowdCSVGrabber) ![language](https://img.shields.io/github/languages/top/tyto-sec/BugcrowdCSVGrabber) ![workflow](https://img.shields.io/github/actions/workflow/status/tyto-sec/BugcrowdCSVGrabber/tests.yml) ![stars](https://img.shields.io/github/stars/tyto-sec/BugcrowdCSVGrabber) 

</div>



> `BugcrowdCsvGrabber` is a specialized Python tool that processes one or more CSV files exported from Bugcrowd's scope page to extract and organize in-scope assets. It automatically cleans domains, validates formats, expands IP ranges, and generates comprehensive asset reports.

<br>

## Features

*   **CSV Batch Processing:** Handles all CSV files within a specified input directory.
*   **Multi-Asset Extraction:** Extracts websites, APIs, IP addresses, network ranges, iOS, Android, hardware, IoT, and other assets.
*   **IP Range Expansion:** Converts CIDR notation to individual IP addresses.
*   **Comprehensive Validation:** Uses regex patterns to validate domains, IPs, and CIDR ranges.
*   **Deduplication:** All outputs are deduplicated and sorted alphabetically.
*   **Scope Filtering:** Only extracts entries where `inScope` is `true`.

<br>

## Installation

Install as a command-line tool:

```bash
pip install .
BugcrowdCsvGrabber --help
```

Or run directly from source:

```bash
python3 -m main --input <path> --output <path>
```

<br>

## Usage

```bash
BugcrowdCsvGrabber --input ./scope --output ./results
```

**Arguments:**
- `--input PATH`: Directory containing Bugcrowd CSV files
- `--output PATH`: Output directory for extracted assets
- `--version`: Show version information
- `-h, --help`: Display help message with full documentation

### Example

```bash
BugcrowdCsvGrabber --input ./bugcrowd_exports --output ./targets
```

<br>


## Output Files

The tool generates the following files in the output directory:

| File | Description |
|------|-------------|
| `rough_websites.txt` | Raw website targets |
| `rough_apis.txt` | Raw API targets |
| `rough_ip_addresses.txt` | Raw IP addresses |
| `rough_networks.txt` | Raw network ranges (CIDR) |
| `rough_other_assets.txt` | Raw other assets |
| `rough_ios.txt` | Raw iOS assets |
| `rough_android.txt` | Raw Android assets |
| `rough_hardware.txt` | Raw hardware assets |
| `rough_iot.txt` | Raw IoT assets |
| `cleaned_domains.txt` | Cleaned and validated domains |
| `cleaned_ips.txt` | Cleaned IPs and expanded CIDR hosts |

<br>

## Input CSV Format

The script expects CSV files with the following columns (standard Bugcrowd export):

| Column | Description |
|--------|-------------|
| **`programName`** | Program name |
| **`inScope`** | Boolean flag (`true`/`false`) - only `true` entries are extracted |
| **`targetCategory`** | Category of asset (website, api, ip_address, network, ios, android, hardware, iot, other) |
| **`targetUri`** | Target URI (when present) |
| **`targetName`** | Target name (when present) |
| **`targetIpAddress`** | Target IP address (when present) |
| **`targetCidr`** | Target network CIDR (when present) |

<br>

## Testing

The project includes unit tests:

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
