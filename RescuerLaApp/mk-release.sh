#!/bin/bash
rm -rf ./bin/app/ && rm -r ./bin/Release/
echo "restoring packeges"
dotnet restore
echo -n "building for linux: ubuntu16"
dotnet publish --framework netcoreapp2.2 --runtime="ubuntu.16.04-x64" -c Release -o ./bin/app/ununtu16
echo -n "building for linux: ubuntu18"
dotnet publish --framework netcoreapp2.2 --runtime="ubuntu.18.04-x64" -c Release -o ./bin/app/ununtu18
echo -n "building for linux"
dotnet publish --framework netcoreapp2.2 --runtime="linux-x64" -c Release -o ./bin/app/linux
echo -n "building for win10"
dotnet publish --framework netcoreapp2.2 --runtime="win10-x64" -c Release -o ./bin/app/win10
echo -n "building for osx"
dotnet publish --framework netcoreapp2.2 --runtime="osx-x64" -c Release -o ./bin/app/osx
cd ./bin/app/
zip -r -9 ./ununtu16.zip ./ununtu16/
zip -r -9 ./ununtu18.zip ./ununtu18/
zip -r -9 ./linux.zip ./linux/
zip -r -9 ./win10.zip ./win10/
zip -r -9 ./osx.zip ./osx/