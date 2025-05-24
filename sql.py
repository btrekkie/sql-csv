#!/usr/bin/env python3
# Runs a read-eval-print loop for executing SQLite queries using the database
# file ./sqlite.db, with support for importing and exporting CSV files.
import csv
import itertools
import os
import re
import sqlite3

try:
    import readline  # noqa
except ImportError:
    pass


def to_column_names(row):
    """Return SQL column names for importing a CSV file.

    Arguments:
        row (list[str]): The CSV file's header row. This may not contain
            any empty strings.

    Returns:
        list[str]: The column names. This is parallel to ``row``.
    """
    column_names = []
    column_name_set = set()
    for str_ in row:
        str_ = re.sub(r'[^a-z0-9_]', '_', str_.lower())
        str_ = re.sub(r'(?<=_)_+', '', str_)
        if str_ in column_name_set:
            suffix = 2
            while f'{str_}{suffix}' in column_name_set:
                suffix += 1
            str_ = f'{str_}{suffix}'
        column_names.append(str_)
        column_name_set.add(str_)
    return column_names


def to_db_value(str_):
    """Return the SQLite value for the specified CSV cell string."""
    if str_ == '':
        return None
    if str_[0] in '$\u20ac\xa5\xa3':
        str_without_currency = str_[1:]
    else:
        str_without_currency = str_

    try:
        value = int(str_without_currency)
        if -2 ** 63 <= value < 2 ** 63:
            return value
        else:
            return float(value)
    except ValueError:
        pass

    try:
        return float(str_without_currency)
    except ValueError:
        return str_


def import_(connection):
    """Execute an "import" command.

    Arguments:
        connection (Connection): The SQLite connection to use.
    """
    filename = input('Enter a CSV file to import: ')
    with open(filename, encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        header_row = next(reader)
        if '' in header_row:
            raise ValueError(
                f'There is no header in row 1, column '
                f'{header_row.index("") + 1}')
        column_names = to_column_names(header_row)

        table_name = input('Enter a SQL table name: ')
        if '"' in table_name:
            raise ValueError(
                'The table name may not contain a quotation mark. Your entry '
                'will automatically be enclosed in quotation marks, so it '
                'should be an ordinary string rather than a quoted '
                'identifier.')
        column_names_sql = f"""("{'", "'.join(column_names)}")"""
        connection.execute(f'CREATE TABLE "{table_name}" {column_names_sql};')
        connection.commit()

        count = 0
        rows = list(itertools.islice(reader, 10000))
        while rows:
            if count > 0:
                print(f'Imported {count} rows...')
            count += len(rows)

            values = []
            for row in rows:
                values.append([to_db_value(str_) for str_ in row])
            connection.executemany(
                f'INSERT INTO "{table_name}" {column_names_sql} '
                f'VALUES ({", ".join(["?"] * len(column_names))});',
                values)
            connection.commit()
            rows = list(itertools.islice(reader, 10000))
        print(f'Imported {count} row(s).')
        print(
            f'Imported table "{table_name}" with columns: '
            f'{", ".join(column_names)}.')


def export(query, connection):
    """Execute an "export" command.

    Arguments:
        query (str): The SQL query string whose results we should
            export.
        connection (Connection): The SQLite connection to use.
    """
    filename = input(
        'Enter a CSV file to store the results of the most recent SQL query '
        'in: ')
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            header = [column[0] for column in cursor.description]
            writer.writerow(header)

            for index, row in enumerate(cursor):
                if index % 10000 == 0 and index > 0:
                    print(f'Exported {index} rows...')
                writer.writerow(row)
            print(f'Exported {index + 1} row(s).')
    finally:
        cursor.close()


def print_table(table):
    """Print the specified table to standard output.

    Arguments:
        table (list[tuple]): The table. Each value ``value`` in
            ``table`` is converted to a string using ``str(value)``.
    """
    if not table:
        return
    widths = [0] * len(table[0])
    for row in table:
        for index, value in enumerate(row):
            if len(str(value)) > widths[index]:
                widths[index] = len(str(value))

    for row in table:
        for value, width in zip(row, widths):
            print(f'| {str(value)}{" " * (width - len(str(value)))} ', end='')
        print('|')


def execute_sql(query, connection):
    """Execute the specified SQL query.

    Arguments:
        query (str): The query.
        connection (Connection): The SQLite connection to use.

    Returns:
        Whether the query was a SELECT statement.

    Raises:
        OperationalError: If there was an error executing the query.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        rows = []
        for index in range(20):
            row = cursor.fetchone()
            if row is None:
                break
            values = []
            for value in row:
                if value is not None:
                    values.append(value)
                else:
                    values.append('NULL')
            rows.append(values)

        if cursor.description is not None:
            header = tuple(column[0] for column in cursor.description)
            print_table([header] + rows)
            if rows:
                if cursor.fetchone() is not None:
                    print('Output first 20 rows.')
                else:
                    print(f'Output all {len(rows)} row(s).')
            else:
                print('Query returned zero rows.')
            return True
        else:
            if cursor.rowcount >= 0:
                print(f'Modified {cursor.rowcount} row(s).')
            else:
                print('Done.')
            return False
    finally:
        cursor.close()


def run_repl():
    """Run a read-eval-print loop for executing SQLite queries.

    Run a read-eval-print loop for executing SQLite queries using the
    database file ``./sqlite.db``, with support for importing and
    exporting CSV files.
    """
    connection = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), 'sqlite.db'))
    try:
        last_query = None
        print('Enter "import", "export", or a SQL query.')
        while True:
            query = input('> ')
            try:
                if query == 'import':
                    import_(connection)
                elif query == 'export':
                    if last_query is not None:
                        export(last_query, connection)
                    else:
                        print('You must enter a SQL query before exporting.')
                elif execute_sql(query, connection):
                    last_query = query
            except Exception as exception:
                print(f'Error: {exception}')
    finally:
        connection.close()


if __name__ == '__main__':
    run_repl()
