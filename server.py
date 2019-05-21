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
    ### TODO - Add status filter
    ### TODO - Add date-range filter


    if name or zipcode or min_cit or max_cit or status:
        if name:
            facilities = Facility.query.filter(Facility.facility_name.like(f'%{name}%')).all()
        elif zipcode:
            facilities = Facility.query.filter(Facility.facility_zip == int(zipcode)).all()

        #####################################################################################
        ### Below queries need to be like:

        ### SELECT facilities.facility_name, citations.facility_id, COUNT(*) 
        ### FROM citations JOIN facilities ON 
        ### facilities.facility_id = citations.facility_id 
        ### GROUP BY (citations.facility_id, facilities.facility_id);


        ### SELECT COUNT(citation_id), facility_id FROM citations GROUP BY facility_id;
        elif min_cit:
            
            cit_by_facility = Citation.query.group_by('facility_id')

            cit_by_facility.query.options(db.joinedload('facilities.facility_id')).having(db.func.count(Citation.))

            #c = Citation.query.group_by('facility_id').having(db.func.count(Citation.citation_id) > int(min_cit))
            
            citations_facilities = Citation.query.options(db.joinedload('facilities')).all()
            print (citations_facilities)
            # facilities = []

            # Facility.query.filter(Facility.citations != False).all()
            facilities = Facility.query.all()

            #for facility in facilities:
                #if facility.citations > 2:


            
            ### citations_facilities = a list of citations... Need to get it to be grouped by facility
            # for facility in citations_facilities:
            #     if facility.citations.count() > min_cit:
            #         facilities.append(facility)


            # num_facilities_with_cits = Facility.query.options(db.joinedload('citations')).count()
            # facilities = facilities_citations.group_by('facility_id').having(db.func.count(Citation.citation_id) >= int(min_cit)).all()
            # q = Citation.query
            # facilities = q.group_by('facility_id').having(db.func.count(Citation.citation_id) >= int(min_cit)).all()
        elif max_cit:
            q = Citation.query
            facilities = q.group_by('facility_id').having(db.func.count(Citation.citation_id) <= int(max_cit)).all()
        elif status:
            facilities = Facility.query.filter(Facility.facility_status == status).all()

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