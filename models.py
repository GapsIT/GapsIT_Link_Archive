from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    positions = db.Column(
        db.Text, nullable=False
    )  # Changed: Store as comma-separated values
    created_by = db.Column(db.String(100))  # Admin username who created it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Link {self.title}>"

    def get_positions_list(self):
        """Return positions as a list"""
        if not self.positions:
            return []
        return [pos.strip() for pos in self.positions.split(",") if pos.strip()]

    def set_positions_list(self, positions_list):
        """Set positions from a list"""
        self.positions = ",".join(positions_list)

    def has_position(self, position):
        """Check if link has a specific position"""
        return position in self.get_positions_list()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "positions": self.get_positions_list(),  # Changed: Return as list
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
