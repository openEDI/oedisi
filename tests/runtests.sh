#!/usr/bin/env bash

cd "$(dirname "$0")"

run_helics () {
    timeout 60 ./helics-run.sh || {
        echo "$folder failed helics run"; exit 2
    }
}

for folder in test_*
do
    cd $folder
    echo "Running tests in $folder"
    for script in *.py
    do
        echo "Running $script"
        python $script || {
            echo "$script failed"; exit 1
        }
    done
    echo "Running helics in $folder"
    {
        run_helics || exit 2
    } | {
        tee >( grep -q 'error' && {
                   echo "$folder helics contains error"
                   exit 3
               }
             )
    }

    cd ..
done
