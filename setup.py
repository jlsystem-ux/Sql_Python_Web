from setuptools import setup, find_packages

setup(
    name="sql-for-testers",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "flask-login>=0.5.0",
        "flask-sqlalchemy>=2.5.0",
        "python-dotenv>=0.19.0",
        "werkzeug>=2.0.0",
    ],
    author="Luis Alberto Arboleda",
    author_email="arboledaluisalberto28@gmail.com",
    description="An interactive platform for learning and practicing SQL in real-time",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jlsystem-ux/Sql_Python_Web",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education :: Testing",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sql-for-testers=main:app",
        ],
    },
) 