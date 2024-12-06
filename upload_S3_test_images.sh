#!/bin/bash

cd images/
for IMAGE in *; do 
    aws s3 cp $IMAGE s3://pointless-analogies-image-bucket/$IMAGE
done
