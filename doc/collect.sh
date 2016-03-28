
set -x

echo $0
echo $PWD
pwd

python3 ../pyinstaller.py -v

git describe --long --dirty
git describe --long --dirty --tag
git status
