import sqlite3
import functools

# database name
db_name = ""


# connect to database
def connection(db):
    """
    Establish a connection to a SQLite database.

    This function takes the name of the database file as input and connects to it.
    If the database file doesn't exist, it returns None.

    Args:
        db (str): The name of the database file.

    Returns:
        sqlite3.Connection or None: The database connection object if successful, or None if the database file doesn't exist.

    Example:
        db_conn = connection("my_database.db")
        if db_conn is not None:
            # Use the database connection for queries and operations
        else:
            print("Database file does not exist.")
    """
    # Declare the variable before the `if` statement
    db_conn = None

    if db is None:
        print(f"No database file '{db}' found.")
    else:
        db_conn = db  # "{}.db".format(db)
        # print(f"Connected to '{db_conn}' successfully...")

    db_connection = sqlite3.connect(db_conn)

    return db_connection


# connect database file
def db_connect(func):
    """
        Decorator function for connecting to a SQLite database before executing the wrapped function.

        This decorator establishes a connection to a SQLite database and creates a cursor object.
        It then executes the wrapped function, passing the database connection and cursor as arguments.
        If any database-related errors occur, they are caught and printed, and the function continues.

        Args:
            func (callable): The function to be wrapped.

        Returns:
            callable: The wrapped function.

        Example:
            @db_connect
            def my_function(conn, *args, **kwargs):
                # Your function code here
        """
    # inner function
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            conn.execute("SELECT name FROM sqlite_temp_master WHERE type='table';")
            # Enable FOREIGN KEY constraints
            conn.excecute("PRAGMA foreign_keys = ON;")

        except (AttributeError, sqlite3.ProgrammingError):
            conn = connection(db_name)

        return func(conn, *args, **kwargs)

    return wrapper


@db_connect
def generate_tables(conn):
    query = """
        BEGIN;
        CREATE TABLE IF NOT EXISTS meals(
        meal_id INTEGER PRIMARY KEY,
        meal_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS ingredients(
        ingredient_id INTEGER PRIMARY KEY,
        ingredient_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS measures(
        measure_id INTEGER PRIMARY KEY,
        measure_name TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS recipes(
        recipe_id INTEGER PRIMARY KEY,
        recipe_name TEXT NOT NULL,
        recipe_description TEXT
        );

        CREATE TABLE IF NOT EXISTS serve(
        serve_id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER NOT NULL,
        meal_id INTEGER NOT NULL,
        --foreign key for recipes
        CONSTRAINT fk_recipe FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
        --foreign key for meals
        CONSTRAINT fk_meal FOREIGN KEY(meal_id) REFERENCES meals(meal_id)
        );

        CREATE TABLE IF NOT EXISTS quantity(
        quantity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        measure_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        --foreign key for meal
        CONSTRAINT fk_measure FOREIGN KEY(measure_id) REFERENCES measures (measure_id),
        --foreign key for ingredient
        CONSTRAINT fk_ingredient FOREIGN KEY(ingredient_id) REFERENCES ingredients (ingredient_id),
        --foreign key for recipe
        CONSTRAINT fk_recipe_qt FOREIGN KEY(recipe_id) REFERENCES recipes (recipe_id)
        );

        COMMIT;
    """

    with conn:
        curs = conn.cursor()
        curs.executescript(query)


# truncate tables in db
def truncate_tables(conn):
    """
        Truncate (delete all records from) specified tables in a SQLite database.

        Args:
            conn (sqlite3.Connection): The database connection.

        Note:
            This function deletes all records from the specified tables but keeps the table structures intact.
            It can be used to reset or clear the data in the specified tables while preserving the table schema.

        Example:
            truncate_tables(connection)
        """
    tables = ["meals", "ingredients", "measures"]

    with conn:
        cursor = conn.cursor()
        for table in tables:
            query = f"DELETE FROM {table};"
            cursor.execute(query)
    conn.commit()


