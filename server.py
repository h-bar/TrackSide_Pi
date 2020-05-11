from flask import Flask
from flask import render_template
from flask import jsonify

import os
import csv
from datetime import datetime

RCD_DIR = './rcd'
app = Flask(__name__, static_folder='rcd')

@app.route('/')
def index():
  rcds = []
  for rcd in os.listdir(RCD_DIR):
    if not rcd == "static":
      rcds.append({
        'name': rcd,
        'href': 'rcds/' + rcd
      })
  return render_template('index.html', rcds=rcds)

@app.route('/rcds/<rcd>')
def rcd(rcd):
  video_file = rcd + '/' + rcd + '.mp4'
  if not os.path.exists(RCD_DIR + '/' + video_file):
    video_file=None

  return render_template('rcd.html', video=video_file, data=rcd)

@app.route('/data/<rcd>')
def data(rcd):
  data_file = RCD_DIR + '/' + rcd + '/' + rcd + '.csv'
  reader = csv.DictReader(open(data_file, 'r'), delimiter=';')
  data = {}
  data_dict = list(reader)

  for field in data_dict[0]:
    if not field == '':
      data[field] = []
    if field == 'gps-lat' or field == 'gps-lon':
      data['gps'] = []
  # print(data)

  for row in data_dict:
    for field in data:
      if field == 'gps':
        data[field].append([float(row['gps-lat']), float(row['gps-lon'])])
      else:
        data[field].append(float(row[field]))
      

  # print(data)
  return jsonify(data)

if __name__ == '__main__':
    app.run(port=6626, debug=True)