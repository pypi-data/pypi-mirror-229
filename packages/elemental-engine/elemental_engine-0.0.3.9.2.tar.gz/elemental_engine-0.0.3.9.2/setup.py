from setuptools import setup, find_packages

VERSION = '0.0.3.9.2'
DESCRIPTION = 'Elemental Engine - for internal API development'
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
    include_dirs=['elemental_engine'],
    packages=find_packages(),
    package_data={'./': ['./elemental_engine/handlers/binaries/bin.so']},
    include_package_data=True,
    install_requires=['pymongo', 'certifi', 'python-dotenv', 'uvicorn', 'fastapi', 'chardet'],
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