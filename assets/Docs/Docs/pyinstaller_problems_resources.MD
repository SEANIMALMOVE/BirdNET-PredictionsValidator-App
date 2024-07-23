# Compiling Python Code with PyInstaller

This guide helps you compile your Python application using PyInstaller on both Windows and Linux without encountering common errors.

## Windows

1. Create the spec file:

    ```sh
    pyi-makespec --collect-data=gradio_client --collect-data=gradio --onefile app.py
    ```

2. Modify the generated spec file:
    - Add the following to the `Analysis` section:

    ```python
    module_collection_mode={
        'gradio': 'py',  # Collect gradio package as source .py files
    },
    ```

3. Save the spec file as `app_windows.spec`.

4. Run the custom script:

    ```sh
    python assets/editSpecData.py windows
    ```

5. Compile the application:

    ```sh
    pyinstaller app_windows.spec
    ```

## Linux

1. Create the spec file:

    ```sh
    pyi-makespec --collect-data=gradio_client --collect-data=gradio app.py
    ```

2. Modify the generated spec file:
    - Add the following to the `Analysis` section:

    ```python
    module_collection_mode={
        'gradio': 'py',  # Collect gradio package as source .py files
    },
    ```

3. Save the spec file as `app_linux.spec`.

4. Run the custom script:

    ```sh
    python assets/editSpecData.py linux
    ```

5. Compile the application:

    ```sh
    pyinstaller app_linux.spec
    ```

## Common Issues and Solutions

- **Module Not Found**: Use the `--collect-data` option to include necessary data files from external packages.
- **DLL Load Errors**: Ensure all dependencies are correctly included in the spec file. Refer to [this StackOverflow post](https://stackoverflow.com/questions/47289279/error-loading-python-dll-loadlibrary-the-specified-module-could-not-be-found) for more details.
For more troubleshooting tips, visit the [PyInstaller GitHub issue discussion](https://github.com/pyinstaller/pyinstaller/issues/8108).
