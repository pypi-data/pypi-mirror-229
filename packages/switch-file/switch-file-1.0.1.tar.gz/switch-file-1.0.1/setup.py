from setuptools import setup, find_packages

setup(
    name="switch-file",
    version="1.0.1",
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
}
)
