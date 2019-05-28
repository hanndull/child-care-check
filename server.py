"""CA Child Care Licensing Violations"""

# https://github.com/users/hanndull/projects/2

##### Import Libraries #######################################################

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Facility, Visitation, Citation, CitationDefinition
from sqlalchemy import func, distinct
from dateutil.parser import *
import requests
import time

##### Create App #############################################################

app = Flask(__name__)

app.secret_key = "Hannah"

# Raise an error for an undefined variable in Jinja
app.jinja_env.undefined = StrictUndefined


##### Define Routes ##########################################################

@app.route('/')
def show_home():
    """Homepage"""

    return render_template('home.html')


@app.route('/filter')
def display_filter_form():
    """Display filter fields of form"""

    return render_template('filter.html')


@app.route('/filter-results', methods=['POST'])
def process_form():
    """Recieve and store filtration input"""

    name = request.form.get('name').upper()
    zipcode = request.form.get('zipcode')
    min_cit = request.form.get('min_cit')
    max_cit = request.form.get('max_cit')
    status = request.form.get('status').upper()
    suppress_date = request.form.get('suppress_date')

    if name or zipcode or min_cit or max_cit or status or suppress_date:

        fquery = Facility.query ### Base query

        if name:
            fquery = fquery.filter(Facility.name.like(f'%{name}%'))
        
        if zipcode:
            fquery = fquery.filter(Facility.f_zip == int(zipcode))

        if min_cit:
            ### Below query based off of https://stackoverflow.com/a/38639550
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) >= min_cit))

        if max_cit:
            ### Below query based off of https://stackoverflow.com/a/38639550
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) <= max_cit))

        if status:
            if status == 'PROBATION':
                status = 'ON PROBATION'
            fquery = fquery.filter(Facility.status == status)

        if suppress_date:
            ### Show only facilities who have had 0 citations since input date
            suppress_date = isoparse(suppress_date)

            fquery = (fquery
                .join(Citation)
                .group_by(Facility.f_id)
                .having(func.max(Citation.date) <= suppress_date))

        facilities = fquery.all() ### Conglomerate all applicable queries

        facility_count = len(facilities)

        flash('Applying your requested filters now...')

        return render_template('filter-results.html', 
                                facilities=facilities, 
                                facility_count=facility_count) 
            ### TODO - figure out how to diplay map w/ filtered points
    
    else:
        flash('No filters were applied.')

        return redirect('/') 


@app.route('/facilities')
def show_facilities():
    """Facilities page"""

    facilities = Facility.query.all()

    return render_template('facilities.html', facilities=facilities)


@app.route('/facilities/<f_id>')
def show_facility_details(f_id):
    """Facility details info page"""

    facility = Facility.query.filter_by(f_id=f_id).one()

    f_url = f'https://secure.dss.ca.gov/CareFacilitySearch/FacDetail/{facility.number}'

    return render_template('/facility_profile.html', facility=facility, f_url=f_url)


@app.route('/map')
def show_map():
    """Return page with facilities plotted to map
    Data for map pins coming from @app.route('/mapping-facilities.json')
    """

    return render_template('map.html')


@app.route('/mapping-facilities.json')
def create_map_json():
    """Create json for map out of facilities query"""

    facilities_list = Facility.query.filter(Facility.longitude != None, Facility.status == 'LICENSED').all() 
    
    facilities = {}
    
    for facility in facilities_list:     
        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    }

        facilities[facility.f_id] = mapinfo
    
    return jsonify(facilities)


@app.route('/geocode-request', methods=['POST', 'GET'])
def send_geocode_request():
    """Requesting of geocodes via Google Geocode API for all facilities in db.
    Also adds latitude, longitude, and Google Place ID to db.
    """

    facilities = Facility.query.filter(Facility.longitude == None).all()

    completed = []
    failed = []
    counter = 0

    for facility in facilities:
        if counter <= 5500:
            if '#' in facility.address:
                address = ''
                for charac in facility.address:
                    if charac != '#':
                        address += charac
                    else: 
                        break
            else:
                address = facility.address 

            geocode_url = (f"https://maps.googleapis.com/maps/api/geocode/json?address={address}+{facility.city}+{facility.state}+{facility.f_zip}&key=AIzaSyAw0meNSqLUJr9iQ0JLsC0b0xXxwBLrP_U")
            results = requests.get(geocode_url)
            results = results.json()

            if len(results['results']) != 0:
                answer = results['results'][0]
                facility.latitude = answer.get('geometry').get('location').get('lat')
                facility.longitude = answer.get('geometry').get('location').get('lng')
                facility.google_place_id = answer.get("place_id")
                #print('>>>>>>>>>>>>>', facility.longitude)
                db.session.commit()
                completed.append(facility.f_id)

            else:
                completed.append('FAILED')
                failed.append(facility.f_id)
            if len(completed)%100 == 0:
                print (">>>>>>>>> completed: ",len(completed), "failed: ", len(failed))
            
            counter += 1

    output = {'completed': completed, 'failed': failed}

    return render_template('geocode-request.html', output=output)


##### Dunder Main ############################################################

if __name__ == "__main__":
    
    # debug must be True at time DebugToolbarExtension invoked
    app.debug = True
    
    # ensures templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug


    connect_to_db(app)

    # enables use of DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')