#! /bin/bash

P=$HOME/go/src/github.com/ok-chain/okchain/dev/
watch -n 1 "echo $P; ls -lh ./autonet_data/okc_*/okc*.log; ls -lh ./autonet_data/okc_*/stc*.log "

echo $P