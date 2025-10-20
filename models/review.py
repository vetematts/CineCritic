"""Review model:

Represents a user’s review of a film, including rating, body text, and status
(draft, published, flagged).

Attributes:
- id (int): Primary key.
- rating (decimal): Rating between 0.5–5.0 in 0.5 steps.
- body (text | None): Optional review content.
- status (enum): Review state (draft, published, flagged).
- film_id (int): Foreign key to Film (CASCADE on delete).
- user_id (int): Foreign key to User (CASCADE on delete).
- created_at (datetime): Auto-set when created.
- updated_at (datetime): Auto-set on update.
- published_at (datetime | None): Timestamp when published.
- flagged_at (datetime | None): Timestamp when flagged.

Constraints:
- One review per (film, user).
- Rating must be one of the allowed step values.
- Published reviews must have a published_at timestamp.

Relationships:
- Linked to Film and User via back_populates.
"""

from extensions import db

class Review(db.Model):
    __tablename__ = "reviews"

    # enum for status to keep values consistent
    review_status_enum = db.Enum("draft", "published", "flagged", name="review_status_enum")

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Numeric(2, 1), nullable=False)            # 0.5–5.0 (step 0.5)
    body = db.Column(db.Text, nullable=True)
    status = db.Column(review_status_enum, nullable=False, default="draft")

    film_id = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    published_at = db.Column(db.DateTime, nullable=True)
    flagged_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("film_id", "user_id", name="uq_review_user_film"),
        db.CheckConstraint("rating IN (0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0)", name="ck_review_rating"),
        db.CheckConstraint("(status <> 'published') OR (published_at IS NOT NULL)", name="ck_review_published_time"),
    )

    # ========== Relationships ==========
    film = db.relationship("Film", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")
