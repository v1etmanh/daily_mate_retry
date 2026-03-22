from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base


class WeatherCache(Base):
    """
    Persistent record of cached weather data per geo-cell.
    Primary cache is Redis (TTL-based); this table serves as fallback / audit log.

    Geo-cell key formula:
        grid_lat = round(lat / 0.1) * 0.1
        grid_lon = round(lon / 0.1) * 0.1
        cache_key = f"weather:{grid_lat}:{grid_lon}"
    """
    __tablename__ = "weather_caches"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(128), nullable=False, unique=True, index=True)  # "weather:{lat}:{lon}"

    grid_lat = Column(Float, nullable=False)
    grid_lon = Column(Float, nullable=False)

    # Raw weather data snapshot
    raw_data = Column(JSON, nullable=True)          # Full API response

    # Normalized WeatherVector (6 dimensions, [0,1])
    temperature_norm = Column(Float, nullable=True)
    humidity_norm = Column(Float, nullable=True)
    wind_speed_norm = Column(Float, nullable=True)
    precipitation_norm = Column(Float, nullable=True)
    heat_stress_index = Column(Float, nullable=True)
    cold_stress_index = Column(Float, nullable=True)

    # TTL metadata
    ttl_minutes = Column(Integer, default=30)       # 15 / 30 / 60 min based on conditions
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<WeatherCache key={self.cache_key} fetched_at={self.fetched_at}>"