#!/bin/bash

cd $GOPATH/src/github.com/ok-chain/okchain/cmd/okchaind;
CGO_CFLAGS=" " CGO_LDFLAGS="-lstdc++ -lm -lz -lbz2 -lsnappy" GOBIN=$GOPATH/src/github.com/ok-chain/okchain/build/bin go install
cd $GOPATH/src/github.com/ok-chain/okchain/cmd/okchaincli;
CGO_CFLAGS=" " CGO_LDFLAGS="-lstdc++ -lm -lz -lbz2 -lsnappy" GOBIN=$GOPATH/src/github.com/ok-chain/okchain/build/bin go install
