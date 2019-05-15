"""Utility file to seed data into project db from CA state data in seed_data/"""


##### Import Libraries #######################################################

from sqlalchemy import func, create_engine
from model import db, Facility, Visitation, Citation, CitationDefinition, connect_to_db
from server import app
from datetime import datetime 
import csv

##### Load Data to DB ########################################################

def load_file(file_path):

    with open(file_path, newline='') as csvfile:
        """return ea row as list of strings within an object of full document"""

        processed_file = csv.reader(csvfile, delimiter=',')

        print('<<<<<<<<<<<<<<<< initiate csv row processing >>>>>>>>>>>>>>>>>>>')

        rows = []

        for row in processed_file:
            rows.append(row)

        print('<<<<<<<<<<<<<<<< complete csv row processing >>>>>>>>>>>>>>>>>>>')

        return rows


def load_facilities(processed_file):
    """Load facilities from file""" 
    ### TO DO - Figure out how the 2 files will be parsed

    ## Delete all rows in table to avoid adding duplicate users
    Facility.query.delete()

    for row in processed_file:
        
        facility = Facility(
                    facility_type = row[0],
                    facility_number = row[1], 
                    facility_name = row[2],
                    facility_phone = row[5],
                    facility_address = row[6], 
                    facility_state = row[8], 
                    facility_zip = row[9], 
                    facility_county = row[10], 
                    facility_capacity = int(row[12]),
                    complaint_count = row[30], 
                    facility_status = row[13],
                    )

        db.session.add(facility)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< facilities loaded >>>>>>>>>>>>>>>>>>>')


def load_visitations(processed_file):
    """Load visitations from file"""

    Visitation.query.delete()

    for row in processed_file:
        if row[23] != '':
            
            facility = Facility.query.filter_by(facility_number=f'{row[1]}').one()

            ##################### split cell by space ##########################
            visit_list = row[23].split()
            inspection_list = row[24].split()

            for visit_date in visit_list:
                # Loop through list of visit dates contained in same CSV cell
                if visit_date in inspection_list:
                    inspection=True
                else:
                    inspection=False
                
                visitation = Visitation(
                    visitation_date = visit_date,
                    is_inspection = inspection,
                    facility_id = facility.facility_id,
                    )

                db.session.add(visitation)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< visitations loaded >>>>>>>>>>>>>>>>>>>')


def load_citations(processed_file):
    """Load citations from file"""

    Citation.query.delete()

    for row in processed_file:
        
        if row[21] != '':

            facility = Facility.query.filter_by(facility_number=f'{row[1]}').one()
            
            ##################### split cell by space ##########################
            cit_list = row[22].split()
            cit_type = row[21].split()

            index = 0

            for citation_date in cit_list:
                # Loop through list of citation dates contained in CSV cell
                ### TODO - Consider whether useful to count against date
                citation_type = cit_type[index]

                citation = Citation(
                        citation_date = citation_date,
                        citation_type = citation_type,
                        facility_id = facility.facility_id,
                    )

                db.session.add(citation)
                
                if index < (len(cit_type)-1):
                    index += 1

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< citations loaded >>>>>>>>>>>>>>>>>>>')


def load_cit_definitions(processed_file):
    """Load citation definitions from file"""
    
    ### TO DO -- find way to scrape thru documentation of citation types
    # Gather into doc for this seeding

    CitationDefinition.query.delete()

    for row in processed_file:
        
        ### TODO - Add in logic of how file cells will correlate to fields

        cit_def = CitationDefinition(
            cit_def_id=cit_def_id,
            citation_code=citation_code,
            citation_description=citation_description,
            citation_url=citation_url,
            )

        db.session.add(cit_def)

    print ('<<<<<<<<<<<<<<<< cit defs loaded >>>>>>>>>>>>>>>>>>>')
    db.session.commit()


##### Dunder Main ############################################################

if __name__ == "__main__":
    connect_to_db(app)

    ## In case tables haven't been created, create them
    db.create_all()

    ## Import different types of data ##??????

    ## Call all seeding functions here 
    processed_file = load_file('excel/fullfile_test.csv')
    load_facilities(processed_file)
    load_visitations(processed_file)
    load_citations(processed_file)

    # definitions_file = load_file('excel/FILENAME')
    # load_cit_definitions(definitions_file)