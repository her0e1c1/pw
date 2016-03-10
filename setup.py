from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="pwm",
    version="3.0.0",
    description="python password manager",
    author="Hiroyuki Ishii",
    packages=find_packages(),
    install_requires=required,
    entry_points="""
    [console_scripts]
    pwm = pwm.main:main
    """
)
