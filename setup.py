# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bmb",
    version="1.0.0",
    author="Marouan Bouchettoy",
    author_email="marouan.bouchettoy@gmail.com",
    description="Framework rapide pour applications web avec BMDB ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BM-Framework/bmb",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "blinker==1.9.0",
        "bmdb==1.2.0",
        "click==8.3.1",
        "colorama==0.4.6",
        "Flask==3.1.2",
        "flask-cors==6.0.2",
        "greenlet==3.3.0",
        "itsdangerous==2.2.0",
        "Jinja2==3.1.6",
        "MarkupSafe==3.0.3",
        "psycopg2==2.9.11",
        "PyJWT==2.10.1",
        "python-dotenv==1.2.1",
        "PyYAML==6.0.3",
        "setuptools==80.9.0",
        "SQLAlchemy==2.0.45",
        "typing_extensions==4.15.0",
        "Werkzeug==3.1.5",
    ],
    entry_points={
        "console_scripts": [
            "bmb=bmb.cli:main",
        ],
    },
)