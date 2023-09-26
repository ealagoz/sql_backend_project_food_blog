
# Food Blog Backend CLI Application

This is a command-line interface (CLI) application for managing a food blog backend. It allows you to interact with a SQLite database to store and retrieve recipes, ingredients, meals, and more.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

Before you can use this application, ensure you have Python 3.x installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/food-blog-backend.git
   ```

2. Change to the project directory:
   ```bash
   cd food-blog-backend
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the Food Blog Backend CLI application, follow these steps:

1. Run the `blog.py` script with the required arguments:

   ```bash
   python blog.py <database_file>
   ```

   - `<database_file>`: The name of the SQLite database file (e.g., `food_blog.db`).

2. You can also use optional arguments:
   - `--ingredients`: Specify a list of ingredients separated by commas.
   - `--meals`: Specify a list of meals separated by commas.

3. After initializing the database and populating necessary tables, you can perform the following actions:
   - Add new recipes with names and descriptions.
   - Associate recipes with meals.
   - Input ingredient quantities for recipes.

4. To find recipe suggestions based on ingredients and meals, you can use the `--ingredients` and `--meals` optional arguments when running the script. For example:

   ```bash
   python blog.py food_blog.db --ingredients="milk,cacao" --meals="breakfast,lunch"
   ```

## Features

- Initialize and manage a SQLite database for your food blog.
- Add recipes, ingredients, meals, and measures.
- Associate recipes with meals and input ingredient quantities.
- Find recipe suggestions based on specified ingredients and meals.
- User-friendly command-line interface for interacting with the backend.

## Contributing

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, please open an issue or create a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to customize this README to include more specific details about your project or additional sections as needed.
