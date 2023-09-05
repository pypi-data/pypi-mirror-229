pad # MySQL Connection Library

The Connection class provides a simple wrapper around `mysql.connector` to manage database connections. 
Below is a basic guide on how to use the class along with sample use cases for each function:

## Prerequisites

- Python 3.x
- mysql-connector-python: Install via pip using pip install mysql-connector-python
- .env file: This should contain your MySQL credentials. Example:

```
RDS_HOSTNAME=db.dvlp1.circ.zone
# Your database use without @circ.zone
RDS_USERNAME=mydbuser
# Your database password
RDS_PASSWORD=mysecretpassword
# Not mandatory
RDS_DATABASE=mydatabase
LOGZIO_TOKEN=cXNHuVkkffkilnkKzZlWExECRlSKqopE
```

## Usage

**Connection Class:**

```py
from circles_local_database_python.cursor import Cursor 
from circles_local_database_python.connection import Connection

# Initialization:
connection = Connection(database="my_database") # or provide host, user, password as arguments if different from .env values

# Connect to Database:
connection.connect()

# Create a Cursor for Database Connection: #these are examples of usage
cursor = connection.cursor()
cursor.execute("SELECT * FROM my_table")
results = cursor.fetchall()

or 

cursor = connection.cursor(params={"param_key": "param_value"})

# Execute a Query: #note this does not commit, only return the values
cursor.execute("INSERT INTO my_table (column1, column2) VALUES (%s, %s)", ("value1", "value2"))

#Commit a Query:
cursor.execute("INSERT INTO my_table (column1, column2) VALUES (%s, %s)", ("value1", "value2"))
connection.commit()

# Fetch All Rows:
cursor.execute("SELECT * FROM my_table")
rows = cursor.fetchall()

# Fetch One Row:
cursor.execute("SELECT * FROM my_table WHERE column_name='some_value'")
row = cursor.fetchone()

# Get Columns Description:
cursor.description()

# Get Last Inserted ID:
cursor.get_lastrowid()

# Close Connection:
connection.close()
