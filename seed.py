"""Utility file to seed data into project db from CA state data in seed_data/"""


##### Import Libraries #######################################################

from sqlalchemy import func 
from model import connect_to_db, db, Facility, Visitation, 
                    Citation, CitationDefinition
from server import app
from datetime import datetime 


##### Load Data to DB ########################################################

def load_facilities(file):
    """Load facilities from file""" 
    ### TO DO - Figure out how the 2 files will be parsed
    ### Maybe add file name param??

    ### TO DO - Add logic here

    User.query.delete()
    # Delete all rows in table to avoid adding duplicate users
  
    for row in open(f"seed_data/{file}"):
        # Read file and insert data
        row = row.rstrip()
        #[TO DO - list all table name fields here] = row.split("|")

        facility = Facility( #TO DO - list all fields here
                            )

        db.session.add(facility) # add to the sql session

    db.session.commit()



    print ('<<<<<<<<<<<<<<<< facilities loaded >>>>>>>>>>>>>>>>>>>')


def load_visitations():
    """Load visitations from file"""

    ### TO DO - Add logic here

    print ('<<<<<<<<<<<<<<<< visitations loaded >>>>>>>>>>>>>>>>>>>')


def load_citations():
    """Load citations from file"""

    ### TO DO - Add logic here

    print ('<<<<<<<<<<<<<<<< citations loaded >>>>>>>>>>>>>>>>>>>')


def load_cit_definitions():
    """Load citation definitions from file"""
    ### TO DO -- find way to scrape thru documentation of citation types
    # Gather into doc for this seeding

    ### TO DO - Add logic here

    print ('<<<<<<<<<<<<<<<< cit defs loaded >>>>>>>>>>>>>>>>>>>')


##### Dunder Main ############################################################

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data

    # Call all seeding functions here 
    load_facilities()
    load_visitations()
    load_citations()
    load_cit_definitions()