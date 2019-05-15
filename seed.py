"""Utility file to seed data into project db from CA state data in seed_data/"""


##### Import Libraries #######################################################

from sqlalchemy import func, create_engine
from model import db, Facility, Visitation, Citation, CitationDefinition, connect_to_db
from server import app
from datetime import datetime 

##### Load Data to DB ########################################################

def load_facilities(file_path):
    """Load facilities from file""" 
    ### TO DO - Figure out how the 2 files will be parsed

    ## Delete all rows in table to avoid adding duplicate users
    Facility.query.delete()

    for row in open(file_path):

        row = row.rstrip()
        row = row.split(",")
        
        facility_type, facility_number, facility_name, facility_phone, facility_address, facility_state, facility_zip, facility_county, facility_capacity, complaint_count, facility_status = row
        
        facility = Facility(
                    facility_type=facility_type, 
                    facility_number=facility_number, 
                    facility_name=facility_name, 
                    facility_phone=facility_phone, 
                    facility_address=facility_address, 
                    facility_state=facility_state, 
                    facility_zip=facility_zip, 
                    facility_county=facility_county, 
                    facility_capacity=facility_capacity, 
                    complaint_count=complaint_count, 
                    facility_status=facility_status,
                    )

        db.session.add(facility)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< facilities loaded >>>>>>>>>>>>>>>>>>>')


    ##PAST TEST CODE 
    # with open(file_path, 'r') as file: # r = open for reading (default)
    #     ### FROM: https://stackoverflow.com/a/34523707 + https://docs.sqlalchemy.org/en/13/core/engines.html
    #     engine = create_engine('postgres:///test1').raw_connection() ###CHANGE TO NEW DB NAME!
    #     cursor = engine.cursor()
    #     command = '''COPY facilities(facility_type, facility_number, 
    #                 facility_zip, facility_county, facility_capacity,
    #                 facility_status, facility_complaint_visits, facility_id) 
    #                 FROM {file_path} DELIMITER ',' CSV HEADER;)
    #                 ''' #http://www.postgresqltutorial.com/import-csv-file-into-posgresql-table/
        
    #     cursor.copy_expert(command, file)

    #     engine.commit()


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

    # Import different types of data ##??????

    ## Call all seeding functions here 
    # load_facilities('excel/facilities_test.csv')
    # load_visitations()
    # load_citations()
    # load_cit_definitions()