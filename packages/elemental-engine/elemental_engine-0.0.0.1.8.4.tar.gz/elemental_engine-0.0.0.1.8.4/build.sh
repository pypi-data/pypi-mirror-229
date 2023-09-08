# Read the version from version.txt
version=$(cat version.txt)
echo Building Engine $version

echo Compiling C code

bin_code_path=./elemental_engine/handlers/binaries
gcc -fPIC -shared -o ${bin_code_path}/bin.dylib ${bin_code_path}/bin.c
docker-compose up
i686-w64-mingw32-gcc -fPIC -shared -o ${bin_code_path}/bin.dll ${bin_code_path}/bin.c

# Update the version in setup.py
awk -v new_version="$version" '/VERSION =/{gsub(/'\''[0-9]+\.[0-9]+\.[0-9]+.*'\''/, "'\''" new_version "'\''")}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py

# Update the version in pyproject.toml
awk -v new_version="$version" '/version =/{gsub(/'\''[0-9]+\.[0-9]+\.[0-9]+.*'\''/, "'\''" new_version "'\''")}1' pyproject.toml > pyproject.toml.tmp
mv pyproject.toml.tmp pyproject.toml

# Run the build and upload commands
python3 -m build

twine upload ./dist/* --username elemental --password Mm12052015@

sudo rm -rf ./dist

sudo rm -rf ./elemental_engine.egg-info



