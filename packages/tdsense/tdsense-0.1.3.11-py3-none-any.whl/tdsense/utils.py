# This function creates a table based on a given query.
def create_table(query, table_name, schema_name):
    """
    Create a table based on a given query.

    Parameters:
    - query: SQL query for creating the table.
    - table_name: Name of the table to be created.
    - schema_name: Name of the schema where the table will be created.

    Returns:
    - query: SQL query for creating the table.

    Note:
    - The function assumes the availability of the specified schema.
    """

    # Generate the SQL query for creating the table
    query = f"""
    CREATE TABLE {schema_name}.{table_name} AS 
    (
        {query}
    ) WITH DATA
    --PRIMARY INDEX (CURVE_ID_1, CURVE_ID_2)
    NO PRIMARY INDEX
    """

    # Return the SQL query for creating the table
    return query

# This function generates an INSERT INTO query for inserting data into a table.
def insert_into(query, table_name, schema_name):
    """
    Generate an INSERT INTO query for inserting data into a table.

    Parameters:
    - query: SQL query for the data to be inserted.
    - table_name: Name of the table to insert the data into.
    - schema_name: Name of the schema where the table is located.

    Returns:
    - query: SQL query for inserting data into the table.

    Note:
    - The function assumes the availability of the specified schema and table.
    """

    # Generate the SQL query for inserting data into the table
    query = f"""
    INSERT INTO {schema_name}.{table_name}  
    {query}
    """

    # Return the SQL query for inserting data into the table
    return query

from packaging import version
def is_version_greater_than(tested_version, base_version="17.20.00.03"):
    """
    Check if the tested version is greater than the base version.

    Args:
        tested_version (str): Version number to be tested.
        base_version (str, optional): Base version number to compare. Defaults to "17.20.00.03".

    Returns:
        bool: True if tested version is greater, False otherwise.
    """
    return version.parse(tested_version) > version.parse(base_version)
def execute_query_wrapper(f):
    """
    Decorator to execute a query. It wraps around the function and adds exception handling.

    Args:
        f (function): Function to be decorated.

    Returns:
        function: Decorated function.
    """
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        query = f(*args, **kwargs)
        if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
            if type(query) == list:
                for q in query:
                    try:
                        tdml.execute_sql(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.execute_sql(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        else:
            if type(query) == list:
                for q in query:
                    try:
                        tdml.get_context().execute(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.get_context().execute(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        return
    return wrapped_f


def execute_query(query):
    if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
        if type(query) == list:
            for q in query:
                try:
                    tdml.execute_sql(q)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                return tdml.execute_sql(query)
            except Exception as e:
                print(str(e).split('\n')[0])
                print(query)
    else:
        if type(query) == list:
            for q in query:
                try:
                    tdml.get_context().execute(q)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                return tdml.get_context().execute(query)
            except Exception as e:
                print(str(e).split('\n')[0])
                print(query)
    return