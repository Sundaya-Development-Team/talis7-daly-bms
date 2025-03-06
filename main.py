import datetime
import time
import os
import signal
import sys
from database import Database
from python_daly_bms.dalybms import DalyBMS
from dotenv import load_dotenv

load_dotenv()

# Global flag for graceful exit
running = True

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    global running
    print("\nStopping data collection...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# database connection
try:
    db = Database(
        db_name=os.getenv("db_name"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        host=os.getenv("db_host"),
        port=os.getenv("db_port")
    )
except Exception as e:
    print(f"Database connection error: {e}")
    sys.exit(1)

# Input data
port = input("Enter the port (example: /dev/ttyUSB0 or COM10): ")
serial_number = input("Enter the serial number (example: AO2912182192): ")
status = input("Enter the status (charge or discharge): ").lower()

# initialize the BMS
bms = DalyBMS()

def connection():
    """
    Connect to the BMS
    Returns True if connection is successful, False otherwise
    """
    try:
        resp = bms.connect(port)
        return resp is None  # None means successful connection
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def get_data():
    """
    Read BMS data
    """
    try:
        data = bms.get_all()
        return data
    except Exception as e:
        print(f"Error reading BMS data: {e}")
        return None

def store_data():
    """
    Store data BMS to database
    """
    global running
    
    while running:
        try:
            data = get_data()
            if not data:
                print("Failed to get data from BMS. Retrying in 5 seconds...")
                time.sleep(5)
                continue
                
            # collect cell voltage data to list
            cell = []
            for i in range(1, len(data['cell_voltages'])+1):
                cell.append(data['cell_voltages'][i])

            new_data = {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "serialNumber": serial_number,
                "totalVoltage": data['soc']['total_voltage'],
                "current": data['soc']['current'],
                "socPercent": data['soc']['soc_percent'],
                "temperature": data['temperatures'][1],
                "cellVoltage": cell
            }
            print(new_data)
            
            # update to table realtime
            # check if serial number exists in table realtime
            isExist = db.select(
                table_name="realtime",
                columns="serial_number",
                condition=f"serial_number = '{new_data['serialNumber']}'"
            )
            
            if isExist:
                # Fix the SQL statement format and properly handle quotes
                db.update(
                    table_name="realtime",
                    set=f"date = '{new_data['date']}', serial_number = '{new_data['serialNumber']}', port = '{port}', status = '{status}', total_voltage = {new_data['totalVoltage']}, current = {new_data['current']}, soc_percent = {new_data['socPercent']}, temperature = {new_data['temperature']}, cell = '{str(new_data['cellVoltage'])}'",
                    condition=f"serial_number = '{new_data['serialNumber']}'"
                )
            else:
                db.insert(
                    table_name="realtime",
                    columns="date, serial_number, port, status, total_voltage, current, soc_percent, temperature, cell",
                    values=(new_data["date"], new_data["serialNumber"], port, status, new_data["totalVoltage"], new_data["current"], new_data["socPercent"], new_data["temperature"], str(new_data["cellVoltage"])),
                )
            
            # store to database
            db.insert(
                table_name="loggers",
                columns="date, total_voltage, current, soc_percent, temperature, cell, serial_number",
                values=(new_data["date"], new_data["totalVoltage"], new_data["current"],
                        new_data["socPercent"], new_data["temperature"], str(new_data["cellVoltage"]),
                        new_data["serialNumber"]),
            )

            time.sleep(0.5)
        
        except Exception as e:
            print(f"Error in data storage: {e}")
            time.sleep(5)  # Wait before retrying

def cleanup():
    """Close resources"""
    try:
        bms.disconnect()
        print("BMS disconnected successfully")
    except:
        pass

def main():
    try:
        connected = connection()
        if connected:
            print("Connected to BMS successfully!")
            store_data()
        else:
            print("Connection failed, please check the port using /dev/ttyUSB0 or COM")
    finally:
        cleanup()
        print("Program terminated")

if __name__ == '__main__':
    main()
