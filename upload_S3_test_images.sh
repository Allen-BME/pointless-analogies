#!/bin/bash

cd images/
for IMAGE in *; do 
    aws s3 cp $IMAGE s3://pointless-analogies-images/$IMAGE
done
