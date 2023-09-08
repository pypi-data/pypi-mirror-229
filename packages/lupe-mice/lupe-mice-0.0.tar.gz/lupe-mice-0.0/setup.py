from setuptools import setup, find_packages
import os


curr_dir = os.path.abspath(os.path.dirname(__file__))


with open("README.md", "r") as fh:
    long_description = fh.read()


def get_requirements():
    with open(os.path.join(curr_dir, "requirements.txt"), encoding="utf-8") as f:
        return f.read().strip().split("\n")


setup(
    name='lupe-mice',
    version='0.0',
    packages=find_packages(),
    install_requires=get_requirements(),
    include_package_data=True,
    python_requires=">=3.9",
    url='https://github.com/runninghsus/lupe',
    license='',
    author='alexanderhsu',
    entry_points={
        "console_scripts": [
            "lupe =lupe.__main__:main"
        ]
    },
    author_email='ahsu2@andrew.cmu.edu',
    description='Introducing LUPE, the innovative no code website predicting pain behavior in mice.',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
