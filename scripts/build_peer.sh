#!/bin/bash

cd $HOME/go/src/github.com/ok-chain/okchain/cmd/okchaind
CGO_CFLAGS=" " CGO_LDFLAGS="-lstdc++ -lm -lz -lbz2 -lsnappy" GOBIN=$HOME/go/src/github.com/ok-chain/okchain/build/bin go install