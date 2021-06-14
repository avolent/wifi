import datetime
import time
import os
from subprocess import check_output
from csv import reader
import colorama
import winwifi

#Global variable setup
path = os.path.dirname(os.path.realpath(__file__)) + "\\"
file = 0

# Setup Mac to Name dictionary
# Check file exists, if not dont continue
if (os.path.isfile(path + 'mac2location.csv')): 
    # Open file and start reading
    mac2location = open(path + "mac2location.csv","r")
    mac2location_file = list(reader(mac2location))
    mac2location.close()
else:
    print(colorama.Fore.RED ,f"Cannot find file 'mac2location.csv' in the directory this script is running. No MAC translations will occur!\nPlease create a .CSV file in the following format\nAP1_Location,aa:bb:cc:dd:ee:ff\nAP2_Location,ff:ee:dd:cc:bb:aa\n")

# Functions Below
# Current Date/Time
def date_func():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return date
def time_func():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return time
def file_time_func():
    time = datetime.datetime.now().strftime("%H-%M-%S")
    return time
# Location Details
def location_func():
    location = input("What is your current location? (Enter to exit) ")
    return location
#Get Current IP Details
def ip_func():
    for retry in range(10):
        try:
            raw_ip = check_output("netsh interface ip show addresses Wi-Fi", shell=True).decode()
            for line in raw_ip.splitlines():
                if "Default Gateway" in line:
                    gateway_ip = line.split()
                    return gateway_ip[2]
        except:
            print(colorama.Fore.RED ,f"No gateway IP found")
            time.sleep(5)
            continue
        break
# Scan WiFi
def wifi_rescan():
    print("Scanning WiFi")
    winwifi.WinWiFi.scan()
    return
# Get current WiFi details
def wifi_func():
    raw_wifi = check_output("netsh wlan show interfaces", shell=True).decode()
    raw_wifi = raw_wifi.replace("(", "").replace(")", "").replace(",", "").replace(" : ", "")
    return raw_wifi
# Wifi around me
def apscan_func():
    raw_apscan = check_output("netsh wlan show network mode=bssid", shell=True).decode()
    raw_apscan = raw_apscan.replace("(", "").replace(")", "").replace(",", "").replace(": ", "")
    return raw_apscan
# Connectivity check to Gateway.
def ping_func(gateway_ip, ping_count):
    for retry in range(10):
        try:
            # print(f"Awaiting completion of ping test.")
            raw_ping = check_output("ping " + gateway_ip + " -n " + ping_count, shell=True).decode()
            raw_ping = raw_ping.replace("(", "").replace(")", "").replace(",", "").replace("=", "")
            # print(f"Ping test complete.\n")
            return raw_ping
        except:
            print(colorama.Fore.RED ,f"Unable to ping gateway ({gateway_ip}), check WiFi connection to access point.")
            gateway_ip = ip_func()
            time.sleep(5)
        continue
    print(colorama.Fore.RED ,f"\nUnable to ping gateway, exiting!\n")
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
# Ask user the ping count they would like to average
def ping_count_func():
    ping_count = input("What number of echo requests would you like to send during the ping (default 3)? ")
    if ping_count == "":
        ping_count = "3"
    return ping_count

# Below functions are the two tests
# Function for the Map Test.
def map_func():
    date = date_func()
    file_time = file_time_func()
    wifi_results_file = f"{path}wifi_results_{date}_{file_time}.csv"
    wifi_results = open(wifi_results_file, "w")
    wifi_results_header = ("LOCATION, TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LAPTOP MAC, PACKET LOSS, PING AVG\n") 
    wifi_results.write(wifi_results_header)
    wifi_results.close()
    ap_results_file = f"{path}ap_results_{date}_{file_time}.csv"
    ap_results = open(ap_results_file, "w")
    ap_results_header = ("LOCATION, TIME, DATE, SSID, BSSID, SIGNAL, CHANNEL\n") 
    ap_results.write(ap_results_header)
    ap_results.close()
    ping_count = ping_count_func()
    test_loop = 1
    while test_loop == 1:
        # Ojects
        location = location_func()
        if location == "":
            test_loop = 0
            print("Exiting")
            continue
        print(f"Location entered: {location}")
        gateway_ip = ip_func()
        wifi_rescan()
        raw_wifi = wifi_func()
        raw_apscan = apscan_func()
        print("Pinging gateway!")
        raw_ping = ping_func(gateway_ip, ping_count)
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
        wifi_results = open(wifi_results_file, "a")
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
                ap_results = open(ap_results_file, "a")
                ap_results.write(ap_output)
            ssid_loop = ssid_loop + 1

        print("Move to your next location.")
    
# Function for the WiFi Test.
def test_func():
    date = date_func()
    file_time = file_time_func()
    wifi_test_file = f"{path}wifi_test_{date}_{file_time}.csv"
    wifi_test = open(wifi_test_file, "w")
    wifi_test_header = ("TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LOCAL MAC, PACKET LOSS, AVG PING\n") 
    wifi_test.write(wifi_test_header)
    wifi_test.close()
    ping_count = ping_count_func()
    test_loop = 1
    while test_loop == 1:
        date = date_func()
        current_time = time_func()
        gateway_ip = ip_func()
        raw_ping = ping_func(gateway_ip, ping_count)
        raw_wifi = wifi_func()
        
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

        ping_colour = int(PingAvg[5].replace("ms", ""))
        if ping_colour <= 50:
            print(colorama.Fore.GREEN ,f"{current_time}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
        elif ping_colour <= 150:
            print(colorama.Fore.YELLOW ,f"{current_time}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
        elif ping_colour > 150:
            print(colorama.Fore.RED ,f"{current_time}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
        
        wifi_test_output = (f"{current_time},{date},{SSID[1]},{convert_mac(APMacAddress[1])},{LaptopRX[3]},{LaptopTX[3]},{LaptopSignal[1]},{APChannel[1]},{LaptopMacAddress[2]},{PacketLoss[7]},{PingAvg[5]}\n")
        wifi_test = open(wifi_test_file, "a")
        wifi_test.write(wifi_test_output)
        wifi_test.close


test = input("Which test do you want run (map/test)? ")

if test == "map":
    print("Commencing WiFi Mapping\n")
    map_func()
elif test == "test":
    print("Commencing WiFi Testing\n")
    test_func()