def attribute_conf(table_name):
    """
    Map a table name to its corresponding attribute column.

    This function takes a table name as input and returns the corresponding
    attribute column name based on a predefined mapping of table names to
    attribute columns.

    :param table_name: The name of the table for which the attribute column is needed.
    :type table_name: str
    :return: The name of the corresponding attribute column.
    :rtype: str or None
    """
    # map table_name to corresponding attribute
    attribute_columns = {
        "meals": "meal_name",
        "ingredients": "ingredient_name",
        "measures": "measure_name",
        "recipes": "recipe_name"
    }
    attribute_column = attribute_columns.get(table_name)
    return attribute_column


@db_connect
def insert_db(conn, *args):
    """
        Insert a new record into a SQLite database table.

        Args:
            conn (sqlite3.Connection): The database connection.
            table_name (str): The name of the table to insert the record into.
            attribute_value (str): The attribute value to insert into the specified table.

        Raises:
            ValueError: If the number of arguments is not 2 or if the table name is unsupported.

        Note:
            The function uses the "INSERT INTO" SQL statement to add a new record to the specified table.
            It assumes that the table structure and relationships are properly set up.

        Example:
            insert_db(connection, "meals", "breakfast")
        """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 2 arguments: \
                         table_name, attribute_value")

    # assign args to variables
    table_name, attribute_value = args

    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = f"INSERT INTO ({attribute_column}) VALUES (:value);"
    # print("query:", query)
    # print("attribute value: ", attribute_value, " ", type(attribute_value))
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value": attribute_value})

    conn.commit()


@db_connect
def insert_to_recipe(conn, *args):
    """
        Insert a new recipe into the 'recipes' table.

        Args:
            conn (sqlite3.Connection): The database connection.
            recipe_name (str): The name of the recipe.
            recipe_description (str): The description of the recipe.

        Raises:
            ValueError: If the number of arguments is not 2.

        Note:
            The function uses the "INSERT INTO" SQL statement to add a new recipe to the 'recipes' table.
            It assumes that the 'recipes' table structure and relationships are properly set up.

        Example:
            insert_to_recipe(connection, "Pancakes", "Delicious breakfast pancakes with syrup.")
        """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 2 arguments: \
                          recipe_name and recipe_description")

    # assign args to variables
    recipe_name, recipe_desc = args

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = f"INSERT INTO recipes([recipe_name], [recipe_description]) VALUES (:value1, :value2);"
    # print("query:", query)
    # print("Name: ", recipe_name, " Description: ", recipe_desc)
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value1": recipe_name, "value2": recipe_desc})

    conn.commit()


@db_connect
def insert_to_serve(conn, *args):
    """
        Insert a recipe-to-meal association into the 'serve' table.

        Args:
            conn (sqlite3.Connection): The database connection.
            recipe_id (int): The ID of the recipe to associate.
            meal_id (int): The ID of the meal to associate.

        Raises:
            ValueError: If the number of arguments is not 2.

        Note:
            The function uses the "INSERT INTO" SQL statement to create an association between a recipe and a meal
            in the 'serve' table. It assumes that the 'serve' table structure and relationships are properly set up.

        Example:
            insert_to_serve(connection, 1, 3)
        """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 2 arguments: \
                          recipe_id and meal_id")

    # assign args to variables
    recipe_id, meal_id = args

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = f"INSERT INTO serve([recipe_id], [meal_id]) VALUES (:value1, :value2);"
    # print("Serve query:", query)
    # print("Recipe: ", recipe_id, " Meal: ", meal_id)
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value1": recipe_id, "value2": meal_id})

    conn.commit()


@db_connect
def insert_ingredient_measure(conn, *args):
    """
        Insert an ingredient or measure into the specified table.

        Args:
            conn (sqlite3.Connection): The database connection.
            table_name (str): The name of the table to insert data into (e.g., 'ingredients' or 'measures').
            attribute_value (str): The value of the ingredient or measure.

        Raises:
            ValueError: If the number of arguments is not 2 or if the provided table_name is unsupported.

        Note:
            The function uses the "INSERT INTO" SQL statement to add the ingredient or measure to the table.
            It assumes that the table structure and relationships are properly set up.

        Example:
            insert_ingredient_measure(connection, 'ingredients', 'strawberry')
        """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 2 arguments: \
                          table_name and ingredient_name")

    # assign args to variables
    table_name, attribute_value = args

    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = f"INSERT INTO {table_name}({attribute_column}) VALUES (:value);"
    # print("Serve query:", query)
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value": attribute_value})

    conn.commit()


