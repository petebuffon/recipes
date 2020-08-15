from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="recipes",
    version="1.0",
    author="Peter Buffon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["recipes"],
    include_package_data=True,
    zip_safe=False,
    url="https://github.com/petebuffon/recipes",
    install_requires=[
        "Flask>=1.1.2",
        "Flask-Session",
        "requests",
        "flask-wtf",
        "gunicorn"
    ]
)
