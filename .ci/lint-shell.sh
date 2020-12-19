#!/usr/bin/env bash

RET=0

CUR_DIR=$(pwd)
SHELL_FILES=$(find "${CUR_DIR}" -type f -name '*.sh')

for SH_F in ${SHELL_FILES[*]}; do
    shellcheck --color=always \
               --severity=style \
               "${SH_F}" \
    || RET=${?}
done

exit ${RET}

