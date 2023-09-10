from setuptools import setup, find_packages

setup(
    name="lib_test_98765",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["python-dotenv==1.0.0"],
    entry_points={
        'console_scripts': [
            'hello=lib_test.command_line:hello_main',
            'bye=lib_test.command_line:bye_main'
        ]}
)
