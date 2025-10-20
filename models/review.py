from extensions import db

class Review(db.Model):
    __tablename__ = "reviews"

    # define the enum type for status
    review_status_enum = db.Enum("draft", "published", "flagged", name="review_status_enum")

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Numeric(2, 1), nullable=False)  # 0.5–5.0 step 0.5
    body = db.Column(db.Text, nullable=True)
    status = db.Column(review_status_enum, nullable=False, default="draft")

    film_id = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    published_at = db.Column(db.DateTime, nullable=True)
    flagged_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        # one review per user-film
        db.UniqueConstraint("film_id", "user_id", name="uq_review_user_film"),

        # enforce allowed ratings (0.5..5.0 in 0.5 steps)
        db.CheckConstraint(
            "rating IN (0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0)",
            name="ck_review_rating"
        ),
        # if status is published, published_at must not be null
        db.CheckConstraint(
            "(status <> 'published') OR (published_at IS NOT NULL)",
            name="ck_review_published_time"
        ),
    )

    # ========== Relationships ==========
    film = db.relationship("Film", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")
