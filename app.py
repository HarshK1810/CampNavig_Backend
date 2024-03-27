from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt

import folium
from folium import plugins

import os
import json
import sqlite3

app = Flask(__name__)

# Generate a random 24-character secret key
app.secret_key = 'your_secret_key'  # Change this to a random secret key
bcrypt = Bcrypt(app)

# Function to create the users table in the SQLite database
def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

create_table()

class navigator:
    def __init__(self):
        self.geoResources = {}
        self.hospitalLocation =(19.01662689782006, 73.10362338086016)
        self.position = 'Eng'
        self.destination = 'Place1'

        for root, dirs, files in os.walk('GeoResources'):
            for file in files:
                self.geoResources[file.split('.')[0]] = root+'/'+file

    def changeStartPoint(self, newStartPoint):
        self.position = newStartPoint
        print(f'Selected Start: {self.position}; Selected Target: {self.destination}')
        self.redrawMap()

    def changeDestination(self,newDestination):
        self.destination = newDestination
        self.redrawMap()


    def drawStartBuilding(self,hospitalMap):

      if self.position == 'Canteen':
        self.position = 'Place1'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Canteen'

      if self.position == 'Ground':
        self.position = 'Place2'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Ground'

      if self.position == 'Civil':
        self.position = 'Place3'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Civil'

      if self.position == 'Dental':
        self.position = 'Place4'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Dental'

      if self.position == 'Hospital':
        self.position = 'Place5'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Hospital'

      if self.position == 'Medical':
        self.position = 'Place6'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Medical'

      if self.position == 'Parking':
        self.position = 'Place7'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Parking'

      if self.position == 'Poshan':
        self.position = 'Place8'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Poshan'

      if self.position == 'Pros':
        self.position = 'Place9'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Pros'

      if self.position == 'Quarter':
        self.position = 'Place10'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Quarter'

      if self.position == 'Eng':
        self.position = 'Place11'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Eng'

      if self.position == 'Gate':
        self.position = 'Place12'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Gate'


    def drawPathWay(self,hospitalMap):

      def switchPosition(coordinate):
        temp = coordinate[0]
        coordinate[0] = coordinate[1]
        coordinate[1] = temp
        return coordinate

      searchString = self.position + self.destination.split('Place')[1]
      print("searchString > ",searchString)
      with open(self.geoResources[searchString]) as f:
           testWay = json.load(f)

      for feature in testWay['features']:
        path = feature['geometry']['coordinates']

      finalPath = list(map(switchPosition,path))
      folium.plugins.AntPath(finalPath).add_to(hospitalMap)

    def drawBuilding(self,hospitalMap):
      hauseOutline = self.geoResources[self.destination]
      folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)



    def redrawMap(self):
        print(f'position {self.position}, destination {self.destination}')
        hospitalMap = folium.Map(location = self.hospitalLocation, width = "100%", zoom_start = 17)
        self.drawStartBuilding(hospitalMap)
        self.drawPathWay(hospitalMap)
        self.drawBuilding(hospitalMap)
        html_map = hospitalMap.get_root().render()
        return html_map
        #display(hospitalMap)

myNavigator = navigator()

# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    fullname = data.get('fullname')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)',
                       (fullname, username, email, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}),200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or Email already exists'}),404
    finally:
        conn.close()

# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[4], password):
        session['username'] = username
        return jsonify({'message': 'Login Successful'}),200
    else:
        return jsonify({'error': 'Invalid Username or Password'}),404
    

# Endpoint for fetching dashboard data
@app.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    # Check if user is logged in
    if 'username' in session:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        username = session['username']
        cursor.execute('SELECT fullname, email FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            fullname, email = user_data
            dashboard_data = {
                'fullname': fullname,
                'email': email,
                'message': 'Welcome to the dashboard!'
            }
            return jsonify(dashboard_data), 200
        else:
            return jsonify({'error': 'User data not found'}), 404
    else:
        return jsonify({'error': 'User not logged in'}), 401

# Endpoint for fetching map data
@app.route('/map', methods=['POST'])
def show_map():
    data = request.json
    selected_start = data.get('start')
    selected_target = data.get('target')

    if selected_start =='Gate' and selected_target =='Place12':
        message = "You are already at the Gate !!!"
        return jsonify({'message': message})
    elif selected_start =='Eng' and selected_target =='Place11':
        message = "You are already in the Engineering Building !!!"
        return jsonify({'message': message})
    elif selected_start =='Canteen' and selected_target =='Place1':
        message = "You are already at the Canteen !!!"
        return jsonify({'message': message})
    elif selected_start =='Ground' and selected_target =='Place2':
        message = "You are already at the Ground !!!"
        return jsonify({'message': message})
    elif selected_start =='Civil' and selected_target =='Place3':
        message = "You are already in Civil Building !!!"
        return jsonify({'message': message})
    elif selected_start =='Dental' and selected_target =='Place4':
        message = "You are already in Dental Building !!!"
        return jsonify({'message': message})
    elif selected_start =='Hospital' and selected_target =='Place5':
        message = "You are already in Hospital !!!"
        return jsonify({'message': message})
    elif selected_start =='Medical' and selected_target =='Place6':
        message = "You are already in Medical Building !!!"
        return jsonify({'message': message})
    elif selected_start =='Parking' and selected_target =='Place7':
        message = "You are already at the Parking Area !!!"
        return jsonify({'message': message})
    elif selected_start =='Quarter' and selected_target =='Place10':
        message = "You are already at the Staff Quarter Area !!!"
        return jsonify({'message': message})
    elif selected_start =='Poshan' and selected_target =='Place8':
        message = "You are already at the Poshan Area !!!"
        return jsonify({'message': message})
    elif selected_start =='Pros' and selected_target =='Place9':
        message = "You are already at the Prosthetics And Orthotics Building !!!"
        return jsonify({'message': message})
    else:
        myNavigator.changeStartPoint(selected_start)
        myNavigator.changeDestination(selected_target)
        print("start >",selected_start)
        print("target >",selected_target)
        hospitalMap = myNavigator.redrawMap()
        return jsonify({'map': hospitalMap, 'message': None})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

    