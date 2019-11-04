#!/bin/bash

set -euo pipefail

base_url='https://mcmicro.s3.amazonaws.com/exemplars/001/exemplar-001'

# We will use this name for both the top level project directory as well as the
# single dataset directory inside it.
dataset="exemplar_001"

echo "Creating project directory '$dataset'"
mkdir -p "$dataset"
cd "$dataset"

echo "Downloading files..."

curl -f -s -O "$base_url/data.yaml"
curl -f -s -O "$base_url/markers.csv"

echo

mkdir -p "$dataset"
cd "$dataset"
mkdir -p raw_files illumination_profiles
base=$(pwd)
for i in `seq 10`; do
  name="exemplar-001-cycle-$(printf %02d $i)"
  cd "$base/raw_files"
  echo "$name raw image"
  curl -f -# -O "$base_url/raw_files/$name.ome.tiff"
  cd "$base/illumination_profiles"
  echo "$name illumination profiles (2)"
  curl -f -# -O "$base_url/illumination_profiles/$name-dfp.tif"
  curl -f -# -O "$base_url/illumination_profiles/$name-ffp.tif"
  echo
done

echo "Done"
