
#All import and dependencies

import datetime as dt
import numpy as np


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

Base = automap_base()

Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

#Create landing page with possible routes
@app.route('/')
def Welcome():
    return(
        f"Welcome to the Hawaiian Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' dates require format of MMDDYYYY.</p>"
    )

#This landing page returns all precipiation values
@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    
    session.close()
    precip = { date: prcp for date, prcp in precipitation}

    return jsonify(precip)

#this landing page returns all station IDs
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations=stations)

#This page returns all date for temperature
#NOTE, CSV files contains data only 2010 to 2017
@app.route('/api/v1.0/tobs')
def temp_monthly():
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_ago).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)

#Start and End date searches for Tobs (Temperature Observations).
#Only available 2010 to 2017
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))

        return jsonify(temps=temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y" )

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug=True)

