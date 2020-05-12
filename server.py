from flask import Flask
from flask import render_template
from flask import jsonify

import os
import csv
from datetime import datetime

RCD_DIR = './static/rcd'
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
  rcds = []
  for rcd in os.listdir(RCD_DIR):
    if not rcd == "static":
      rcds.append({
        'name': rcd,
        'href': 'rcds/' + rcd
      })
  rcds.sort(key = lambda i: i['name'], reverse=True)
  return render_template('index.html', rcds=rcds)

@app.route('/rcds/<rcd>')
def rcd(rcd):
  video_file = rcd + '/' + rcd + '.mp4'
  if not os.path.exists(RCD_DIR + '/' + video_file):
    video_file=None

  return render_template('rcd.html', video= video_file, data=rcd)

@app.route('/data/<rcd>')
def data(rcd):
  data_file = RCD_DIR + '/' + rcd + '/' + rcd + '.csv'
  reader = csv.DictReader(open(data_file, 'r'), delimiter=',')
  data = {}
  data_dict = list(reader)
  # print(data_dict)

  for field in data_dict[0]:
    if not field == '':
      data[field] = []
    if field == 'lat' or field == 'lon':
      data['gps'] = []
  # print(data)

  for row in data_dict:
    for field in data:
      if field == 'gps':
        data[field].append([float(row['lat']), float(row['lon'])])
      else:
        data[field].append(float(row[field]))
      

  # print(data)
  return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6626)