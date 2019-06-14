from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##### COMPOSE ORM ############################################################

class Facility(db.Model):
    """Class model for facility information"""

    __tablename__ = 'facilities'

    f_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    f_type = db.Column(db.String, nullable=False)
    number = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True) 
    address = db.Column(db.String, nullable=False) 
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    f_zip = db.Column(db.Integer, nullable=False) 
    county = db.Column(db.String, nullable=True)
    capacity = db.Column(db.String, nullable=False) 
    no_complaints = db.Column(db.String,nullable=False) 
    status = db.Column(db.String, nullable=False)
    latitude = db.Column(db.String, nullable=True)
    longitude = db.Column(db.String, nullable = True)
    google_place_id = db.Column(db.String, nullable = True)

    ### DB Relationships ###
        ### visitations --> Visitation Class
        ### citations --> Citation Class


    def __repr__ (self):
        """Display info about facility"""

        return f"""<f_id={self.f_id} 
                    f_type={self.f_type} 
                    name={self.name} 
                    f_zip={self.f_zip}
                    status={self.status} 
                    no_complaints={self.no_complaints}>
                    """


class Visitation(db.Model):
    """Class model for facility visitations"""

    __tablename__ = 'visitations'

    v_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    is_inspection = db.Column(db.String, nullable=True)
    f_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.f_id'), nullable=True)
    
    ### DB Relationships ###
    facilities = db.relationship('Facility', backref='visitations')
        ### citations --> Citation Class


    def __repr__(self):
        """Info about visitation"""

        return f"""<v_id={self.v_id} 
                    date={self.date}
                    f_id= {self.f_id}>
                    """


class Citation(db.Model):
    """Class model for facility citations"""

    __tablename__ = 'citations'

    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.String, nullable=True)     
    v_id = db.Column(db.Integer, 
                    db.ForeignKey('visitations.v_id'), nullable=True)
    cd_id = db.Column(db.Integer, 
                    db.ForeignKey('cit_definitions.cd_id'), nullable=True)
        ### Retaining cit_def_id as FKey, although most will be null--
        ### Only linking a few clean citations for purposes of demo
    f_id = db.Column(db.Integer, 
                    db.ForeignKey('facilities.f_id'), nullable=True)

    ### DB Relationships ###
    visitations = db.relationship('Visitation', backref='citations')
    cit_definitions = db.relationship('CitationDefinition', backref='citations')
    facilities = db.relationship('Facility', backref='citations', lazy='joined')

    def __repr__(self):
        """Info about citation"""

        return f"""<c_id={self.c_id} 
                    code={self.code}
                    date={self.date}>
                    """ 


class CitationDefinition(db.Model):
    """Class model for facility licensing violations"""

    __tablename__ = 'cit_definitions'

    cd_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=True)

    ### DB Relationships ###
        ### citations --> Citation Class


    def __repr__(self):
        """Info about citation definition"""

        return f"""<cd_id={self.cd_id} 
                    code={self.code}
                    description={self.description}
                    url={self.url}>
                    """


##### Helper functions ########################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///licensinginfo'
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

