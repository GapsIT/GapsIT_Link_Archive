from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(
        db.String(100), nullable=False
    )  # Only employees with this position can see
    created_by = db.Column(db.String(100))  # Admin username who created it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Link {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "position": self.position,
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
