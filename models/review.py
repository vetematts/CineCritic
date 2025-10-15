# models/review.py
from extensions import db

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Numeric(2, 1), nullable=False)  # 0.5–5.0 step 0.5
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="draft")  # draft|published|flagged

    film_id = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    published_at = db.Column(db.DateTime, nullable=True)
    flagged_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("film_id", "user_id", name="uq_review_user_film"),
        db.CheckConstraint(
            "status IN ('draft','published','flagged')",
            name="ck_review_status"
        ),
    )
