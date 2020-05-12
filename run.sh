#rfcomm release 0
sudo rfcomm bind /dev/rfcomm0 00:1D:A5:05:AF:10
./fix_touchscreen

python3 server.py > server.log 2>&1 &
echo "Server IP:   "`hostname -I`
echo "Server port: 6626"
python3 app.py > app.log 2>&1 &