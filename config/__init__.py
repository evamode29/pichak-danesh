import pymysql

# cPanel shared hosting may not provide gcc to build mysqlclient.
# PyMySQL is pure Python and can be used through Django's MySQL backend.
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
