#!/usr/bin/env python3
# Copyright (c) 2019-2021 PyI40AAS Contributors
#
# This program and the accompanying materials are made available under the terms of the Eclipse Public License v. 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0 which is available
# at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="fmu_to_aasx",
    version="0.0.1",
    author="Sebastian Heppner",
    author_email="s.heppner@plt.rwth-aachen.de",
    description="A script to add AAS Simulation Model Ports to an existing AASX file based on the ports from an FMU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=["fmu_to_aasx"]
)