@db_connect
def insert_to_quantity(conn, *args):
    """
        Insert quantity information into the specified table.

        Args:
            conn (sqlite3.Connection): The database connection.
            table_name (str): The name of the table to insert data into.
            quantity (int): The quantity value.
            recipe_id (int): The recipe ID.
            measure_id (int): The measure ID.
            ingredient_id (int): The ingredient ID.

        Raises:
            ValueError: If the number of arguments is not 5.

        Note:
            The function uses the "INSERT INTO" SQL statement to add quantity information to the table.
            It assumes that the table structure and relationships are properly set up.

        Example:
            insert_to_quantity(connection, 'quantity', 5, 1, 1, 2)
        """
    # ensure there are exactly three args
    if len(args) != 5:
        raise ValueError("Function requires exactly 5 arguments: \
                          table_name, quantity, recipe_id, meal_id, ingredient_id")

    # assign args to variables
    table_name, quantity, recipe_id, measure_id, ingredient_id = args

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = (f"INSERT INTO {table_name}(quantity, [recipe_id], "
             f"[measure_id], [ingredient_id]) VALUES (:value1, :value2, "
             f":value3, :value4);")
    # print("SERVE: ")
    # print("Recipe id: ", recipe_id, "Quantity id:", quantity, " Measure id: ", measure_id,
    #      " Ingredient id: ", ingredient_id)
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value1": quantity, "value2": recipe_id,
                             "value3": measure_id, "value4": ingredient_id})

    conn.commit()


@db_connect
def insert_many_db(conn, *args):
    """
    Insert a new record into a SQLite database table.

    This function performs an SQL INSERT operation on the specified table,
     adding a new record with the specified attribute and value.

    :param conn: A SQLite database connection.
    :param args: Positional arguments representing the table name,
    :and attribute value for the new record.
    :return: None
    """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 2 arguments: \
                         table_name, attribute_value")

    # assign args to variables
    table_name, attribute_values = args

    # get attribute name
    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    # Use INSERT OR REPLACE to insert or update based on conflicts
    query = f"INSERT INTO {table_name} ({attribute_column}) VALUES (:value);"
    # print("query:", query)
    # print("attribute value: ", attribute_values, " ", type(attribute_values))
    with conn:
        curs = conn.cursor()
        # Use executemany to insert multiple rows
        curs.executemany(query, [{"value": value} for value in attribute_values])

    conn.commit()


@db_connect
def db_update(conn, *args):
    """
    Update a record in a SQLite database table.

    This function performs an SQL UPDATE operation on the specified table, setting a specific attribute to a new value.

    :param conn: A SQLite database connection.
    :param args: Positional arguments representing the table name, attribute to update, and the new attribute value.
    :return: None
    """
    # ensure there are exactly three args
    if len(args) != 3:
        raise ValueError("Function requires exactly 3 arguments: \
                         table_name, attribute, and attribute_value")

    # assign args to variables
    table_name, attribute_value = args

    # get attribute name
    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    query = f"UPDATE {table_name} SET {attribute_column} = :value;"
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value": attribute_value})

    conn.commit()


@db_connect
def db_remove(conn, *args):
    """
    Remove records from a SQLite database table based on a specified
    attribute value.

    This function performs an SQL DELETE operation on the specified table,
     removing records where the specified attribute matches a given value.

    :param conn: A SQLite database connection.
    :param args: Positional arguments representing the table name,
    attribute to match for deletion, and the attribute value to match.
    :return: None
    """
    # ensure there are exactly three args
    if len(args) != 3:
        raise ValueError("Function requires exactly 3 arguments: \
                         table_name, attribute, and attribute_value")

    # assign args to variables
    table_name, attribute_value = args

    # get attribute name
    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    query = f"DELETE FROM {table_name} WHERE {attribute_column} = :value;"
    with conn:
        curs = conn.cursor()
        curs.execute(query, {"value": attribute_value})

    conn.commit()


