#!/bin/bash

# This script creates and configures conda environment for lacmus project. 
# The name of the environment will be 'lacmusenv' by default or the one you passed as the first argument.
# Usage:
# ./setup_conda_env.sh [environment_name]

# Do not forget to grand the script execute permission by:
# chmod +x ./setup_conda_env.sh


env_name=$1

if [ -z $env_name ]
then
env_name="lacmusenv"
fi

conda create -n $env_name python=3.7 anaconda
source activate $env_name
conda install tensorflow-gpu==1.14
pip install numpy --user
pip install . --user
python setup.py build_ext --inplace

echo
echo "Done creating $env_name environment"
