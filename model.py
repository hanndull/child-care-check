from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##### COMPOSE ORM #####

class Facility(db.Model):
    """Class model for facility information"""

    __tablename__ = 'facilities'

    facility_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_type = db.Column(db.String(30), nullable=False)
    facility_number = db.Column(db.String(12), nullable=False)
    facility_name = db.Column(db.String, nullable=False)
    facility_phone = db.Column(db.String(20), nullable=True) # TODO - check on phone num as str
    facility_address = db.Column(db.String, nullable=True) # TODO - check on address as nullable
    facility_state = db.Column(db.String(2), nullable=False)
    facility_zip = db.Column(db.Integer(5), nullable=False)
    facility_county = db.Column(db.String, nullable=True)
    facility_capacity = db.Column(db.Integer(5), nullable=False)
    complaint_count = db.Column(db.Integer,nullable=False)
    facility_status = db.Column(db.String, nullable=False)

    def __repr__ (self):
        """Display info about facility"""

        return f"""<facility_id={facility_id} facility_type={facility_type} 
                    facility_name={facility_name} facility_zip={facility_zip}
                    facility_status={facility_status} 
                    complaint_count={complaint_count}>
                    """


class Visitation(db.Model):
    """Class model for facility visitations"""

    __tablename__ = 'violations'

    visitation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitation_date = 
    is_inspection = 
    facility_id = 

    def __repr__(self):
        """Info about visitation"""

        return f"""<visitation_id={visitation_id} 
                    visitation_date={visitation_date}
                    facility_id= {facility_id}>
                    """


class Citation(db.Model):
    """Class model for facility citations"""

    __tablename__ = 'citations'

    citation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    citation_date = 
    visitation_id = 
    citation_type = 
    citation_code = 
    facility_id = 

    def __repr__(self):
        """Info about citation"""

        return f"""<citation_id={citation_id} citation_date={citation_date}
                    citation_type={citation_type} citation_code={citation_code}>
                    """


class CitationDefinitions(db.Model):
    """Class model for facility licensing violations"""

    __tablename__ = 'cit_definitions'

    cit_def_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    citation_code = 
    citation_description = 
    citation_url = 

    def __repr__(self):
        """Info about citation definition"""

        return f"""<cit_def_id={cit_def_id} citation_code={citation_code}
                    citation_description={citation_description}
                    citation_url={citation_url}
                    """


##############################################################################
##### Helper functions #####

def init_app():
    """Flask app for use of SQL Alchemy"""
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///project'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # If you run this module interactively, you will be able to work 
    # with the database directly.

    init_app()