import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_static_files(path, prefix='src/categorical_gpt/'):
    res = []
    for root, dirs, files in os.walk(path):
        for file in files:
            res.append(os.path.join(file).replace(prefix, ''))
    return res


setuptools.setup(
    name="categorical-gpt",
    version="0.1.6",
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
    include_package_data=True,
    package_dir={"categorical_gpt": "src/categorical_gpt"},
    package_data={
        'categorical_gpt': ['gui/.output/public/favicon.ico',
                            'gui/.output/public/index.html',
                            'gui/.output/public/404.html',
                            'gui/.output/public/200.html',
                            'gui/.output/public/value-assignments/index.html',
                            'gui/.output/public/characteristics/index.html',
                            'gui/.output/public/results/index.html',
                            'gui/.output/public/_nuxt/Icon.569dfb32.js',
                            'gui/.output/public/_nuxt/IconCSS.e6fb2110.js',
                            'gui/.output/public/_nuxt/error-404.1109f9fd.js',
                            'gui/.output/public/_nuxt/export.3c8a7cf1.js',
                            'gui/.output/public/_nuxt/value-assignments.92be1689.js',
                            'gui/.output/public/_nuxt/default.23e872a6.js',
                            'gui/.output/public/_nuxt/error-500.e798523c.css',
                            'gui/.output/public/_nuxt/IconCSS.fe0874d9.css',
                            'gui/.output/public/_nuxt/wizzard.3c4dee2d.js',
                            'gui/.output/public/_nuxt/results.b43ee184.js',
                            'gui/.output/public/_nuxt/entry.7d06bf3a.css',
                            'gui/.output/public/_nuxt/entry.193f47eb.js',
                            'gui/.output/public/_nuxt/config.270a4c2e.js',
                            'gui/.output/public/_nuxt/error-500.8a0d15bf.js',
                            'gui/.output/public/_nuxt/index.c6479a78.js',
                            'gui/.output/public/_nuxt/characteristics.aa155223.js',
                            'gui/.output/public/_nuxt/CharacteristicList.vue.8d7e1db5.js',
                            'gui/.output/public/_nuxt/Icon.6f5d80f8.css',
                            'gui/.output/public/_nuxt/error-404.95c28eb4.css',
                            'gui/.output/public/export/index.html'],
    },
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["scikit-learn", "scikit-image", "numpy", "flask", "flask-cors", "networkx", "umap-learn", "loguru", "requests"],
)
