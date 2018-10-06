#!/bin/sh
# Copyright 2018 Evgeny Golyshev <eugulixes@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

if [ -f .env ]; then
    . ./env
fi

set -x

ADDR=${HOST:="http://127.0.0.1:8006"}

USERNAME=${USERNAME:=""}

PASSWORD=${PASSWORD:=""}

PYTHON=${PYTHON:="python3"}

set +x

if [ -z "${PYTHON}" ]; then
    >&2 echo "Python interpreter is not specified"
    exit 1
fi

${PYTHON} rc_tests.py --host="${HOST}" --username="${USERNAME}" --password="${PASSWORD}"

