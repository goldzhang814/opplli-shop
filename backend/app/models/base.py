from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, MappedColumn


class TimestampMixin:
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
