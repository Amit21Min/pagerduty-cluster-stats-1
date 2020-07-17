#!/bin/bash

set -exv

CURRENT_DIR=$(dirname "$0")

BASE_IMG="pagerduty-cluster-stats"
IMG="${BASE_IMG}:latest"

BUILD_CMD="docker build" IMG="$IMG" make docker-build