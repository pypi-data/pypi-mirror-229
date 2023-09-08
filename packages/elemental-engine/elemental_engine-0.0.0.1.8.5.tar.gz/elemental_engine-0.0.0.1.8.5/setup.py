from setuptools import setup, find_packages

VERSION = '0.0.0.1.8.5'
DESCRIPTION = 'Elemental Engine - Fast API based robust REST API'
LONG_DESCRIPTION = ''

setup(
    name="elemental_engine",
    version=VERSION,
    author="Elemental (Tom Neto)",
    author_email="<info@elemental.run>",
    description=DESCRIPTION,
    url='https://github.com/tomneto/ElementalEngine.git',
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={
        'elemental_engine': [
            'docs/*',
            'docs/descriptions/*',
            'handlers/binaries/*.dll',
            'handlers/binaries/*.dylib',
            'handlers/binaries/*.so',
        ],
    },
    include_package_data=True,
    install_requires=['pymongo', 'certifi', 'python-dotenv', 'uvicorn', 'fastapi', 'chardet', 'psutil'],
    keywords=['python', 'api'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    zip_safe=False,
    python_requires='>=3.8'
)
