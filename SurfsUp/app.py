#import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from flask import Flask, jsonify

#database setup
database_path = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

#reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(autoload_with=engine)

#save database references to a table
Measurement = Base.classes.measurement
Station = Base.classes.station

#flask setup
app = Flask(__name__)

#List all available routes
@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#app routing for precip for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session link
    session = Session(engine)
    #query the last 12 months of precip data
    cutoff_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
    session.close()

    #create a dictionary from the results and append to a list of precipitation_data
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

 #app routing for station list
@app.route("/api/v1.0/stations")
def stations():
    #create session link
    session = Session(engine)
    #query the names of all stations in the list
    results = session.query(Measurement.station).distinct().all()
    session.close()

    #create a dictionary of the active stations and their counts
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["station name"] = station[0]
        station_data.append(station_dict)

    return jsonify(station_data)

#app routing for t_observed for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    #create session link
    session = Session(engine)
    #query the last 12 months of temperature data from the most active observation station 
    cutoff_date_12month = '2016-08-23'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date_12month)).all()
    session.close()

    #create a dictionary of t_obs data for the most active station
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Oberved Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()

    temp_data = []
    for tobs in results:
        temp_dict = {}
        temp_dict["Average"] = results[0][0]
        temp_dict["Minimum"] = results[0][1]
        temp_dict["Maximum"] = results[0][2]
        temp_data.append(temp_dict)

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)