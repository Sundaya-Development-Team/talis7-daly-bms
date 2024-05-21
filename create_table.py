from database import Database
import argparse
import os 
from dotenv import load_dotenv

load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Manage database tables.')
parser.add_argument('operation', choices=[
                    'create', 'drop'], help='The operation to perform.')
parser.add_argument('--table', help='The name of the table to operate on.')
args = parser.parse_args()

# database connection
db = Database(
    db_name=os.getenv("db_name"),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    host=os.getenv("db_host"),
    port=os.getenv("db_port")
)

# Perform operation
if args.operation == 'create':
    db.create_table(
        table_name='loggers',
        columns='id SERIAL PRIMARY KEY, date VARCHAR, serial_number VARCHAR, total_voltage FLOAT, current FLOAT, soc_percent FLOAT, temperature INTEGER, cell VARCHAR, "createdAt" TIMESTAMP DEFAULT NOW(), "updatedAt" TIMESTAMP DEFAULT NOW()',
    )
elif args.operation == 'drop':
    db.drop_table(table_name=args.table_name)
