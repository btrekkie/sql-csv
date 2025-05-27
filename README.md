# Description
`sqlite-csv` is a Python program that presents a read-eval-print loop allowing
the user to connect to a SQLite database, execute SQL queries, and import and
export CSV files. One possible use case is to perform data processing on
spreadsheets using SQL code rather than spreadsheet formulas, which may be
easier or more convenient in some cases.

To execute the program, run `python3 /path/to/sql.py` from the command line.

# Features
* Execute SQL queries on a SQLite database in a read-eval-print loop.
* Import a CSV file as a SQL table. The column names are derived from the header
  row, and the values' datatypes are inferred.
* Export the results of a SQL query to a CSV file.
* CSV files and SQL result sets are streamed, rather than loading them all into
  memory at once. As a result, it is possible to import and export very large
  CSV files without running out of memory.
* No external dependencies.

# Limitations
* Configuration and options are limited (because I prioritized simplicity of
  implementation and use).
* Importing and exporting large CSV files is not particularly fast.

# Example
```
Enter "import", "export", or a SQL query.
> import
Enter a CSV file to import: ./countries.csv
Enter a SQL table name: countries
Imported 245 row(s).
Imported table "countries" with columns: country, latitude, longitude, name.
> SELECT name, country FROM countries WHERE latitude >= 0 ORDER BY name
| name                | country |
| Afghanistan         | AF      |
| Albania             | AL      |
| Algeria             | DZ      |
| Andorra             | AD      |
| Anguilla            | AI      |
| Antigua and Barbuda | AG      |
| Armenia             | AM      |
| Aruba               | AW      |
| Austria             | AT      |
| Azerbaijan          | AZ      |
| Bahamas             | BS      |
| Bahrain             | BH      |
| Bangladesh          | BD      |
| Barbados            | BB      |
| Belarus             | BY      |
| Belgium             | BE      |
| Belize              | BZ      |
| Benin               | BJ      |
| Bermuda             | BM      |
| Bhutan              | BT      |
Output first 20 rows.
> export
Enter a CSV file to store the results of the most recent SQL query in: ./northern_hemisphere_countries.csv
Exported 181 row(s).
```
