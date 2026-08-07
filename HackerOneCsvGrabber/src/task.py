import os
import glob
import datetime as dt

from src.core.csv_extractor import (
    extract_asset
)
from src.core.txt_loader import (
    save_asset_to_file
)
from src.utils.transformations import (
    clean_domain,
    get_ip_addresses_from_cidr
)
from src.utils.filters import (
    is_valid_domain,
    is_valid_ip,
    is_valid_cidr
)


def run(input_directory, output_directory):
    all_assets = {}
    
    csv_pattern = os.path.join(input_directory, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {input_directory}")
        return
    
    for csv_file in csv_files:
        print(f"Processing {os.path.basename(csv_file)}...")
        urls = extract_asset(csv_file, "url")
        all_assets["urls"] = all_assets.get("urls", set()).union(urls)
        
        wildcards = extract_asset(csv_file, "wildcard")
        all_assets["wildcards"] = all_assets.get("wildcards", set()).union(wildcards)
        
        repos = extract_asset(csv_file, "source_code")
        all_assets["source_code_repos"] = all_assets.get("source_code_repos", set()).union(repos)

        ips = extract_asset(csv_file, "ip_address")
        all_assets["ip_addresses"] = all_assets.get("ip_addresses", set()).union(ips)

        ip_ranges = extract_asset(csv_file, "cidr")
        all_assets["ip_ranges"] = all_assets.get("ip_ranges", set()).union(ip_ranges)

        apple_store_app_ids = extract_asset(csv_file, "apple_store_app_id")
        all_assets["apple_store_app_ids"] = all_assets.get("apple_store_app_ids", set()).union(apple_store_app_ids)

        google_play_app_ids = extract_asset(csv_file, "google_play_app_id")
        all_assets["google_play_app_ids"] = all_assets.get("google_play_app_ids", set()).union(google_play_app_ids)

    print("\n###########################################################################################")
    print("#                                   Extraction Summary                                    #")
    print("###########################################################################################\n")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_urls.txt")
    save_asset_to_file(all_assets.get("urls", set()), output_file, "URLs")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_wildcards.txt")
    save_asset_to_file(all_assets.get("wildcards", set()), output_file, "Wildcards")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_source_code_repos.txt")
    save_asset_to_file(all_assets.get("source_code_repos", set()), output_file, "Source Code Repositories")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_ip_addresses.txt")
    save_asset_to_file(all_assets.get("ip_addresses", set()), output_file, "IP Addresses")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_ip_ranges.txt")
    save_asset_to_file(all_assets.get("ip_ranges", set()), output_file, "IP Ranges")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_apple_store_app_ids.txt")
    save_asset_to_file(all_assets.get("apple_store_app_ids", set()), output_file, "Apple Store App IDs")

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_google_play_app_ids.txt")
    save_asset_to_file(all_assets.get("google_play_app_ids", set()), output_file, "Google Play App IDs")

    for urls in all_assets.get("urls", set()):
        cleaned_url = clean_domain(urls)
        if is_valid_domain(cleaned_url):
            all_assets["cleaned_urls"] = all_assets.get("cleaned_urls", set()).union({cleaned_url})

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_cleaned_urls.txt")
    save_asset_to_file(all_assets.get("cleaned_urls", set()), output_file, "Cleaned URLs")

    for wildcards in all_assets.get("wildcards", set()):
        cleaned_wildcard = clean_domain(wildcards)
        if is_valid_domain(cleaned_wildcard):
            all_assets["wildcards_domains"] = all_assets.get("wildcards_domains", set()).union({cleaned_wildcard})

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_wildcards_domains.txt")
    save_asset_to_file(all_assets.get("wildcards_domains", set()), output_file, "Wildcards Domains")

    expanded_ips = set()
    for cidr in all_assets.get("ip_ranges", set()):
        if is_valid_cidr(cidr):
            ips = get_ip_addresses_from_cidr(cidr)
            expanded_ips.update(ips)
    all_assets["expanded_ip_addresses"] = expanded_ips.union(all_assets.get("ip_addresses", set()))

    output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_expanded_ip_addresses.txt")
    save_asset_to_file(all_assets.get("expanded_ip_addresses", set()), output_file, "Expanded IP Addresses") 

    print("\nExtraction completed successfully!\n")  