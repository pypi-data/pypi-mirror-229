#!/bin/zsh

conda init zsh
conda activate envname

cd notification_center/frontend
npm run build
cd ../..

python setup.py sdist bdist_wheel

# if upload is the first parameter
twine upload --skip-existing dist/*
