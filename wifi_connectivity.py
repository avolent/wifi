import datetime
import time
import os
from subprocess import check_output
from csv import reader
import colorama

colorama.init()

# Setup directory and log file.
path = os.path.dirname(os.path.realpath(__file__)) + "\\"
if (os.path.isfile(path + 'wifi_test_log.csv')): 
    # Open file and start reading
    print("wifi_test_log.csv file already exists, appending to the end.")
else:
    wifi_debug = open(path + "wifi_test_log.csv","w")
    wifi_csv_header = ("TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LOCAL MAC, PACKET LOSS, AVG PING\n")
    wifi_debug.write(wifi_csv_header)
    wifi_debug.close()
    print(f"Logfile created at {path}wifi_test_log.csv")

# Setup Mac to Name dictionary
# Check file exists, if not dont continue
if (os.path.isfile(path + 'mac2location.csv')): 
    # Open file and start reading
    mac2location = open(path + "mac2location.csv","r")
    mac2location_file = list(reader(mac2location))
    mac2location.close()
else:
    print(colorama.Fore.RED ,f"Cannot find file 'mac2location.csv' in the directory this script is running. No MAC translations will occur!\nPlease create a .CSV file in the following format\nAP1_Location,aa:bb:cc:dd:ee:ff\nAP2_Location,ff:ee:dd:cc:bb:aa\n")

# Current Date/Time
def date_func():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return date

def time_func():
    currenttime = datetime.datetime.now().strftime("%H:%M:%S")
    return currenttime

# Current IP Details
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

# Get current WiFi details
def wifi_func():
    raw_wifi = check_output("netsh wlan show interfaces", shell=True).decode()
    raw_wifi = raw_wifi.replace("(", "").replace(")", "").replace(",", "").replace(" : ", "")
    return raw_wifi

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

ping_count = ping_count_func()

# Test Loop
test_loop = 1
while test_loop == 1:
    wifi_debug = open(path + "wifi_test_log.csv","a")
    date = date_func()
    currenttime = time_func()
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
        print(colorama.Fore.GREEN ,f"{currenttime}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
    elif ping_colour <= 150:
        print(colorama.Fore.YELLOW ,f"{currenttime}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
    elif ping_colour > 150:
        print(colorama.Fore.RED ,f"{currenttime}, {date}, {SSID[1]}, {convert_mac(APMacAddress[1])}, TX/RX: {LaptopTX[3]}/{LaptopRX[3]}Mbps, SIGNAL: {LaptopSignal[1]}, CHANNEL: {APChannel[1]}, LOCAL MAC: {LaptopMacAddress[2]}, PACKET LOSS: {PacketLoss[7]}, AVG PING: {PingAvg[5]}")
    
    wifi_debug_output = (f"{currenttime},{date},{SSID[1]},{convert_mac(APMacAddress[1])},{LaptopRX[3]},{LaptopTX[3]},{LaptopSignal[1]},{APChannel[1]},{LaptopMacAddress[2]},{PacketLoss[7]},{PingAvg[5]}\n")
    wifi_debug.write(wifi_debug_output)
    wifi_debug.close