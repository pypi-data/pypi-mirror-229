from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name="switch-file",
    version="1.0.3",
    packages=find_packages(),
    install_requires=[
        # dependencies
        "img2pdf",
        "pandas",
        "reportlab",
        "python-docx2pdf",
        "pywin32",
    ],
    entry_points={
    "console_scripts": [
        "switch-file = switch_file.converter:main"
    ]
},
    long_description="""
    Python package that simplifies the process of converting various file formats to PDF, including Word (DOCX), text, images, and XLSX files. It provides a convenient command-line interface for users.
    """,
    long_description_content_type='text/markdown',
    author="Harshita Dhurwe",
    author_email="harshitadhurwe@gmail.com",
    license="MIT",
     password="pypi-AgEIcHlwaS5vcmcCJGQwZGNmY2M0LTU2ZDktNDU0Ni1hNzQ4LTgzZGNlMjQ0MGFjNAACKlszLCJkM2MxNGVjNS03M2I2LTRlYmQtODcyZi1mNDZkZmRiOGJmY2MiXQAABiB7ugRCnqBbRGpshn5yDnL3UArtNKGld3uwWGq5Q6TF2A",
)
