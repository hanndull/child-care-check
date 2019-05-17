"""Utility file to seed data into project db from CA state data in seed_data/"""


##### Import Libraries #######################################################

from sqlalchemy import func, create_engine
from model import db, Facility, Visitation, Citation, CitationDefinition, connect_to_db
from server import app
from datetime import datetime 
import csv
from random import choice 

##### Load Data to DB ########################################################

def load_file(file_path):

    with open(file_path, newline='') as csvfile:
        """return ea row as list of strings within an object of full document"""
        ### NOTE: prior to loading doc, should wrap commas in cells with quotes

        processed_file = csv.reader(csvfile, delimiter=',')

        print('<<<<<<<<<<<<<<<< initiate csv row processing >>>>>>>>>>>>>>>>>>>')

        rows = []

        for row in processed_file:
            rows.append(row)

        print('<<<<<<<<<<<<<<<< complete csv row processing >>>>>>>>>>>>>>>>>>>')

        return rows


def load_facilities(processed_file):
    """Load facilities from file""" 

    for row in processed_file:
        
        name = ""
        for char in row[2]:
            if char != "'":
                name += char

        facility = Facility(
                    facility_type = row[0],
                    facility_number = row[1], 
                    facility_name = name,
                    facility_phone = row[5],
                    facility_address = row[6], 
                    facility_state = row[8], 
                    facility_zip = row[9], 
                    facility_county = row[10], 
                    facility_capacity = row[12],
                    complaint_count = row[30], 
                    facility_status = row[13],
                    )

        db.session.add(facility)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< facilities loaded >>>>>>>>>>>>>>>>>>>')


def load_visitations(processed_file):
    """Load visitations from file"""

    for row in processed_file:
        if row[23] != '':
            
            facility = Facility.query.filter_by(facility_number=f'{row[1]}').one()

            ##################### split cell by space ##########################
            visit_list = row[23].split("','")
            inspection_list = row[24].split("','")

            for visit_date in visit_list:
                # Loop through list of visit dates contained in same CSV cell
                if visit_date in inspection_list:
                    inspection=True
                else:
                    inspection=False
                
                visit_date = visit_date.strip()

                ### TODO - insert datetime logic here

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
    ### NOTE: load_cit_definitions must be run prior to this function

    for row in processed_file:
        
        if row[21] != '':

            facility = Facility.query.filter_by(facility_number=f'{row[1]}').one()
            citation_definitions = CitationDefinition.query.all() ### TODO - Make sure this functions 
            
            ##################### split cell by space ##########################
            cit_list = row[22].split("','")
        
            for citation_date in cit_list:
                ## Loop through list of citation dates contained in CSV cell
                
                #citation_type = choice(citation_definitions)
                ## Choose random choice for a citation type 
                ## (real CSV data too messy for MVP timeframe)
                
                citation_date = citation_date.strip()

                ### TODO - insert datetime logic here

                citation = Citation(
                        citation_date = citation_date,
                        #citation_type = citation_type.citation_code,
                        facility_id = facility.facility_id,
                    )

                db.session.add(citation)
                
                # if index < (len(cit_type)-1):
                #     index += 1

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< citations loaded >>>>>>>>>>>>>>>>>>>')


def load_cit_definitions(processed_file):
    """Load citation definitions from file"""
    
    ### TO DO -- find way to scrape thru documentation of citation types
    # Gather into doc for this seeding

    for row in processed_file:
        
        ### TODO - Add in logic of how file cells will correlate to fields

        cit_def = CitationDefinition(
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
    ### TO DO - Figure out how the 2 main files will be seeded properly!

    ## In case tables haven't been created, create them
    db.create_all()

    ## Delete all rows in table to avoid adding duplicate users
    Facility.query.delete()
    Visitation.query.delete()
    Citation.query.delete()
    CitationDefinition.query.delete()

    ## Call all seeding functions here 

    # definitions_file = load_file('excel/FILENAME')
    # load_cit_definitions(definitions_file)

    processed_file1 = load_file('excel/centerdata.csv')
    load_facilities(processed_file1)
    load_visitations(processed_file1)
    load_citations(processed_file1)

    # processed_file2 = load_file('excel/homedata.csv')
    # load_facilities(processed_file2)
    # ### TODO - figure out why process throws error here
    # load_visitations(processed_file2)
    # load_citations(processed_file2)

