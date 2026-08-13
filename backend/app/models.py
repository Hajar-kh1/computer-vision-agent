"""SQLAlchemy ORM models — predictions table (spec §16).

Required columns at minimum:
    id, image_name, predicted_class, confidence,
    inference_ms, model_version, created_at

Recommended additional columns:
    image_path, top_k_predictions (JSON), image_hash, request_id

TODO (Student 2 — Backend Engineer):
- Define class Prediction(Base) with the columns above.
- top_k_predictions as JSON (SQLAlchemy JSON type).
- created_at with server_default=func.now().
"""

# from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
#
# class Prediction(Base):
#     __tablename__ = "predictions"
#     id = Column(Integer, primary_key=True, index=True)
#     image_name = Column(String, nullable=False)
#     predicted_class = Column(String, nullable=False)
#     confidence = Column(Float, nullable=False)
#     inference_ms = Column(Float, nullable=False)
#     model_version = Column(String, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
