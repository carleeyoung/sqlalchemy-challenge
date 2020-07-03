# 1. import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
    
import datetime as dt
from datetime import date

import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Home Page
@app.route("/")
def welcome():
    """Welcome to the Hawaii Weather App"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Convert query results to dictionary using date as the key and prcp as the value. Return JSON representation of dictionary. 
#################################################
# Precipitation Page
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    past_year = pd.to_datetime(last_day) - dt.timedelta(days=365)

    one_year_ago = pd.to_datetime(past_year[0]).strftime('%Y-%m-%d')

    """Return a dictionary of date: precipitation data for all Hawaii weather stations"""
    # Query data for the precipitation data for the last year in the dataset
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    date_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_prcp.append(prcp_dict)

    return jsonify(date_prcp)


#Return a JSON lsit of stations from the dataset
#################################################
# Station Page
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of weather stations where data is collected in Hawaii"""
    # Query all passengers
    results = session.query(Station.station, Station.name).all()

    session.close()

    station_list = []

    for station in results:
        
        station_list.append(station)

    return jsonify(station_list)


#Query the dates and temperature observations of the most active stations for the last year of data.
#Return a JOSN list of temperature observations (TOBS) for the previous year.
#################################################
# Temperature observations Page

@app.route("/api/v1.0/tobs")
def TOBS():
    
    session = Session(engine)

    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    past_year = pd.to_datetime(last_day) - dt.timedelta(days=365)

    one_year_ago = pd.to_datetime(past_year[0]).strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    session.close()

    return jsonify(results)


#################################################
# Temps from start date Page

@app.route("/api/v1.0/<start>")
def start_date(start):
    print("Server received request for '<start>' page...")


    start_dt = pd.to_datetime(str(start)).strftime('%Y-%m-%d')


    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= func.strftime(start_dt)).\
        filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    session.close()


    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)


#################################################
# Temps from start date and end date Page
@app.route("/api/v1.0/<start>/<stop>")

def start_stop_date(start, stop):

    print("Server received request for '<start>' page...")


    start_dt = pd.to_datetime(str(start)).strftime('%Y-%m-%d')
    stop_dt = pd.to_datetime(str(stop)).strftime('%Y-%m-%d')


    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= func.strftime(start_dt), Measurement.date <= func.strftime(stop_dt)).\
        filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    session.close()


    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)


if __name__ == "__main__":
    app.run(debug=True)



