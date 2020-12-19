#!/usr/bin/env bash

RET=0

CUR_DIR=$(pwd)
YAML_FILES=$(find "${CUR_DIR}" -type f \( -iname '*.yml' -or -iname '*.yaml' \))

for YM_F in ${YAML_FILES[*]}; do
    yamllint -c "${CUR_DIR}/.ci/yamllint.yml" "${YM_F}" \
    || RET=${?}
done

exit ${RET}

