#!/bin/bash

echo "Build gvit/veracode..."
docker build . -f Dockerfile -t gvit/veracode:latest #--no-cache

echo "Done!"
