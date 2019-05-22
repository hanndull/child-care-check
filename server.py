"""CA Child Care Licensing Violations"""

# https://github.com/users/hanndull/projects/2

##### Import Libraries #######################################################

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Facility, Visitation, Citation, CitationDefinition
from sqlalchemy import func
from dateutil.parser import *

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
    max_date = request.form.get('min_date') ### more recent
    min_date = request.form.get('max_date') ### less recent
       ### TODO - add filter logic

    if name or zipcode or min_cit or max_cit or status or min_date:

        fquery = Facility.query ### Base query

        if name:
            fquery = fquery.filter(Facility.facility_name.like(f'%{name}%'))
        
        if zipcode:
            fquery = fquery.filter(Facility.facility_zip == int(zipcode))

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
            fquery = fquery.filter(Facility.facility_status == status)

        if min_date:
            # SELECT * FROM citations WHERE citation_date BETWEEN '2017-01-01' AND '2019-05-01';
            # can replace right date w/ "current_date" or left date with "where time > XXXdateXXX()"
            # https://popsql.com/learn-sql/postgresql/how-to-query-date-and-time-in-postgresql/


            ### THIS WORKED
            ### SELECT facilities.facility_name, citations.citation_date
            ### FROM facilities
            ### LEFT JOIN citations
            ### ON facilities.facility_id = citations.facility_id
            ### GROUP BY (citations.citation_date, facilities.facility_id)
            ### ORDER BY facilities.facility_id;

            ### MOST RECENT CITATION, Based on citations table=
            # test1=# SELECT facilities.facility_name, facilities.facility_id, MAX(citations.citation_date)
            # test1-# FROM citations
            # test1-# LEFT JOIN facilities
            # test1-# ON facilities.facility_id = citations.facility_id
            # test1-# GROUP BY (facilities.facility_id)
            # test1-# ORDER BY facilities.facility_id;

            ### MOST RECENT CITATION, based on facilities table
            # test1=# SELECT facilities.facility_name, facilities.facility_id, MAX(citations.citation_date)
            # test1-# FROM facilities 
            # test1-# LEFT JOIN citations
            # test1-# ON facilities.facility_id = citations.facility_id
            # test1-# GROUP BY facilities.facility_id
            # test1-# ORDER BY facilities.facility_id;

            ### MOST RECENT CITATION W/ FILTER DATE
            # SELECT DISTINCT ON (facilities.facility_id) facilities.facility_id, MAX(citations.citation_date)
            # FROM facilities 
            # LEFT JOIN citations
            # ON facilities.facility_id = citations.facility_id
            # GROUP BY facilities.facility_id, citations.citation_date HAVING citations.citation_date > '2018-01-01'
            # ORDER BY facilities.facility_id;
            isoparse(min_date)
            
            ### TODO - Fix this query
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility.facility_id, Facility.citations)
                .having(func.and_(Facility.citations <= min_date))
                )
            #10503
            
            #current_date = datetime.datetime.utcnow()
            #date_results = Citation.query.filter(Citation.citation_date <= min_date)
            # fquery = (fquery
            #     .outerjoin(Facility.citations)
            #     .group_by(Facility)
            #     .having(Facility.citations.citation_date <= isoparse(min_date)))

        facilities = fquery.all() ### Conglomerate all applicable queries

        flash('Applying your requested filters now...')

        return render_template('filter-results.html', facilities=facilities) 
        ### TODO - figure out how to diplay map w/ filtered points
    
    else:
        flash('No filters were applied.')

        return redirect('/') 


@app.route('/filter_by_zip')
def filter_zip():
    """Filter by facility zip code"""

    pass


@app.route('/facilities')
def show_facilities():
    """Facilities page"""

    facilities = Facility.query.all()

    return render_template('facilities.html', facilities=facilities)


@app.route('/facilities/<facility_id>')
def show_facility_details(facility_id):
    """Facility details info page"""

    facility = Facility.query.filter_by(facility_id=facility_id).one()

    return render_template('/facility_profile.html', facility=facility)


@app.route('/map')
def show_map():
    """Return page with facilities plotted to map"""

    facilities = Facility.query.all()

    return render_template('map.html', facilities=facilities)


@app.route('/geocode-request')
def send_geocode_request():

    facilities = Facility.query.all()

    # for facility in facilities:
        # Loop thru facilities, create geocode request url for each

        ### TODO - this is currently not saving to anything--
        ### Need to figure out if Google Geocode req is viable for this project
        # (f"https://maps.googleapis.com/maps/api/geocode/json?address={facility.address}+{facility_city}+{facility_state}&key=AIzaSyAw0meNSqLUJr9iQ0JLsC0b0xXxwBLrP_U")

    return 

#@app.route('/map/<facility_id>')



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