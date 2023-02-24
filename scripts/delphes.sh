#!/bin/bash

DefaultEntryPoint=/usr/local/share/delphes/delphes/DelphesHepMC2
if [[ $1 == *".py" ]]; then
    DefaultEntryPoint=python
fi

docker run -i --rm  -v $PWD:$PWD -w $PWD --entrypoint $DefaultEntryPoint \
    gitlab-registry.cern.ch/scipp/mario-mapyde/delphes-snowmass:master $1 $2 $3