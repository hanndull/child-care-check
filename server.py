"""CA Child Care Licensing Violations"""

# https://github.com/users/hanndull/projects/2

##### Import Libraries #######################################################

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Facility, Visitation, Citation, CitationDefinition
from sqlalchemy import func

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
    date = request.form.get('date')
    ### TODO - Add status filter
    ### TODO - Add date-range filter

    print(">>>>>>>>>>>>>>>>>>>>>>>>", date)
    ### TODO - Turn into datetime obj

    if name or zipcode or min_cit or max_cit or status:

        fquery = Facility.query

        if name:
            fquery = fquery.filter(Facility.facility_name.like(f'%{name}%'))
        if zipcode:
            fquery = fquery.filter(Facility.facility_zip == int(zipcode))

        #####################################################################################
        ### Below queries need to be like:

        ### SELECT facilities.facility_name, citations.facility_id, COUNT(*) 
        ### FROM citations JOIN facilities ON 
        ### facilities.facility_id = citations.facility_id 
        ### GROUP BY (citations.facility_id, facilities.facility_id);


        ### SELECT COUNT(citation_id), facility_id FROM citations GROUP BY facility_id;
        if min_cit:

            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) >= min_cit))

        if max_cit:
            fquery = (fquery
                .outerjoin(Facility.citations)
                .group_by(Facility)
                .having(func.count_(Facility.citations) <= max_cit))

        if status:
            fquery = fquery.filter(Facility.facility_status == status)

        facilities = fquery.all()


#######################

            # facilities = (Facility.query
            #     .(querystring)
            #     # .outerjoin(Facility.citations)
            #     # .group_by(Facility)
            #     # .having(func.count_(Facility.citations) >= min_cit)
            #     .all())

#######################


        flash('Applying your requested filters now!')

        return render_template('filter-results.html', facilities=facilities) 
        ### TODO - figure out why it is not rendering test.html
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