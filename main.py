import datetime
import time
import os
from database import Database
from python_daly_bms.dalybms import DalyBMS
from dotenv import load_dotenv

load_dotenv()

# database connection
db = Database(
    db_name=os.getenv("db_name"),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    host=os.getenv("db_host"),
    port=os.getenv("db_port")
)

# changing the port to the port of the BMS
PORT = 'COM6'

# serial number of the BMS
serial_number = "0003"

# initialize the BMS
bms = DalyBMS()

def connection():
    resp = bms.connect(PORT)
    return resp


def get_data():
    """
    read bms data
    """
    data = bms.get_all()
    return data


def store_data():
    """
    store data bms to database
    """
    while True:
        data = get_data()
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

        # store to database
        db.insert(
            table_name="loggers",
            columns="date, total_voltage, current, soc_percent, temperature, cell, serial_number",
            values=(new_data["date"], new_data["totalVoltage"], new_data["current"],
                    new_data["socPercent"], new_data["temperature"], new_data["cellVoltage"],
                    new_data["serialNumber"]),
        )

        time.sleep(0.5)


def main():
    resp = connection()
    if resp == None:
        store_data()
    else:
        print("Connection failed, please check the port using /dev/ttyUSB0 or COM")


if __name__ == '__main__':
    main()
