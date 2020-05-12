python3 server.py > server.log 2>&1 &
echo "Server IP:   "`hostname -I`
echo "Server port: 6626"
python3 app.py > app.log 2>&1 &