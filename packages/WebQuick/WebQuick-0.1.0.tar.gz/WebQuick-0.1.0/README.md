
# PySet - Python Project Boilerplate Generator

PySet is a command-line tool that simplifies the process of setting up Python web projects using popular frameworks like Django, FastAPI, and Flask. It allows you to quickly create project templates based on your chosen framework and project name.

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher installed on your system.

### Installation

You can install PySet using pip:

```bash
pip install WebQuick
```

### Usage

To create a new Python web project, use the following command:

```bash
WebQuick <framework> <project_name>
```

Replace `<framework>` with the desired framework (`django`, `fastapi`, or `flask`) and `<project_name>` with the name you want for your project.

#### Examples

Create a new Django project named "mydjangoapp":

```bash
WebQuick django mydjangoapp
```

Create a new FastAPI project named "myfastapiapp":

```bash
WebQuick fastapi myfastapiapp
```

Create a new Flask project named "myflaskapp":

```bash
WebQuick flask myflaskapp
```

### Features

- Generates a project directory with a standard structure for the selected framework.
- Automatically updates the Django settings module in `manage.py` with the project name.
- Supports Django, FastAPI, and Flask frameworks.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test thoroughly.
4. Commit your changes with clear and concise messages.
5. Push your changes to your fork.
6. Create a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the open-source community for their contributions and support.

Happy coding!
```
Feel free to save this content to a Markdown file (e.g., `README.md`) within your project's repository and customize it as needed.