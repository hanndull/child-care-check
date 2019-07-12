"""CA Child Care Licensing Violations"""

# https://github.com/users/hanndull/projects/2

##### Import Libraries #######################################################

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Facility, Visitation, Citation, CitationDefinition
from sqlalchemy import func, distinct
from dateutil.parser import isoparse
import requests
import json
import os
import sys

##### Create App #############################################################

app = Flask(__name__)

app.secret_key = os.environ['APP_KEY'] ### Store key in secrets.sh
### must run `source secrets.sh` in ea new shell where you want to run server

# Raise an error for an undefined variable in Jinja
app.jinja_env.undefined = StrictUndefined

##### Define Routes ##########################################################

@app.route('/')
def show_home():
    """Homepage"""
    
    return render_template('home.html')


@app.route('/about')
def show_about():
    """Render About page"""

    return render_template('about.html')


@app.route('/facilities')
def show_facilities():
    """Facilities page"""

    facilities = Facility.query.order_by(Facility.name).all()
    num_facilities = len(facilities)

    return render_template(
                            'facilities.html', 
                            facilities=facilities, 
                            num_facilities=num_facilities
                            )


@app.route('/citations')
def show_citation_defs():
    """Page of citation definitions"""

    cit_defs = CitationDefinition.query.order_by(CitationDefinition.code).all()

    return render_template('common-citations.html', cit_defs=cit_defs)


@app.route('/facilities/<f_id>')
def show_facility_details(f_id):
    """Facility details info page"""

    facility = Facility.query.filter_by(f_id=f_id).one()

    f_url = f'https://secure.dss.ca.gov/CareFacilitySearch/FacDetail/{facility.number}'

    return render_template('/facility_profile.html', facility=facility, f_url=f_url)


@app.route('/citations/<cd_id>')
def show_citation_details(cd_id):
    """Citation Definition info on page"""

    citation_def = CitationDefinition.query.filter_by(cd_id=cd_id).one()

    cd_url = citation_def.url

    return render_template('/citation-profile.html', citation_def=citation_def, cd_url=cd_url)


@app.route('/map')
def show_map():
    """Return page with facilities plotted to map
    Data for base map pins coming from @app.route('/mapping-facilities.json')
    Data for filtered map pins coming from 
    """

    return render_template('map.html')


@app.route('/pass-json.json')
def pass_json_to_js():
    """Read local JSON file and pass to map"""

    with open('data.txt') as file:  
        data = file.read()
        
        return data

@app.route('/get-filter-geocode.json', methods=['GET'])
def retrieve_filter_coords():
    """Request geocoded coords of city or zipcode input by user
    For use in centering filtered map on searched location
    """
    city = request.args.get('city')
    zipcode = request.args.get('zipcode')

    if city and zipcode:
        url_insert = (f"{city}+CA+{zipcode}")
    elif city:
        url_insert = (f"{city}+CA")
    else:
        url_insert = (f"CA+{zipcode}")

    geocode_url = (f"https://maps.googleapis.com/maps/api/geocode/json?address={url_insert}&key=AIzaSyDlFREKPkL5QDTnbsWAgm-abRBK6JS3nv4")

    results = requests.get(geocode_url)
    results = results.json()

    if len(results['results']) != 0:
        answer = results['results'][0]
        
        lat = answer.get('geometry').get('location').get('lat')
        lng = answer.get('geometry').get('location').get('lng')

        return jsonify({"lat": lat, "lng": lng})
 
    return None


@app.route('/multi-filter.json')
def process_facilities():
    """Recieve and store filtration input into JSON for homepage map
    and for use on /facilities page filter buttons
    """
    
    name = request.args.get('name')
    city = request.args.get('city')
    status = request.args.get('status')
    f_type = request.args.get('type')

    fquery = Facility.query ### Base query

    if name:
            name = name.upper()
            fquery = fquery.filter(Facility.name.like(f'%{name}%')
                )
    
    if not city:
        city = 'SAN FRANCISCO'
    if city:
            city = city.upper()
            fquery = fquery.filter(Facility.city.like(f'%{city}%')
                )
    
    if not status:
        status = 'LICENSED'
    if status:
        status = status.upper()
        if status == 'PROBATION':
            status = 'ON PROBATION'
        fquery = fquery.filter(Facility.status == status)             

    fquery = fquery.filter(Facility.status == 'LICENSED')

    facilities = fquery.all() ### Conglomerate all queries
    
    facility_count = len(facilities)
    facilities_dict = {"count": facility_count}

    for facility in facilities:     
        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    "citation_count": len(facility.citations),
                    }
        facilities_dict[str(facility.f_id)] = mapinfo 
        ### must stringify for comparison of f_id to "count"
    
    return jsonify(facilities_dict)


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
    
    fquery = Facility.query ### Base query


    if name or zipcode or city or min_cit or max_cit or status or suppress_date or f_type:

        if name:
            name = name.upper()
            fquery = fquery.filter(Facility.name.like(f'%{name}%')
                )
        
        if zipcode:
            fquery = fquery.filter(Facility.f_zip == int(zipcode))

        if city:
            city = city.upper()
            fquery = fquery.filter(Facility.city.like(f'%{city}%')
                )            

        if min_cit:
            ### Below query based off of https://stackoverflow.com/a/38639550
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) >= min_cit)
                )

        if max_cit:
            ### Below query based off of https://stackoverflow.com/a/38639550
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) <= max_cit)
                )

        if suppress_date:
            ### Show only facilities who have had 0 citations since input date
            suppress_date = isoparse(suppress_date)

            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having((func.max(Citation.date) <= suppress_date) | (func.count_(Facility.citations) == 0))
                )
        
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

    
    testquery = fquery ### To show total num markers that should be produced

    fquery = fquery.limit(200)
    page_num = int(page_num)

    if page_num > 1:
        fquery = fquery.offset(200 * (page_num - 1))
        ### Add offset and limit to keep ea query to ~100
        ### Logic for pagination so front end can request specific "page"

    facilities = fquery.all() ### Conglomerate all applicable queries
    testquery = testquery.all()
    testquery_count = len(testquery)

    facility_count = len(facilities)
    
    facilities_dict = {"count": facility_count}

    for facility in facilities:     
        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    "citation_count": len(facility.citations),
                    }
        facilities_dict[str(facility.f_id)] = mapinfo 
        ### must stringify for comparison of f_id to "count"
    
    return jsonify(facilities_dict)


##### For Creating JSON for BaseMap ###########################################

@app.route('/mapping-facilities.json')
def create_map_json():
    """Create json for base map out of facilities query.
    For quicker loading of initial map fn that is called when user loads 
    /map route. Includes color label for use in creation of map markers.
    """

    facilities_list = Facility.query.all() 

    facilities = {}

    for facility in facilities_list:     
        citation_count = len(facility.citations)

        mapinfo = {
                    "title": facility.name,
                    "lat": facility.latitude, 
                    "lng": facility.longitude,
                    "status": facility.status,
                    "citation_count": citation_count,
                    }

        facilities[str(facility.f_id)] = mapinfo

    with open('data.txt', 'w') as outfile:  
        json.dump(facilities, outfile)
    
    return "Production of JSON was a success"


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
    #app.debug = True
    
    # ensures templates, etc. are not cached in debug mode
    #app.jinja_env.auto_reload = app.debug


    connect_to_db(app)

    # enables use of DebugToolbar
    # DebugToolbarExtension(app)
    # import pdb; pdb.set_trace()
    app.run(port=5000, host='0.0.0.0')