#! /bin/bash 

mkdir -p /opt/tautonet/logs
mkdir -p /opt/tautonet/tcases

chmod -R 777 /opt/tautonet/

pip install -r requirements.txt
python ./setup.py install
cp -r ./tcases/* /opt/tautonet/tcases/