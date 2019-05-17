from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##### COMPOSE ORM ############################################################

class Facility(db.Model):
    """Class model for facility information"""

    __tablename__ = 'facilities'

    facility_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_type = db.Column(db.String, nullable=False)
    facility_number = db.Column(db.String, nullable=False)
    facility_name = db.Column(db.String, nullable=False)
    facility_phone = db.Column(db.String, nullable=True) # TODO - check on phone num as str
    facility_address = db.Column(db.String, nullable=False) 
    facility_city = db.Column(db.String, nullable=False)
    facility_state = db.Column(db.String, nullable=False)
    facility_zip = db.Column(db.String, nullable=False) #TODO - change to int once data is cleaned
    facility_county = db.Column(db.String, nullable=True)
    facility_capacity = db.Column(db.String, nullable=False) #TODO - change back to int
    no_complaints = db.Column(db.String,nullable=False) #TO DO - update this field
    facility_status = db.Column(db.String, nullable=False)

    ### DB Relationships ###
        ### visitations --> Visitation Class
        ### citations --> Citation Class


    def __repr__ (self):
        """Display info about facility"""

        return f"""<facility_id={self.facility_id} 
                    facility_type={self.facility_type} 
                    facility_name={self.facility_name} 
                    facility_zip={self.facility_zip}
                    facility_status={self.facility_status} 
                    no_complaints={self.no_complaints}>
                    """


class Visitation(db.Model):
    """Class model for facility visitations"""

    __tablename__ = 'visitations'

    visitation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitation_date = db.Column(db.String, nullable=False)
    is_inspection = db.Column(db.String, nullable=True)
    facility_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.facility_id'), nullable=True)
    
    ### DB Relationships ###
    facilities = db.relationship('Facility', backref='visitations')
        ### citations --> Citation Class


    def __repr__(self):
        """Info about visitation"""

        return f"""<visitation_id={self.visitation_id} 
                    visitation_date={self.visitation_date}
                    facility_id= {self.facility_id}>
                    """


class Citation(db.Model):
    """Class model for facility citations"""

    __tablename__ = 'citations'

    citation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    citation_date = db.Column(db.String, nullable=False)
    citation_code = db.Column(db.String, nullable=True)     
    visitation_id = db.Column(db.Integer, 
                    db.ForeignKey('visitations.visitation_id'), nullable=True)
    cit_def_id = db.Column(db.Integer, 
                    db.ForeignKey('cit_definitions.cit_def_id'), nullable=True)
        ### Retaining cit_def_id as FKey, although most will be null--
        ### Only linking a few clean citations for purposes of demo
    facility_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.facility_id'), nullable=True)

    ### DB Relationships ###
    visitations = db.relationship('Visitation', backref='citations')
    cit_definitions = db.relationship('CitationDefinition', backref='citations')
    facilities = db.relationship('Facility', backref='citations')


    def __repr__(self):
        """Info about citation"""

        return f"""<citation_id={self.citation_id} 
                    citation_code={self.citation_code}
                    citation_date={self.citation_date}>
                    """ 


class CitationDefinition(db.Model):
    """Class model for facility licensing violations"""

    __tablename__ = 'cit_definitions'

    cit_def_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    citation_code = db.Column(db.String, nullable=True)
    citation_description = db.Column(db.String, nullable=True)
    citation_url = db.Column(db.String, nullable=True)

    ### DB Relationships ###
        ### citations --> Citation Class


    def __repr__(self):
        """Info about citation definition"""

        return f"""<cit_def_id={self.cit_def_id} 
                    citation_code={self.citation_code}
                    citation_description={self.citation_description}
                    citation_url={self.citation_url}>
                    """


##### Helper functions ########################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///test1' ##TO DO - update 
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # If you run this module interactively, you will be able to work 
    # with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")

