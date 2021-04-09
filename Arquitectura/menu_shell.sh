#!/bin/bash
source /Users/rafaelgomezbermejo/Environments/arq/bin/activate
# ----------------------------------
# User defined function
# ----------------------------------
generate_new_dist(){
    python /Users/rafaelgomezbermejo/Repositorios/pythonScripts/Arquitectura/setup.py sdist bdist_wheel
}

local_install_arq(){
    pip uninstall -y architecture-tools-RafaelGB
    pip install dist/architecture-tools-RafaelGB-0.0.10.tar.gz
    break
}
run_general_test(){
    pytest --rootdir /Users/rafaelgomezbermejo/Repositorios/pythonScripts/Arquitectura/tdd -v  tdd/tdd_main.py
}
# ----------------------------------
# General Menu
# ----------------------------------
PS3='Please enter your choice: '
options=("Generate new dist" "Install arq in local" "Run general TEST" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Generate new dist")
            echo "you chose choice $REPLY which is $opt"
            generate_new_dist
            ;;
        "Install arq in local")
            echo "you chose choice $REPLY which is $opt"
            local_install_arq
            ;;
        "Run general TEST")
            echo "you chose choice $REPLY which is $opt"
            run_general_test
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done