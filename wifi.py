import datetime
import os
import winwifi
from subprocess import check_output
from csv import reader
import pywifi

# Output files
path = os.path.dirname(os.path.realpath(__file__)) + "\\"
wifi_results = open(path + "wifi_results.csv","w")
wifi_csv_header = ("LOCATION, TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LAPTOP MAC, PACKET LOSS, PING AVG\n")
wifi_results.write(wifi_csv_header)
ap_results = open(path + "ap_results.csv", "w")
ap_csv_header  = ("LOCATION, TIME, DATE, SSID, BSSID, SIGNAL, CHANNEL\n")
ap_results.write(ap_csv_header)

# Setup Mac to Name dictionary
# Check file exists, if not dont continue
if (os.path.isfile(path + 'mac2location.csv')): 
    # Open file and start reading
    mac2location = open(path + "mac2location.csv","r")
    mac2location_file = list(reader(mac2location))
    mac2location.close()
else:
    print("Cannot find file 'mac2location.csv' in the directory this script is running. No MAC translations will occur")

# Current Date/Time
def date_func():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return date

def time_func():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return time

# Location Details
def location_func():
    location = input("What is your current location? (Enter to exit) ")
    print(f"Location entered: {location}")
    return location

# Current IP Details
def ip_func():
    raw_ip = check_output("netsh interface ip show addresses Wi-Fi", shell=True).decode()
    for line in raw_ip.splitlines():
        if "Default Gateway" in line:
            gateway_ip = line.split()
            return gateway_ip[2]
    print(f"No gateway IP found")
    return 0

# Scan WiFi
def wifi_rescan():
    print("Scanning WiFi")
    winwifi.WinWiFi.scan()
    # wifi = pywifi.PyWiFi()
    # iface = wifi.interfaces()[0]
    # iface.scan()
    return

# Get current WiFi details
def wifi_func():
    raw_wifi = check_output("netsh wlan show interfaces", shell=True).decode()
    raw_wifi = raw_wifi.replace("(", "").replace(")", "").replace(",", "").replace(" : ", "")
    return raw_wifi

# Connectivity check to Gateway.
def ping_func(gateway_ip):
    print(f"Awaiting completion of ping test.")
    raw_ping = check_output("ping " + gateway_ip + " -n 3", shell=True).decode()
    raw_ping = raw_ping.replace("(", "").replace(")", "").replace(",", "").replace("=", "")
    print(f"Ping test complete.\n")
    return raw_ping

# Wifi around me
def apscan_func():
    raw_apscan = check_output("netsh wlan show network mode=bssid", shell=True).decode()
    raw_apscan = raw_apscan.replace("(", "").replace(")", "").replace(",", "").replace(": ", "")
    return raw_apscan

# Tries to match the MAC address against a physical location
def convert_mac(mac_address):
    # Declare some global shiz
    mac_match1 = []
    mac_match2 = []
    for mac2location_row in mac2location_file:
        # Return on an exact match
        if (mac_address.lower() in mac2location_row[1].lower()):
            return mac2location_row[0] + " (" + mac_address +")"
        # Keep track of 'close' matches
        if (mac_address[:-1].lower() in mac2location_row[1].lower()):
            #MAC missing 1 character matches, remember this 4 l8r
            mac_match1.append(mac2location_row[0])
        if (mac_address[:-2].lower() in mac2location_row[1].lower()):
            #MAC missing 2 character matches, remember this 4 l8r
            mac_match2.append(mac2location_row[0])
    if (len(mac_match1) == 1): return mac_match1[0] + "*" + " (" + mac_address +")"
    if (len(mac_match2) == 1): return mac_match2[0] + "**" + " (" + mac_address + ")"
    return mac_address

date = date_func()
time = time_func()    
print(f"The current date and time is {date} {time}")

#Wifi Testing Loop
test_loop = 1
while test_loop == 1:
    # Ojects
    location = location_func()
    if location == "":
        test_loop = 0
        continue
    gateway_ip = ip_func()
    wifi_rescan()
    raw_wifi = wifi_func()
    raw_apscan = apscan_func()
    raw_ping = ping_func(gateway_ip)
    date = date_func()
    time = time_func()
    apscan = raw_apscan.replace("BSSID", "#BSSID").split("\r\n\r\n")

    # Objectifing raw_wifi
    for line in raw_wifi.splitlines():
        if "SSID" in line and "BSSID" not in line:
            SSID = line.split()
        if "BSSID" in line:
            APMacAddress = line.split()
        if "Receive rate" in line:
            LaptopRX = line.split()
        if "Transmit rate" in line:
            LaptopTX = line.split()
        if "Signal" in line:
            LaptopSignal = line.split()
        if "Channel" in line:
            APChannel = line.split()
        if "Physical address" in line:
            LaptopMacAddress = line.split()

    # Objectifing raw_ping
    for line in raw_ping.splitlines():
        if "Packets" in line:
            PacketLoss = line.split()
        if "Average" in line:
            PingAvg = line.split()

    # Writing results to wifi_result.csv
    wifi_output = (f"{location}, {time}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, {LaptopRX[3]}, {LaptopTX[3]}, {LaptopSignal[1]}, {APChannel[1]}, {LaptopMacAddress[2]}, {PacketLoss[7]}, {PingAvg[5]}\n")
    wifi_results.write(wifi_output)

    # Objectifing apscan and writing results for ap_results.csv
    for line in raw_apscan.splitlines():
        if "visible" in line:
            ssid_count = line.split()
            ssid_count = int(ssid_count[2])

    ssid_loop = 1
    while ssid_loop <= ssid_count:
        bssid_count = apscan[ssid_loop].count("BSSID ")
        # print(f"The BSSID count for SSID {ssid_loop} is {bssid_count}")
        ssid_name = apscan[ssid_loop].splitlines()[0].replace("SSID", "").strip().split(" ")
        ssid_name.pop(0)
        ssid_name = " ".join(ssid_name)
        for bssid in apscan[ssid_loop].split("#"):
            bssid_lines = bssid.splitlines()
            if "Network type" in bssid_lines[1]: continue
            bssid_signal = bssid_lines[1].replace("Signal", "").strip()
            bssid_mac = bssid_lines[0].replace("BSSID", "").strip().split("                 ")[1]
            bssid_channel = bssid_lines[3].replace("Channel", "").strip()
            # print(f"{location}, {time}, {date}, {ssid_name}, {bssid_mac}, {bssid_signal}, {bssid_channel}\n")
            ap_output = (f"{location}, {time}, {date}, {ssid_name}, {convert_mac(bssid_mac)}, {bssid_signal}, {bssid_channel}\n")
            ap_results.write(ap_output)
        ssid_loop = ssid_loop + 1

    print("Enter in your next location.")

print("Test Completed\n")
ap_results.close()
wifi_results.close()
print(f'The WiFi results have been saved to "{path}wifi_results.csv", aswell as the AP scan results "{path}ap_results.csv".')
input("Click enter to exit")