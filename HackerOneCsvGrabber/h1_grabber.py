import argparse
import sys
import os

from src.task import (
    run
)

def main():
    banner = """
       888    888                   888                             .d88888b.                          
       888    888                   888                            d88P" "Y88b                         
       888    888                   888                            888     888                         
       8888888888  8888b.   .d8888b 888  888  .d88b.  888d888      888     888 88888b.   .d88b.        
       888    888     "88b d88P"    888 .88P d8P  Y8b 888P"        888     888 888 "88b d8P  Y8b       
       888    888 .d888888 888      888888K  88888888 888          888     888 888  888 88888888       
       888    888 888  888 Y88b.    888 "88b Y8b.     888          Y88b. .d88P 888  888 Y8b.           
       888    888 "Y888888  "Y8888P 888  888  "Y8888  888           "Y88888P"  888  888  "Y8888        
                                                                                                    
                                                                                                    
                                                                                                    
     .d8888b.                          .d8888b.                  888      888                       
    d88P  Y88b                        d88P  Y88b                 888      888                       
    888    888                        888    888                 888      888                       
    888        .d8888b  888  888      888        888d888 8888b.  88888b.  88888b.   .d88b.  888d888 
    888        88K      888  888      888  88888 888P"      "88b 888 "88b 888 "88b d8P  Y8b 888P"   
    888    888 "Y8888b. Y88  88P      888    888 888    .d888888 888  888 888  888 88888888 888     
    Y88b  d88P      X88  Y8bd8P       Y88b  d88P 888    888  888 888 d88P 888 d88P Y8b.     888     
     "Y8888P"   88888P'   Y88P         "Y8888P88 888    "Y888888 88888P"  88888P"   "Y8888  888 2.0.0    
    
    """
    print(banner)
    
    parser = argparse.ArgumentParser(
        description="HackerOneCsvGrabber - Extracts and processes scope assets from HackerOne CSV files.",
        prog='HackerOneCsvGrabber',
        epilog="""
EXAMPLES:
  HackerOneCsvGrabber --input ./scope --output ./results
  HackerOneCsvGrabber --input /path/to/csvs --output /path/to/output

OUTPUT FILES:
  - rough_urls.txt                    - Raw URLs extracted from CSV
  - rough_wildcards.txt               - Raw wildcard domains
  - cleaned_urls.txt                  - Cleaned and validated domains
  - wildcards_domains.txt             - Cleaned wildcard domains
  - rough_ip_addresses.txt            - Individual IP addresses
  - rough_ip_ranges.txt               - IP ranges (CIDR notation)
  - expanded_ip_addresses.txt         - All IPs from expanded ranges
  - source_code_repos.txt             - Source code repositories
  - apple_store_app_ids.txt           - Apple Store app identifiers
  - google_play_app_ids.txt           - Google Play app identifiers

For more info, visit: https://github.com/tyto-sec/HackerOneCsvGrabber
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        metavar='PATH',
        help='Directory containing HackerOne CSV files to process'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        metavar='PATH',
        help='Output directory where extracted assets will be saved'
    )

    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output   
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' does not exist")
        sys.exit(1)
    
    run(input_dir, output_dir)


if __name__ == '__main__':
    main()