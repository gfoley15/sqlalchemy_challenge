# Import the dependencies.
# import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaiian climate API.<br/>"
        f"Here are the Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    # Calculate the date one year from the last date in data set.
    one_year_date = most_recent_date - dt.timedelta(days=365)

    """Return a list of precipitation data including date and precipitation amount"""
    # Query precipitation from Measurement table
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_date)

    session.close()

    # Create a dictionary from the row data and append to a list
    prcp_data = []
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    station_query = session.query(Station.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_query))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperature obserations for the last 12 months"""
    # Using the most active station
    # Query the last 12 months of temperature observation data for most active station
    lastyr_temps_query = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_date).\
    filter(Measurement.date <= most_recent_date).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list
    temps_data = []
    for date, tobs in lastyr_temps_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temps_data.append(tobs_dict)

    return jsonify(temps_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of MIN, MAX, and AVG temperature obserations for all the dates greater than or equal to the start date"""
    start_date_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurment.date >= start).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list
    start_temps_data = []
    for row in start_date_query:
        start_date_temps_dict = {}
        low_t, high_t, avg_t = row
        start_date_temps_dict["low_t"] = low_t
        start_date_temps_dict["high_t"] = high_t
        start_date_temps_dict["avg_t"] = avg_t
        start_temps_data.append(start_date_temps_dict)

    return jsonify(start_temps_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of MIN, MAX, and AVG temperature obserations for the dates from the start date to the end date, inclusive."""
    start_end_date_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    start_end_temps_data = []
    for row in start_end_date_query:
        start_end_date_temps_dict = {}
        low_t, high_t, avg_t = row
        start_end_date_temps_dict["low_t"] = low_t
        start_end_date_temps_dict["high_t"] = high_t
        start_end_date_temps_dict["avg_t"] = avg_t
        start_end_temps_data.append(start_end_date_temps_dict)

    return jsonify(start_end_temps_data)

if __name__ == '__main__':
    app.run(debug=True)
