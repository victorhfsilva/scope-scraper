import argparse
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from src.task import (
	run
)


def main():
	banner = r"""
            888888b.                                                                 888              
            888  "88b                                                                888              
            888  .88P                                                                888              
            8888888K.  888  888  .d88b.   .d8888b 888d888 .d88b.  888  888  888  .d88888              
            888  "Y88b 888  888 d88P"88b d88P"    888P"  d88""88b 888  888  888 d88" 888              
            888    888 888  888 888  888 888      888    888  888 888  888  888 888  888              
            888   d88P Y88b 888 Y88b 888 Y88b.    888    Y88..88P Y88b 888 d88P Y88b 888              
            8888888P"   "Y88888  "Y88888  "Y8888P 888     "Y88P"   "Y8888888P"   "Y88888              
                                     888                                                              
                                Y8b d88P                                                              
                                 "Y88P"                                                               
    .d8888b.   .d8888b.  888     888       .d8888b.                  888      888                       
    d88P  Y88b d88P  Y88b 888     888      d88P  Y88b                 888      888                       
    888    888 Y88b.      888     888      888    888                 888      888                       
    888         "Y888b.   Y88b   d88P      888        888d888 8888b.  88888b.  88888b.   .d88b.  888d888 
    888            "Y88b.  Y88b d88P       888  88888 888P"      "88b 888 "88b 888 "88b d8P  Y8b 888P"   
    888    888       "888   Y88o88P        888    888 888    .d888888 888  888 888  888 88888888 888     
    Y88b  d88P Y88b  d88P    Y888P         Y88b  d88P 888    888  888 888 d88P 888 d88P Y8b.     888     
     "Y8888P"   "Y8888P"      Y8P           "Y8888P88 888    "Y888888 88888P"  88888P"   "Y8888  888 1.0.0     
                                                                                                                                                                                                       
	"""
	print(banner)

	parser = argparse.ArgumentParser(
		description="Bugcrowd CSV Grabber - Extracts and processes scope assets from Bugcrowd CSV files.",
		prog='BugcrowdCsvGrabber',
		epilog="""
EXAMPLES:
  BugcrowdCsvGrabber --input ./scope --output ./results
  BugcrowdCsvGrabber --input /path/to/csvs --output /path/to/output

OUTPUT FILES:
  - rough_websites.txt              - Raw website targets
  - rough_apis.txt                  - Raw API targets
  - rough_ip_addresses.txt          - Raw IP addresses
  - rough_networks.txt              - Raw network ranges (CIDR)
  - rough_other_assets.txt          - Raw other assets
  - rough_ios.txt                   - Raw iOS assets
  - rough_android.txt               - Raw Android assets
  - rough_hardware.txt              - Raw hardware assets
  - rough_iot.txt                   - Raw IoT assets
  - cleaned_domains.txt             - Cleaned and validated domains
  - cleaned_ips.txt                 - Cleaned IPs and expanded CIDR hosts
		""",
		formatter_class=argparse.RawDescriptionHelpFormatter
	)

	parser.add_argument(
		'--version',
		action='version',
		version='%(prog)s 1.0.0'
	)

	parser.add_argument(
		'--input',
		type=str,
		required=True,
		metavar='PATH',
		help='Directory containing Bugcrowd CSV files to process'
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
