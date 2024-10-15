#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")

BUILD_DIR="$PROJECT_ROOT/build"

if [ -d "$BUILD_DIR" ]; then
  echo "Deleting contents of $BUILD_DIR"
  rm -rf "$BUILD_DIR/*"
else
  echo "Creating build directory: $BUILD_DIR"
  mkdir -p "$BUILD_DIR"
fi

cd "$BUILD_DIR" || exit

echo "Running cmake .."
cmake ..

echo "Running make"
make
