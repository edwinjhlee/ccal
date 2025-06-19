from setuptools import setup, find_packages

setup(
    name="ccal",
    version="0.1.0",
    description="一个带农历和节日的终端日历应用（Textual UI）",
    author="Li Junhao",
    author_email="l@x-cmd.com",
    license="AGPLv3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "textual>=0.40.0",
        "cnlunar",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "ccal=app:main_entry"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)