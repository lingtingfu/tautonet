#! /bin/bash

echo "Your Local IP: " `ifconfig | grep 192 | grep broadcast | awk '{print $2}'`
echo "Your Current User: " `users`