#!/usr/bin/env bash
#
# Create app/common/build_info.py using current build parameters
#
# From pl-cloud-starter/backend/cloud-starter-falcon
#  ./build/generate_build_info.sh
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/config.sh

(
cd ${SCRIPT_DIR}/..

cat << EOF > app/common/build_info.py
# -*- coding: utf-8 -*-
"""
Build information for this service.

Auto-generated during the build process - do not modify
"""


class BuildInfo(object):
    """Current build info"""
    repo_name = '${REPO_NAME}'
    service_type = '${SERVICE_TYPE}'
    service_name = '${SERVICE_NAME}'
    version = '${DOCKER_VERSION}'
    commit_hash = '$(git rev-parse HEAD)'
    build_date = '$(date)'
    build_epoch_sec = $(date +%s)
EOF
)
