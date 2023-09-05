import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="categorical-gpt",
    version="0.1.2",
    author="Karim Huesmann",
    author_email="karimhuesmann@gmail.com",
    description="Transformation of categorical data to numerical feature vectors with Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khuesmann/categorical-gpt",
    project_urls={
        "Homepage": "https://github.com/khuesmann/categorical-gpt",
        "Bug Tracker": "https://github.com/khuesmann/categorical-gpt/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={
        'categorical_gpt.gui': ['.output/public/*'],
    },
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["scikit-learn", "scikit-image", "numpy", "flask", "flask-cors", "networkx", "umap-learn", "loguru", "requests"],
)
