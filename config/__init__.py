import pymysql

# Lets Django's MySQL backend (which expects mysqlclient) work with the
# pure-Python PyMySQL driver instead — no system-level MySQL client
# libraries needed to install this project.
pymysql.install_as_MySQLdb()
