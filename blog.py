import database as db
import argparse
import sys


# parse arguments
def parse_arguments():
    """
        Parse command-line arguments for the Food Blog Backend CLI application.

        Returns:
            argparse.Namespace: A namespace containing the parsed arguments.
        """
    parser = argparse.ArgumentParser(description="Food Blog Backend CLI application")

    # define a required argument for database file
    parser.add_argument("database_file", help="Database Filename (food_blog.db)")

    # define optional arguments
    parser.add_argument("--ingredients", help="List of ingredients (comma-separated)")
    parser.add_argument("--meals", help="List of meals (comma-separated)")

    args = parser.parse_args()

    # split the comma-seperated values into list
    if args.ingredients:
        args.ingredients = args.ingredients.split(",")
    if args.meals:
        args.meals = args.meals.split(",")

    return args


# define another function
def execute_after_pars(connection, args):
    """
        Execute queries based on parsed arguments and print recipe suggestions.

        Args:
            connection (sqlite3.Connection): SQLite database connection.
            args (argparse.Namespace): Parsed command-line arguments.

        Prints:
            str: Recipe suggestions based on ingredients and meals, or a message if no recipes match.

        """
    # set arguments into SQL queries
    recipe_suggestions = db.find_recipes(connection, args.ingredients, args.meals)

    if len(recipe_suggestions) == 0:
        print("no such recipes")
    else:
        print("Recipe selected for you: ", recipe_suggestions)


def main():
    """
        Main function for the Food Blog Backend CLI application.

        Parses command-line arguments, initializes the database, populates tables,
        and handles user interactions.

        Args:
            None

        Returns:
            None
        """
    args = parse_arguments()

    db.db_name = args.database_file
    # generate database tables
    connection = db.connection(db.db_name)
    db.generate_tables(connection)
    # truncate/reset tables[meals, ingredients, measures]
    db.truncate_tables(connection)

    # dictionary data for populating tables
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry",
                            "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    # insert dict data into tables
    for key in data.keys():
        db.insert_many_db(connection, key, data[key])

    if args.meals or args.ingredients:
        # call execute_after_pars()
        execute_after_pars(connection, args)
        sys.exit()
    else:
        pass

    while True:
        # user input: recipe name
        print("Pass the empty recipe name to exit.")
        recipe_name = input("Enter recipe name: ")
        if len(recipe_name) == 0:
            sys.exit()
        else:
            # user input: recipe description
            recipe_desc = input("Describe recipe: ")

            # populate entries into recipes db table
            db.insert_to_recipe(connection, recipe_name, recipe_desc)

            # print all meals
            results = db.select_all_db(connection, "meals")

            for index, item in enumerate(results):
                print(f"{index + 1}) {item[1]}", end=" ")
            print()

            # ask when dish can be served
            dishes = input("Enter proposed meals separated by a space: ")
            dishes_int = [int(item) for item in dishes.split()]
            # get all recipes
            result = db.select_db(connection, "recipes", recipe_name)
            for item in dishes_int:
                db.insert_to_serve(connection, result[0], item)

            # ingredient information gathering
            # ingredient_info = " "
            quantity = []
            ingredient = []
            measure = []
            while True:
                ingredient_info = input("Input quantity of ingredient <press enter to stop>: ")
                if len(ingredient_info) == 0:
                    break
                elif len(ingredient_info.split()) == 2:
                    quant, ing = ingredient_info.split()
                    quantity.append(quant)
                    measure.append("")
                    if ing == "black" or ing == "blue":
                        ingredient.append(ing + "berry")
                    else:
                        ingredient.append(ing)
                elif len(ingredient_info.split()) == 3:
                    quant, meas, ing = ingredient_info.split()
                    quantity.append(quant)
                    measure.append(meas)
                    if ing == "black" or ing == "blue":
                        ingredient.append(ing + "berry")
                    else:
                        ingredient.append(ing)

            # insert ingredients
            result_ing = []
            for item in ingredient:
                # db.insert_ingredient_measure(connection, "ingredients", item)
                result_ing.append(db.select_db(connection, "ingredients", item))

            # insert measure
            result_mea = []
            for item in measure:
                result_mea.append(db.select_db(connection, "measures", item))

            # insert recipe_id, ingredient_id, measure_id, quantity into quantity
            for i in range(len(quantity)):
                db.insert_to_quantity(connection, "quantity", quantity[i][0], result[0],
                                      result_mea[i][0], result_ing[i][0])


if __name__ == "__main__":
    main()