@db_connect
def select_db(conn, *args):
    """
    Retrieve a record from a SQLite database table based on a specified
    attribute value.

    This function performs an SQL SELECT operation on the specified table,
     retrieving a record where the specified attribute matches a given value.

    :param conn: A SQLite database connection.
    :param args: Positional arguments representing the table name,
    attribute name, and attribute value for selection.
    :return: A single row resulting from the query, or None if no match
    is found.
    """
    # ensure there are exactly three args
    if len(args) != 2:
        raise ValueError("Function requires exactly 3 arguments: \
                         table_name, attribute, and attribute_value")

    # assign args to variables
    table_name, attribute_value = args

    # get attribute name
    attribute_column = attribute_conf(table_name)
    if attribute_column is None:
        raise ValueError(f"Unsupported table name: {table_name}")

    query = f"SELECT * FROM {table_name} WHERE {attribute_column} = :value;"
    # print("Measure values in query function: ", table_name, " ", attribute_value)

    curs = conn.cursor()
    curs.execute(query, {"value": attribute_value})

    result = curs.fetchone()

    conn.close()

    return result


@db_connect
def select_all_db(conn, *args):
    """
    Retrieve all records from a SQLite database table based on a specified
    table name.

    :param conn: A SQLite database connection.
    :param args: Positional argument representing the table name
    :return: A multiple rows resulting from the query, or None if no match
    is found.
    """
    # ensure there are exactly three args
    if len(args) != 1:
        raise ValueError("Function requires exactly 1 argument1: \
                         table_name")

    # assign args to variables
    table_name = args
    # print(" TABLE NAME: ", table_name[0])
    query = f"SELECT * FROM {table_name[0]};"
    curs = conn.cursor()
    curs.execute(query)

    result = curs.fetchall()

    conn.close()

    return result


@db_connect
def find_recipes(conn, *args):
    """
        Retrieve recipe names based on specified ingredients and meals.

        Args:
            conn (sqlite3.Connection): The database connection.
            *args: Variable-length arguments, where the first argument is
                   a list of ingredients and the second argument is a list of meals.

        Returns:
            str: A comma-separated string of recipe names that match the criteria.
        """
    ingredients, meals = args

    if len(ingredients) == 1:
        query = """
               SELECT r.recipe_name
               FROM recipes r
               JOIN quantity q ON r.recipe_id = q.recipe_id
               JOIN ingredients i ON q.ingredient_id = i.ingredient_id
               JOIN serve s ON r.recipe_id = s.recipe_id
               JOIN meals m ON s.meal_id = m.meal_id
               WHERE (i.ingredient_name = 'cacao')
               AND (m.meal_name IN ({}))
               GROUP BY m.meal_name
               ;
               """.format(
            ",".join([f"'{meal}'" for meal in meals]))
    else:
        query = """
           SELECT r.recipe_name
           FROM recipes r
           JOIN quantity q ON r.recipe_id = q.recipe_id
           JOIN ingredients i ON q.ingredient_id = i.ingredient_id
           JOIN serve s ON r.recipe_id = s.recipe_id
           JOIN meals m ON s.meal_id = m.meal_id
           WHERE ({})
           AND (m.meal_name IN ({}))
           GROUP BY r.recipe_name
           HAVING COUNT(DISTINCT i.ingredient_name) = {}
           ;
           """.format(
            " OR ".join([f"i.ingredient_name ='{ingredient}'" for ingredient in ingredients]),
            ",".join([f"'{meal}'" for meal in meals]),
            len(ingredients))

    curs = conn.cursor()
    curs.execute(query)
    result = curs.fetchall()

    # Extract recipe names from the result and join them with a comma
    recipe_names = ", ".join(recipe[0] for recipe in result)

    conn.close()

    return recipe_names
