from flask import Flask, render_template, request
from flask import redirect, url_for
from flask_mysqldb import MySQL
import requests
import json
import pandas as pd
from flask import jsonify

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'dsci551'
app.config['MYSQL_PASSWORD'] = 'Lrx@1998'
app.config['MYSQL_DB'] = 'dsci551'
mysql.init_app(app)


@app.route('/')
def main():
   return render_template('index.html')

@app.route('/data',methods=['GET'])
def displayall():
    cnx = mysql.connection
    cursor = cnx.cursor()
    query = "select * from info where pollutant_standard = 'PM25 Annual 2012'"\
    "limit 20 "
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('data.html',data=data)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/location')
def location():
    cnx = mysql.connection
    cursor=cnx.cursor()
    query = "select distinct city from info"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('location.html',data=data)

@app.route('/average')
def average():
    data = pd.read_csv("average.csv",index_col=None)
    data=data.sort_values(by=['average_aqi'])
    return render_template('average.html',tables=[data.to_html(index=False)],titles=data.columns.values)

@app.route('/search',methods=['GET','POST'])
def search():
    data = {}
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        fil = request.form['filter']
        standard = request.form['standard']
        keyword = request.form['search']
        date = request.form['date']
        if date=="" or date is None:
            cursor.execute(f"select * from info where {fil}='{keyword}' AND pollutant_standard = '{standard}' order by date_local")
        else:
            cursor.execute(f"select * from info where {fil}='{keyword}' AND pollutant_standard = '{standard}' AND date_local= '{date}'")
        data = cursor.fetchall()
    return render_template('search.html',data=data)

@app.route('/realtime',methods=['GET','POST'])
def realtime():
    data={}
    wea=[]
    poll=[]
    if request.method == "POST":
        location = request.form['realtime']
        response = requests.get(f'http://api.airvisual.com/v2/city?city={location}&state=California&country=USA&key=9b22d3de-036c-45d5-911a-e5c96ddcaf47')
        data =response.json()['data']
        if response:
            weather = data['current']['weather']
            pollution = data['current']['pollution']
            wea = list(weather.values())[1:]
            poll = list(pollution.values())[1:]
        else:
            print("Sorry, location data is unavailable")
            
    return render_template('realtime.html',wea=wea,poll=poll)


if __name__ == '__main__':
   app.run(debug = True)
