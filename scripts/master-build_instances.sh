#!/bin/bash
for i in {6..10}
do
    gcloud compute disks create "instance-$i" --zone "us-east1-b" --source-snapshot "sumo101-ray-gcloud" --type "pd-standard"
    gcloud compute instances create "instance-6" --zone "us-east1-b" --disk name=instance-6,device-name=instance-6,mode=rw,boot=yes --metadata startup-script='#! /bin bash
done
