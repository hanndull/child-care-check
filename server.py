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


@app.route('/facilities')
def show_facilities():
    """Facilities page"""

    facilities = Facility.query.order_by(Facility.name).all()

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
    Data for base map pins coming from @app.route('/mapping-facilities.json')
    Data for filtered map pins coming from 
    """

    return render_template('map.html')


@app.route('/mapping-facilities.json')
def create_map_json():
    """Create json for base map out of facilities query"""

    facilities_list = Facility.query.filter(Facility.longitude != None, Facility.status == 'LICENSED').all() 

    facilities = {}
    
    for facility in facilities_list:     
        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    "citation_count": len(facility.citations),
                    }
### TODO - This area is taking a lot of time to load, consider whether to add count to db, or some other solution
        facilities[facility.f_id] = mapinfo
    
    return jsonify(facilities)


@app.route('/filter-results.json')
def process_form():
    """Recieve and store filtration input into JSON"""

    name = request.args.get('name')
    zipcode = request.args.get('zipcode')
    city = request.args.get('city')
    min_cit = request.args.get('min_cit')
    max_cit = request.args.get('max_cit')
    status = request.args.get('status')
    suppress_date = request.args.get('suppress_date')
    f_type = request.args.get('type')
    page_num = request.args.get('page_num') ### For use in pagination

    ### TODO - Citation date and counts may not be working together


    fquery = Facility.query.options(db.joinedload('citations')) ### Base query

    fquery = fquery.offset(100 * page_num).limit(100)
        ### Add offset and limit to keep ea query to ~100
        ### Logic for pagination so front end can request specific "page"

    if name or zipcode or city or min_cit or max_cit or status or suppress_date or f_type:

        if name:
            name = name.upper()
            fquery = fquery.filter(Facility.name.like(f'%{name}%'))
        
        if zipcode:
            fquery = fquery.filter(Facility.f_zip == int(zipcode))

        if city:
            city = city.upper()
            fquery = fquery.filter(Facility.city.like(f'%{city}%'))            

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

        if suppress_date:
            ### Show only facilities who have had 0 citations since input date
            suppress_date = isoparse(suppress_date)

            fquery = (fquery
                .join(Citation)
                .group_by(Facility.f_id)
                .having(func.max(Citation.date) <= suppress_date))
        
        if status:
            status = status.upper()
            if status == 'PROBATION':
                status = 'ON PROBATION'
            fquery = fquery.filter(Facility.status == status)

        if f_type:
            if f_type == 'infant':
                f_type = 'INFANT CENTER'
            elif f_type == 'ill':
                f_type = 'DAY CARE CENTER - ILL CENTER'
            elif f_type == 'prek':
                f_type = 'DAY CARE CENTER'
            elif f_type == 'school':
                f_type = 'SCHOOL AGE DAY CARE CENTER'
            fquery = fquery.filter(Facility.f_type == f_type)

    facilities = fquery.all() ### Conglomerate all applicable queries
    
    # else:
    #     facilities = Facility.query.all()
    
    ### TODO -- consider setting to user location, if no filter params given

    facility_count = len(facilities)
    start = time.time()
    print(">>>>>> PROCESSING INTO JSON: ", facility_count)
    
    facilities_dict = {"count": facility_count}

    for facility in facilities:     
        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    "citation_count": len(facility.citations),
                    } ### TODO - ^This area is taking a lot of time to load, consider whether to add count to db, or some other solution
        facilities_dict[facility.f_id] = mapinfo
    
    end = time.time()
    print(end, "Time elapsed: ", end - start)
    
    return jsonify(facilities_dict)


##### For Geocoding ##########################################################

@app.route('/geocode-request', methods=['POST', 'GET'])
def send_geocode_request():
    """Requesting of geocodes via Google Geocode API for all facilities in db.
    Also adds latitude, longitude, and Google Place ID to db.
    """
    pass ### Only for use in finding and storing lat/long when adding/updating

    # facilities = Facility.query.filter(Facility.longitude == None).all()

    # completed = []
    # failed = []
    # counter = 0

    # for facility in facilities:
    #     if counter <= 5500:
    #         if '#' in facility.address:
    #             address = ''
    #             for charac in facility.address:
    #                 if charac != '#':
    #                     address += charac
    #                 else: 
    #                     break
    #         else:
    #             address = facility.address 

    #         geocode_url = (f"https://maps.googleapis.com/maps/api/geocode/json?address={address}+{facility.city}+{facility.state}+{facility.f_zip}&key=AIzaSyAw0meNSqLUJr9iQ0JLsC0b0xXxwBLrP_U")
    #         results = requests.get(geocode_url)
    #         results = results.json()

    #         if len(results['results']) != 0:
    #             answer = results['results'][0]
    #             facility.latitude = answer.get('geometry').get('location').get('lat')
    #             facility.longitude = answer.get('geometry').get('location').get('lng')
    #             facility.google_place_id = answer.get("place_id")
    #             #print('>>>>>>>>>>>>>', facility.longitude)
    #             db.session.commit()
    #             completed.append(facility.f_id)

    #         else:
    #             completed.append('FAILED')
    #             failed.append(facility.f_id)
    #         if len(completed)%100 == 0:
    #             print (">>>>>>>>> completed: ",len(completed), "failed: ", len(failed))
            
    #         counter += 1

    # output = {'completed': completed, 'failed': failed}

    # return render_template('geocode-request.html', output=output)


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