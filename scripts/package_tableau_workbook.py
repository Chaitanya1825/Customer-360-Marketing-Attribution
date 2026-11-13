import os
import zipfile
import subprocess
import time
import json
import xml.etree.ElementTree as ET

BASE_DIR = r"C:\Users\HP\Desktop\Customer 360 and Marketing Attribution Platform"
TABLEAU_DIR = os.path.join(BASE_DIR, "exports", "tableau")
DIR_NORM = TABLEAU_DIR.replace("\\", "/")

def create_packages():
    # Read base workbook
    hyper_twb_path = os.path.join(TABLEAU_DIR, "Customer360_Hyper.twb")
    final_twb_path = os.path.join(TABLEAU_DIR, "Customer360_Analytics.twb")

    if os.path.exists(hyper_twb_path):
        with open(hyper_twb_path, "r", encoding="utf-8") as f:
            hyper_xml = f.read()
        with open(final_twb_path, "w", encoding="utf-8") as f:
            f.write(hyper_xml)
        os.remove(hyper_twb_path)
    else:
        with open(final_twb_path, "r", encoding="utf-8") as f:
            hyper_xml = f.read()

    print(f"Verified base TWB: {final_twb_path}")

    # 2. Build Customer360_Analytics.twbx (Packaged Workbook)
    # Inside twbx, relative paths are: Data/Extracts/*.hyper
    rel_xml = hyper_xml.replace(
        f"{DIR_NORM}/customer_360.hyper", "Data/Extracts/customer_360.hyper"
    ).replace(
        f"{DIR_NORM}/fct_order_attribution.hyper", "Data/Extracts/fct_order_attribution.hyper"
    ).replace(
        f"{DIR_NORM}/fct_campaign_performance.hyper", "Data/Extracts/fct_campaign_performance.hyper"
    )

    twbx_path = os.path.join(TABLEAU_DIR, "Customer360_Analytics.twbx")
    with zipfile.ZipFile(twbx_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write inner twb
        zf.writestr("Customer360_Analytics.twb", rel_xml)
        # Write hyper files into Data/Extracts/
        zf.write(os.path.join(TABLEAU_DIR, "customer_360.hyper"), "Data/Extracts/customer_360.hyper")
        zf.write(os.path.join(TABLEAU_DIR, "fct_order_attribution.hyper"), "Data/Extracts/fct_order_attribution.hyper")
        zf.write(os.path.join(TABLEAU_DIR, "fct_campaign_performance.hyper"), "Data/Extracts/fct_campaign_performance.hyper")
    
    print(f"Created Packaged Workbook: {twbx_path} (Size: {os.path.getsize(twbx_path)} bytes)")

if __name__ == '__main__':
    create_packages()

