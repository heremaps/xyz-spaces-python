#!/usr/bin/env bash

# Copyright (C) 2019-2020 HERE Europe B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# License-Filename: LICENSE

# If the search path in conf.py is not set-up this will inspect the installed
# xyzspaces package, not the local code in the xyzspaces subfolder!

export DEST=docs/apiref
rm -f $DEST/*.rst
rm -rf $DEST/_build
rm -rf $DEST/_static
rm -rf $DEST/_templates

# Just creating conf.py, Makefile and make.bat once, hence commenting below.

sphinx-apidoc --private --separate --module-first --full -o $DEST xyzspaces
sphinx-build -b html -D html_theme=sphinx_rtd_theme $DEST $DEST/_build/html
