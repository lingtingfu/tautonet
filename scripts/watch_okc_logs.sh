#! /bin/bash

cd $HOME/go/src/github.com/ok-chain/okchain/dev/
watch -n 1 "ls ./autonet_data/okc_*/okc*.log -l; ls ./autonet_data/okc_*/stc*.log -l"