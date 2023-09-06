from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='mdnet',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.9',
    packages=['mdnet'],
    install_requires=[
        'markdown',
        'jinja2',
        'python-frontmatter',
        'feedgen',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'mdnet=mdnet.mdnet:main',
        ],
    },
)
