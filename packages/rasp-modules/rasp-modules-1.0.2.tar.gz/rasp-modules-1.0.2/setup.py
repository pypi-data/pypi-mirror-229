import setuptools

with open("README.md", encoding="utf-8") as rd:
    long_description = rd.read()

setuptools.setup(
    name="rasp-modules",
    version="1.0.2",
    author="Salah Ud Din (@4yub1k)",
    author_email="salahuddin@protonmail.com",
    description="It contains modules for raspberry PI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='LICENSE',
    url="https://github.com/4yub1k/rasp-modules",
    keywords=["rasberry", "rasberrypi", "rasberry pi"],
    project_urls={
        "Documentation": "https://rasp-modules.readthedocs.io/en/latest/",
        "Source": "https://github.com/4yub1k/rasp-modules",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
