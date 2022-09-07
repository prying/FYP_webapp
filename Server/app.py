from cmath import log10
import csv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flaskext.mysql import MySQL
import os.path

from datetime import datetime, timedelta
import operator

from sqlalchemy import column, true

import myFilters

# Passwords
import mySecrets

# configuration and definitions
DEBUG = True
RSSI_DISTANCE_EST = 6 # Meters
RSSI_AT_1_METER = -57
RSSI_N_FACTOR = 2.5 # Between 2 and 4 in most indoor spaces
RSSI_THRESHOLD = (RSSI_AT_1_METER - 10*RSSI_N_FACTOR*log10(RSSI_DISTANCE_EST)).real
print(f"rssi threshold = {RSSI_THRESHOLD}")
DEFUALT_VAR = 1.0682

RAW_DATA_FILE = "rawData.csv"

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# Database
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = mySecrets.username
app.config['MYSQL_DATABASE_PASSWORD'] = mySecrets.password
app.config['MYSQL_DATABASE_DB'] = mySecrets.database
app.config['MYSQL_DATABASE_HOST'] = mySecrets.host
mysql.init_app(app)

database_table = 'tbl_rssitest'

# enable CORS
# TODO: This needs to be changed later on as its currently all routes from anywhere
CORS(app, resources={r'/*': {'origins': '*'}})

def reCalcRSSI():
  conn = mysql.connect()
  cursor = conn.cursor()

  # First get a list of tags
  cursor.execute(f"""SELECT DISTINCT deviceID FROM tbl_rssiCpy """)
  deviceList = cursor.fetchall()

  for deviceID in deviceList:
    deviceID = deviceID[0]

    # Filter each beacon
    cursor.execute(f"""SELECT DISTINCT uuid FROM tbl_rssiCpy WHERE deviceID={deviceID} """)
    beaconList = cursor.fetchall()

    for uuid in beaconList:
      uuid = uuid[0]
      cursor.execute(f"""SELECT id, pkGroup, rssi FROM tbl_rssiCpy WHERE deviceID={deviceID} AND uuid={uuid}""")
      rows = cursor.fetchall()

      data = {
        'deviceID': deviceID,
        'uuid': uuid,
        'pkGroup': rows[0][1],
        'mu': rows[0][2],
        'sigma': DEFUALT_VAR
      }
      
      cursor.execute(f"""UPDATE tbl_rssiCpy SET rssiFiltered = {rows[0][2]} WHERE id = {rows[0][0]} """)
      conn.commit()

      for row in rows[1:]:
        data = myFilters.runningKalmanFilter(data, row[2], row[1])
        cursor.execute(f"""UPDATE tbl_rssiCpy SET rssiFiltered = {data['mu']} WHERE id = {row[0]} """)
        conn.commit()

  print('done re filtering!')

# Check if server is running
@app.route('/ping')
def ping():
	return jsonify('Server is running')

