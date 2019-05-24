"""Utility file to seed data into project db from CA state data in seed_data/"""


##### Import Libraries #######################################################

from sqlalchemy import func, create_engine
from model import db, Facility, Visitation, Citation, CitationDefinition, connect_to_db
from server import app
from datetime import *
import csv
from dateutil.parser import *

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

        address = ""
        for char in row[6]:
            if char != "'":
                address += char

        if row[30] == "No Complaints":
            no_complaints = True
        else: 
            no_complaints = False

        facility = Facility(
                    f_type = row[0],
                    number = row[1], 
                    name = name,
                    phone = row[5],
                    address = address, 
                    city = row[7],
                    state = row[8], 
                    f_zip = int(row[9][:6]), 
                    county = row[10], 
                    capacity = row[12],
                    no_complaints = no_complaints, 
                    status = row[13],
                    )

        db.session.add(facility)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< facilities loaded >>>>>>>>>>>>>>>>>>>')


def load_visitations(processed_file):
    """Load visitations from file"""

    for row in processed_file:
        if row[23] != '':

            ##################### split cell by comma ##########################
            visit_list = row[23].split("','")
            inspection_list = row[24].split("','")

            for inspect_date in inspection_list:
                # Loop through list of inspection dates contained in same CSV cell

                inspect_date = inspect_date.strip()

                if "/" in inspect_date:
                    parse(inspect_date, dayfirst=False)
                else:
                    inspection_list.remove(inspect_date)        

            for visit_date in visit_list:
                # Loop through list of visit dates contained in same CSV cell
                
                visit_date = visit_date.strip()

                if "/" not in visit_date:
                    visit_list.remove(visit_date)
                elif "/" in visit_date:
                    parse(visit_date, dayfirst=False)
                
                    if visit_date in inspection_list:
                        inspection=True
                    else:
                        inspection=False
                    
                    facility = Facility.query.filter_by(number=f'{row[1]}').one()

                    visitation = Visitation(
                        date = visit_date,
                        is_inspection = inspection,
                        f_id = facility.f_id,
                        )

                    db.session.add(visitation)

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< visitations loaded >>>>>>>>>>>>>>>>>>>')


def load_citations(processed_file):
    """Load citations from file"""

    for row in processed_file:
        
        if row[21] != '':

            facility = Facility.query.filter_by(number=f'{row[1]}').one()
            
            ##################### split cell by space ##########################
            cit_list = row[22].split("','")
            code_list = row[21].split("','")
        
            index = 0
            for date in cit_list:
                ## Loop through list of citation dates contained in CSV cell
                
                #citation_date = citation_date.strip()
                date = parse(date.strip(), dayfirst=False)

                if len(cit_list) == len(code_list):
                    code = code_list[index].strip()
                else:
                    code = None

                visit = Visitation.query.filter_by(f_id = facility.f_id, date=date).first()
                
                if visit:
                    v_id = visit.v_id
                else:
                    v_id = None

                citation = Citation(
                        date = date,
                        code = code,
                        f_id = facility.f_id,
                        v_id = v_id,
                    )

                db.session.add(citation)

                if index < (len(cit_list) -1):
                    index += 1

    db.session.commit()

    print ('<<<<<<<<<<<<<<<< citations loaded >>>>>>>>>>>>>>>>>>>')


def load_cit_definitions(processed_file):
    """Load citation definitions from file"""

    for row in processed_file:

        cit_def = CitationDefinition(
            code=code,
            description=description,
            url=url,
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

