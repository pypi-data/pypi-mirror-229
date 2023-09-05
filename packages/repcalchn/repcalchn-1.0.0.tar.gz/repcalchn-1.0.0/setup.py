import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="repcalchn",
    packages=['repcalchn'],
    version="1.0.0",
    author="Doctor",
    author_email="",
    description="The French Republican calendar and decimal time in Python in Chinese and French",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/git-thinker/repcalchn",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            'repcalchn=repcalchn.command_line:main'
        ]
    }
)
