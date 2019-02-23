#! /bin/bash

gsutil -m cp -r ~/ray_results/$(ls -t ~/ray_results | head -1) gs://ray_results

while true
do
    gsutil -m rsync -r ~/ray_results/$(ls -t ~/ray_results | head -1) gs://ray_results/$(ls -t ~/ray_results | head -1)
    sleep 600
done
