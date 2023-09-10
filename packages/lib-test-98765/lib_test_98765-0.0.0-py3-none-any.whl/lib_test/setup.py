from setuptools import setup, find_packages

setup(
    name="lib_test_98765",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["python-dotenv==1.0.0"],
    entry_points={
        'console_scripts': [
            'hello=lib_test.command_line.bye:main',
            'bye=lib_test.command_line.hello:main'
        ]}
)
