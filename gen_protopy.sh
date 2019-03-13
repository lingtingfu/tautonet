#! /bin/bash 

proto_path=`go env | grep GOPATH | cut -d= -f2 | sed 's/"//g'`/src/github.com/okchain/go-okchain/protos
crr_dir=`pwd`
dest_dir=$crr_dir/autonet/okproto
cd $proto_path
cp ./*.proto $dest_dir
python -m grpc_tools.protoc -I. --python_out=$dest_dir --grpc_python_out=$dest_dir ./*.proto