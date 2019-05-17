"""CA Child Care Licensing Violations"""

# https://github.com/users/hanndull/projects/2

##### Import Libraries #######################################################

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Facility, Visitation, Citation, CitationDefinition

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