# analysis_usedecorator.py
import nbformat
from nbconvert import PythonExporter
import inspect
import os
import pkg_resources


def convert_notebook_to_python(notebook_file, python_file):
    # Load the notebook file
    with open(notebook_file, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Configure the exporter
    exporter = PythonExporter()

    # Export the notebook to a Python script
    (python_code, resources) = exporter.from_notebook_node(notebook)

    # Write the Python code to a file
    with open(python_file, "w", encoding="utf-8") as f:
        f.write(python_code)


def convert_str_to_dict(input_str: str):
    output_dict = {}
    key_value_pairs = input_str.split(",")

    for pair in key_value_pairs:
        key, value = pair.split("=")
        key = key.strip()  # Remove any extra spaces
        value = value.strip().strip('"')
        output_dict[key] = value
    return output_dict


# create struture template function
def create_struture_template(func, folder_directory: str):
    source_lines, _ = inspect.getsourcelines(func)
    decorator_line = source_lines[0]

    try:
        ster = decorator_line[decorator_line.find("(") + 1 : decorator_line.rindex(")")]

        dict_args = convert_str_to_dict(ster)
        title: str = dict_args["name"]
        dict_args["title"] = title
        dict_args["name"] = title.replace(" ", "_").lower()
        """make directory"""

        d_story = folder_directory + "/" + dict_args["name"]
        print(f"d_story: {d_story}")

        """crate directory function name"""
        os.mkdir(d_story)
        os.mkdir(d_story + "/src")

        main_file = os.path.join(d_story + "/src/", "main.py")
        with open(main_file, "w") as file:
            file.write("")
        with open(os.path.join(d_story, "setup.yml"), "w") as file:
            file.write("")
        with open(os.path.join(d_story + "/src/", "__init__.py"), "w") as file:
            file.write("")
        with open(os.path.join(d_story, "requirements.txt"), "w") as file:
            file.write("")
        with open(os.path.join(d_story, "LICENSE"), "w") as file:
            file.write("")
        with open(os.path.join(d_story, "README.md"), "w") as file:
            file.write("")
        return dict_args

    except:
        print("could not read")


# retrieve source code
def retrieve(func, folder_contain):
    source_lines, _ = inspect.getsourcelines(func)
    """skip decorator function name"""
    new_lines = source_lines[1:]
    source_code = "".join(new_lines)
    """
    write content main.py
    change file path
    """
    file_path = folder_contain + "/src/main.py"
    #  file_name = os.path.join(absolute_path, "TestFunction/main.py")

    with open(file_path, "a") as f:
        f.write(source_code)
    # print(source_code)


def get_functions_with_decorator(module, decorator):
    functions = []
    # print(dir(module))

    for name, obj in inspect.getmembers(module):
        if (
            inspect.isfunction(obj)
            and hasattr(obj, "__wrapped__")
            and getattr(obj, decorator.__name__, False) is True
        ):
            functions.append(obj)

    return functions


def write_resource_package(file_path, source_function):
    ignore_package = ["pulsar"]
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(
        ["%s==%s" % (i.key, i.version) for i in installed_packages]
    )
    list_package_append = []
    # file_path = "usedecorator_2.py"
    with open(file_path, "r") as file:
        content = file.read()
        for ipl in installed_packages_list:
            x = ipl.split("==")
            if x[0] in ignore_package:
                continue
            if content.find(x[0]) != -1:
                list_package_append.append(ipl)

    # print(list_package_append)
    requirement_file_path = os.path.join(source_function, "requirements.txt")
    with open(requirement_file_path, "a") as file:
        for lpa in list_package_append:
            file.write(lpa)
            file.write("\n")
