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
    facility_address = db.Column(db.String, nullable=True) # TODO - check on address as nullable
    facility_state = db.Column(db.String, nullable=False)
    facility_zip = db.Column(db.String, nullable=False) #TODO - change to int once data is cleaned
    facility_county = db.Column(db.String, nullable=True)
    facility_capacity = db.Column(db.Integer, nullable=False)
    complaint_count = db.Column(db.String,nullable=False) #TO DO - update this field
    facility_status = db.Column(db.String, nullable=False)


    ### DB Relationships ###
        # visitations --> Visitation Class
        # citations --> Citation Class


    def __repr__ (self):
        """Display info about facility"""

        return f"""<facility_id={self.facility_id} 
                    facility_type={self.facility_type} 
                    facility_name={self.facility_name} 
                    facility_zip={self.facility_zip}
                    facility_status={self.facility_status} 
                    complaint_count={self.complaint_count}>
                    """


class Visitation(db.Model):
    """Class model for facility visitations"""

    __tablename__ = 'visitations'

    visitation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitation_date = db.Column(db.DateTime(timezone=False), nullable=False) ###Not sure if just "date" works
    is_inspection = db.Column(db.Boolean, nullable=False)
    facility_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.facility_id'), nullable=False)

    
    ### DB Relationships ###
    facilities = db.relationship('Facility', backref='visitations')
    # citations --> Citation Class


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
    citation_date = db.Column(db.DateTime(timezone=False), nullable=False)
    visitation_id = db.Column(db.Integer, 
                    db.ForeignKey('visitations.visitation_id'), nullable=True)
                    #Keeping nullable for now (for dates that don't match up btwn citation and visitation)
                    #Check into percentage of NULL cells here after seeded & re-evaluate
    citation_type = db.Column(db.String(1), nullable=False) 
    citation_code = db.Column(db.String, 
                    db.ForeignKey('cit_definitions.citation_code'), nullable=False)
    facility_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.facility_id'), nullable=False)

    ### DB Relationships ###
    visitations = db.relationship('Visitation', backref='citations')
    citation_defs = db.relationship('CitationDefinition', backref='citations')
    facilities = db.relationship('Facility', backref='citations')


    def __repr__(self):
        """Info about citation"""

        return f"""<citation_id={self.citation_id} 
                    citation_date={self.citation_date}
                    citation_type={self.citation_type} 
                    citation_code={self.citation_code}>
                    """


class CitationDefinition(db.Model):
    """Class model for facility licensing violations"""

    __tablename__ = 'cit_definitions'

    cit_def_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    citation_code = db.Column(db.String, nullable=False)
    citation_description = db.Column(db.String, nullable=False)
    citation_url = db.Column(db.String, nullable=False)

    # DB Relationships ###
        # citations --> Citation Class

    def __repr__(self):
        """Info about citation definition"""

        return f"""<cit_def_id={self.cit_def_id} 
                    citation_code={self.citation_code}
                    citation_description={self.citation_description}
                    citation_url={self.citation_url}
                    """


##### Helper functions ########################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///test2' ##TO DO - update 
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