@app.route('/query', methods=['GET', 'POST'])
def databaseQuery():
  response_obj = {'status' : 'success'}

  if request.method == 'POST':
    post_data = request.get_json()

    # TODO: Sanity check data 
    databaseQuery.deviceID = post_data.get('deviceID')
    dateTimeRaw = post_data.get('date')

    # Prosses the date time into yyyy-mm-dd hh:mm:ss
    # Because of a bug on the client the time is submitted in UTC
    # TODO remove hard coded UTC offset
    databaseQuery.dateTime = []
    for timestamp in dateTimeRaw:
      databaseQuery.dateTime.append(datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours = 10))

    print(request)
    print('\n')

    response_obj['query'] = 'recived'

  if request.method == 'GET':
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(f"""SELECT timeRec, pkGroup, uuid, rssi, rssiFiltered FROM {database_table} 
      WHERE deviceID={databaseQuery.deviceID} 
      AND timeRec >= '{databaseQuery.dateTime[0]}' 
      AND timeRec <= '{databaseQuery.dateTime[1]}' """)
    rows = cursor.fetchall()

    # Save most recent request to CSV for optional download
    with open(RAW_DATA_FILE, 'w') as f:
      csvFile = csv.writer(f)
      csvFile.writerows(rows)

    rawTable = []
    for row in rows:
      #print(row)
      rawTable.append({
        'dateTime': row[0].strftime('%d/%m/%Y %H:%M:%S'),
        'pkGroup': row[1],
        'uuid': row[2],
        'rssi': row[3],
        'rssiFiltered': row[4]
      })
  
    # Get each different beacon ID
    cursor.execute(f"SELECT DISTINCT uuid FROM {database_table} WHERE deviceID={databaseQuery.deviceID} AND timeRec >= '{databaseQuery.dateTime[0]}' AND timeRec <= '{databaseQuery.dateTime[1]}' ")
    beacons = cursor.fetchall()

    roomList = []
    for beacon in beacons:
      cursor.execute(f"SELECT timeRec, rssiFiltered FROM {database_table} WHERE deviceID={databaseQuery.deviceID} AND uuid={beacon[0]} AND timeRec >= '{databaseQuery.dateTime[0]}' AND timeRec <= '{databaseQuery.dateTime[1]}' ")
      rows = cursor.fetchall()

      inRoomFlag = False
      enterTime = 0
      lastInRoomTime = 0
      for row in rows:
        if row[1] >= RSSI_THRESHOLD and not inRoomFlag:
          inRoomFlag = True
          enterTime = row[0]

        # Last time they where known to be in the room
        if row[1] >= RSSI_THRESHOLD:
          lastInRoomTime = row[0]

        # TODO last index check looks slow, optimise
        if (row[1] < RSSI_THRESHOLD or row == rows[-1]) and inRoomFlag:
          inRoomFlag = False
          roomList.append({
            'enterTime': enterTime.strftime('%Y-%m-%d %H:%M:%S'),
            'exitTime': lastInRoomTime.strftime('%Y-%m-%d %H:%M:%S'),
            'uuid': beacon[0]
          })

        # Catch edge case after previouse condition
        if row[1] < RSSI_THRESHOLD and inRoomFlag:
          inRoomFlag = False

    # Get a list of everyone that was in the same rooms at the same time
    contactList = []
    for place in roomList:
      cursor.execute(f"SELECT DISTINCT deviceID FROM {database_table} WHERE rssiFiltered >= {RSSI_THRESHOLD} AND uuid = {place['uuid']} AND deviceID != {databaseQuery.deviceID} AND timeRec >= '{place['enterTime']}' AND timeRec <= '{place['exitTime']}' ")
      deviceIDs = cursor.fetchall()

      for deviceID in deviceIDs:
        newDevice = True
        for contact in contactList:
          if contact['deviceID'] == deviceID[0]:
            newDevice = False
            if place['uuid'] not in contact['uuid']:
              contact['uuid'].append(place['uuid'])
        if newDevice == True:
          contactList.append({
            'deviceID': deviceID[0],
            'uuid': [place['uuid']]
          })

    # Sort the roomList by enter time
    roomList.sort(key = operator.itemgetter('enterTime'))

    cursor.close()
    conn.close()
    response_obj['roomTable'] = roomList
    response_obj['contactList'] = contactList
    response_obj['rawTable'] = rawTable

  return jsonify(response_obj)

@app.route('/rssi_submit', methods=['POST'])
def rssiSubmit():
  response_obj = {'status' : 'success'}

  try:
    a = len(rssiSubmit.filterData)
  except AttributeError:
    rssiSubmit.filterData = []
    rssiSubmit.filterData.append({
      'deviceID': 0,
      'uuid': 0,
      'pkGroup': 0,
      'mu': 0,
      'sigma': 0
    })

  if request.method == 'POST':
    pkGroup = int(request.args['pkGroup'])
    uuid = int(request.args['uuid'])
    rssi = int(request.args['rssi'])
    deviceID = int(request.args['deviceID'])
    rssiFiltered = -100
    # Preform filtering
    # Check if this device has already contacted the database before
    # TODO: same for loop used twice, try optimise
    if (not list(filter(lambda item: item['deviceID'] == deviceID and item['uuid'] == uuid, rssiSubmit.filterData))):
      # Add new filter data
      rssiSubmit.filterData.append({
        'deviceID': deviceID,
        'uuid': uuid,
        'pkGroup': pkGroup,
        'mu': rssi,
        'sigma': DEFUALT_VAR
      })

    for data in rssiSubmit.filterData:
      if data['deviceID'] == deviceID and data['uuid'] == uuid:
        data = myFilters.runningKalmanFilter(data, rssi, pkGroup)
        data['pkGroup'] = pkGroup
        rssiFiltered = data['mu']

    # Connect to database and submit
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO {database_table} (pkGroup, uuid, rssi, deviceID, rssiFiltered) VALUES ({pkGroup}, {uuid}, {rssi}, {deviceID}, {rssiFiltered}) """)

    conn.commit()

    cursor.close()
    conn.close()

    response_obj['query'] = 'recived'

  return jsonify(response_obj)

@app.route("/downloadTable", methods=['GET'])
def downloadTable():
  if os.path.exists(RAW_DATA_FILE):
    return send_file(RAW_DATA_FILE)
    


# Start Flask server
if __name__ == '__main__':
  #reCalcRSSI()
  databaseQuery.deviceID = 0
  databaseQuery.dateTime = []
  app.run(host='0.0.0.0', port=5000, debug=True)
