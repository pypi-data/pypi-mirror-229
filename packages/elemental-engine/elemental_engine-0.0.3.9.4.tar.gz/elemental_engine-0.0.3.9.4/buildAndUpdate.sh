python3 -m build

twine upload dist/*tar.gz

sudo rm dist

sudo rm elemental_engine.egg-info