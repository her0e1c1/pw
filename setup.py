from setuptools import setup, find_packages


setup(
    name="pw",
    version="1.0.0",
    description="python password manager",
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    password = pw.commands:do
    """
)
