# wifi_tool.py

## What is it?

## To-Do

- [x]  Map Mode
- [x]  Test Mode
- [ ]  Combine Modes into one script
- [ ]  Linux Support

## Modes

**Map Mode** - Positionally grab currently connected BSSID information and all BSSIDs with-in the vicinity.

- Test the currently connected BSSID and output the following into a CSV file.

    ```python
    LOCATION, TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LAPTOP MAC, PACKET LOSS, PING AVG
    ```

- Map all the BSSID within the vicinity and output the following into a CSV file.

    ```python
    LOCATION, TIME, DATE, SSID, BSSID, SIGNAL, CHANNEL
    ```

**Test Mode** - Continuously output diagnostic information about currently connected BSSID.

- Continuously ping and grab the following data and output into a CSV

    ```python
    TIME, DATE, SSID, BSSID, LAPTOP RX (Mbps), LAPTOP TX (Mbps), SIGNAL, CHANNEL, LOCAL MAC, PACKET LOSS, AVG PING
    ```

## Mac2Location

## **Output Files**

The output files are date/time based, so a new one is created each run based on start time.

wifi_results.csv : The connected BSSID and the results at each position

ap_results.csv : BSSIDs with in the vicinity of the test location and their results

wifi_test.csv : Results of each individual test output to a new line.
