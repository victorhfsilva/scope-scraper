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
    get_ip_addresses_from_cidr,
    clean_ip
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

        website_uri = extract_asset(csv_file, target_category="website", target_field="targetUri")
        all_assets["website"] = all_assets.get("website", set()).union(website_uri)

        website_name = extract_asset(csv_file, target_category="website", target_field="targetName")
        all_assets["website"] = all_assets.get("website", set()).union(website_name)

        website_ip = extract_asset(csv_file, target_category="website", target_field="targetIpAddress")
        all_assets["website"] = all_assets.get("website", set()).union(website_ip)

        api_uri = extract_asset(csv_file, target_category="api", target_field="targetUri")
        all_assets["api"] = all_assets.get("api", set()).union(api_uri)

        api_name = extract_asset(csv_file, target_category="api", target_field="targetName")
        all_assets["api"] = all_assets.get("api", set()).union(api_name)

        api_ip = extract_asset(csv_file, target_category="api", target_field="targetIpAddress")
        all_assets["api"] = all_assets.get("api", set()).union(api_ip)

        ip_address_uri = extract_asset(csv_file, target_category="ip_address", target_field="targetUri")
        all_assets["ip_address"] = all_assets.get("ip_address", set()).union(ip_address_uri)

        ip_address_name = extract_asset(csv_file, target_category="ip_address", target_field="targetName")
        all_assets["ip_address"] = all_assets.get("ip_address", set()).union(ip_address_name)

        ip_address_ip = extract_asset(csv_file, target_category="ip_address", target_field="targetIpAddress")
        all_assets["ip_address"] = all_assets.get("ip_address", set()).union(ip_address_ip)

        network_uri = extract_asset(csv_file, target_category="network", target_field="targetCidr")
        all_assets["network"] = all_assets.get("network", set()).union(network_uri)

        network_name = extract_asset(csv_file, target_category="network", target_field="targetName")
        all_assets["network"] = all_assets.get("network", set()).union(network_name)

        network_ip = extract_asset(csv_file, target_category="network", target_field="targetIpAddress")
        all_assets["network"] = all_assets.get("network", set()).union(network_ip)

        other_uri = extract_asset(csv_file, target_category="other", target_field="targetUri")
        all_assets["other"] = all_assets.get("other", set()).union(other_uri)

        other_name = extract_asset(csv_file, target_category="other", target_field="targetName")
        all_assets["other"] = all_assets.get("other", set()).union(other_name)

        other_ip = extract_asset(csv_file, target_category="other", target_field="targetIpAddress")
        all_assets["other"] = all_assets.get("other", set()).union(other_ip)

        ios_uri = extract_asset(csv_file, target_category="ios", target_field="targetUri")
        all_assets["ios"] = all_assets.get("ios", set()).union(ios_uri)

        ios_name = extract_asset(csv_file, target_category="ios", target_field="targetName")
        all_assets["ios"] = all_assets.get("ios", set()).union(ios_name)

        ios_ip = extract_asset(csv_file, target_category="ios", target_field="targetIpAddress")
        all_assets["ios"] = all_assets.get("ios", set()).union(ios_ip)

        android_uri = extract_asset(csv_file, target_category="android", target_field="targetUri")
        all_assets["android"] = all_assets.get("android", set()).union(android_uri)

        android_name = extract_asset(csv_file, target_category="android", target_field="targetName")
        all_assets["android"] = all_assets.get("android", set()).union(android_name)

        android_ip = extract_asset(csv_file, target_category="android", target_field="targetIpAddress")
        all_assets["android"] = all_assets.get("android", set()).union(android_ip)

        hardware_uri = extract_asset(csv_file, target_category="hardware", target_field="targetUri")
        all_assets["hardware"] = all_assets.get("hardware", set()).union(hardware_uri)

        hardware_name = extract_asset(csv_file, target_category="hardware", target_field="targetName")
        all_assets["hardware"] = all_assets.get("hardware", set()).union(hardware_name)

        hardware_ip = extract_asset(csv_file, target_category="hardware", target_field="targetIpAddress")
        all_assets["hardware"] = all_assets.get("hardware", set()).union(hardware_ip)

        iot_uri = extract_asset(csv_file, target_category="iot", target_field="targetUri")
        all_assets["iot"] = all_assets.get("iot", set()).union(iot_uri)

        iot_name = extract_asset(csv_file, target_category="iot", target_field="targetName")
        all_assets["iot"] = all_assets.get("iot", set()).union(iot_name)

        iot_ip = extract_asset(csv_file, target_category="iot", target_field="targetIpAddress")
        all_assets["iot"] = all_assets.get("iot", set()).union(iot_ip)

        print("\n###########################################################################################")
        print("#                                   Extraction Summary                                    #")
        print("###########################################################################################\n")

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_websites.txt")
        save_asset_to_file(all_assets.get("website", set()), output_file, "websites")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_apis.txt")
        save_asset_to_file(all_assets.get("api", set()), output_file, "APIs")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_ip_addresses.txt")
        save_asset_to_file(all_assets.get("ip_address", set()), output_file, "IP addresses")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_networks.txt")
        save_asset_to_file(all_assets.get("network", set()), output_file, "networks")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_other_assets.txt")
        save_asset_to_file(all_assets.get("other", set()), output_file, "other assetss")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_ios.txt")
        save_asset_to_file(all_assets.get("ios", set()), output_file, "iOS assets")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_android.txt")
        save_asset_to_file(all_assets.get("android", set()), output_file, "Android assets")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_hardware.txt")
        save_asset_to_file(all_assets.get("hardware", set()), output_file, "hardware assets")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_rough_iot.txt")
        save_asset_to_file(all_assets.get("iot", set()), output_file, "IoT assets")

        for urls in all_assets.get("website", set()).union(all_assets.get("api", set())):
            cleaned_domain = clean_domain(urls)
            if is_valid_domain(cleaned_domain):
                all_assets["cleaned_domains"] = all_assets.get("cleaned_domains", set()).union({cleaned_domain})
            elif is_valid_cidr(cleaned_domain):
                ip_list = get_ip_addresses_from_cidr(cleaned_domain)
                for ip in ip_list:
                    ip = clean_ip(ip)
                    all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({ip})
            elif is_valid_ip(cleaned_domain):
                cleaned_ip = clean_ip(cleaned_domain)
                all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({cleaned_ip})

        for api in all_assets.get("api", set()):
            cleaned_domain = clean_domain(api)
            if is_valid_domain(cleaned_domain):
                all_assets["cleaned_domains"] = all_assets.get("cleaned_domains", set()).union({cleaned_domain})
            elif is_valid_cidr(cleaned_domain):
                ip_list = get_ip_addresses_from_cidr(cleaned_domain)
                for ip in ip_list:
                    ip = clean_ip(ip)
                    all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({ip})
            elif is_valid_ip(cleaned_domain):
                cleaned_ip = clean_ip(cleaned_domain)
                all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({cleaned_ip})

        for ip in all_assets.get("ip_address", set()):
            cleaned_ip = clean_domain(ip)
            if is_valid_domain(cleaned_ip):
                all_assets["cleaned_domains"] = all_assets.get("cleaned_domains", set()).union({cleaned_ip})
            elif is_valid_cidr(cleaned_ip):
                ip_list = get_ip_addresses_from_cidr(cleaned_ip)
                for ip in ip_list:
                    ip = clean_ip(ip)
                    all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({ip})
            elif is_valid_ip(cleaned_ip):
                cleaned_ip = clean_ip(cleaned_ip)
                all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({cleaned_ip})

        for network in all_assets.get("network", set()):
            cleaned_network = clean_domain(network)
            if is_valid_domain(cleaned_network):
                all_assets["cleaned_domains"] = all_assets.get("cleaned_domains", set()).union({cleaned_network})
            elif is_valid_cidr(cleaned_network):
                ip_list = get_ip_addresses_from_cidr(cleaned_network)
                for ip in ip_list:
                    ip = clean_ip(ip)
                    all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({ip})
            elif is_valid_ip(cleaned_network):
                cleaned_network = clean_ip(cleaned_network)
                all_assets["cleaned_ips"] = all_assets.get("cleaned_ips", set()).union({cleaned_network})

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_cleaned_domains.txt")
        save_asset_to_file(all_assets.get("cleaned_domains", set()), output_file, "cleaned domains")

        output_file = os.path.join(output_directory, f"{dt.datetime.now().strftime('%Y%m%d')}_cleaned_ips.txt")
        save_asset_to_file(all_assets.get("cleaned_ips", set()), output_file, "cleaned IPs")