from typing import Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from geopic_tag_reader.model import PictureType

try:
    import pyexiv2  # type: ignore
    import timezonefinder  # type: ignore
    import pytz
except ImportError:
    raise Exception(
        """Impossible to write the exif tags without the '[write-exif]' dependency (that will need to install libexiv2).
Install this package with `pip install geopic-tag-reader[write-exif]` to use this function"""
    )

tz_finder = timezonefinder.TimezoneFinder()


@dataclass
class PictureMetadata:
    capture_time: Optional[datetime] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    picture_type: Optional[PictureType] = None


def writePictureMetadata(picture: bytes, metadata: PictureMetadata) -> bytes:
    """
    Override exif metadata on raw picture and return updated bytes
    """
    if not metadata.capture_time and not metadata.longitude and not metadata.latitude and not metadata.picture_type:
        return picture

    img = pyexiv2.ImageData(picture)

    updated_exif = {}
    updated_xmp = {}

    if metadata.capture_time:
        if metadata.capture_time.utcoffset() is None:
            metadata.capture_time = localize(metadata.capture_time, img)

        # for capture time, override GPSInfo time and DatetimeOriginal
        updated_exif["Exif.Photo.DateTimeOriginal"] = metadata.capture_time.strftime("%Y-%m-%d %H:%M:%S")
        offset = metadata.capture_time.utcoffset()
        if offset is not None:
            updated_exif["Exif.Photo.OffsetTimeOriginal"] = format_offset(offset)

        utc_dt = metadata.capture_time.astimezone(tz=pytz.UTC)
        updated_exif["Exif.GPSInfo.GPSDateStamp"] = utc_dt.strftime("%Y-%m-%d")
        updated_exif["Exif.GPSInfo.GPSTimeStamp"] = utc_dt.strftime("%H/1 %M/1 %S/1")

    if metadata.latitude is not None:
        updated_exif["Exif.GPSInfo.GPSLatitudeRef"] = "N" if metadata.latitude > 0 else "S"
        updated_exif["Exif.GPSInfo.GPSLatitude"] = _to_exif_dms(metadata.latitude)

    if metadata.longitude is not None:
        updated_exif["Exif.GPSInfo.GPSLongitudeRef"] = "E" if metadata.longitude > 0 else "W"
        updated_exif["Exif.GPSInfo.GPSLongitude"] = _to_exif_dms(metadata.longitude)

    if metadata.picture_type is not None:
        updated_xmp["Xmp.GPano.ProjectionType"] = metadata.picture_type.value

    if updated_exif:
        img.modify_exif(updated_exif)
    if updated_xmp:
        img.modify_xmp(updated_xmp)

    return img.get_bytes()


def format_offset(offset: timedelta) -> str:
    """Format offset for OffsetTimeOriginal. Format is like "+02:00" for paris offset
    >>> format_offset(timedelta(hours=5, minutes=45))
    '+05:45'
    >>> format_offset(timedelta(hours=-3))
    '-03:00'
    """
    offset_hour, remainer = divmod(offset.total_seconds(), 3600)
    return f"{'+' if offset_hour >= 0 else '-'}{int(abs(offset_hour)):02}:{int(remainer/60):02}"


def localize(dt: datetime, metadata: pyexiv2.ImageData) -> datetime:
    """
    Localize a datetime in the timezone of the picture
    If the picture does not contains GPS position, the datetime will not be modified.
    """
    exif = metadata.read_exif()
    lon = exif["Exif.GPSInfo.GPSLongitude"]
    lon_ref = exif.get("Exif.GPSInfo.GPSLongitudeRef", "E")
    lat = exif["Exif.GPSInfo.GPSLatitude"]
    lat_ref = exif.get("Exif.GPSInfo.GPSLatitudeRef", "N")

    if not lon or not lat:
        return dt  # canot localize, returning same date

    lon = _from_dms(lon) * (1 if lon_ref == "E" else -1)
    lat = _from_dms(lat) * (1 if lat_ref == "N" else -1)

    tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
    if not tz_name:
        return dt  # cannot find timezone, returning same date

    tz = pytz.timezone(tz_name)

    return tz.localize(dt)


def _from_dms(val: str) -> float:
    """Convert exif lat/lon represented as degre/minute/second into decimal
    >>> _from_dms("1/1 55/1 123020/13567")
    1.9191854417991367
    >>> _from_dms("49/1 0/1 1885/76")
    49.00688961988304
    """
    deg_raw, min_raw, sec_raw = val.split(" ")
    deg_num, deg_dec = deg_raw.split("/")
    deg = float(deg_num) / float(deg_dec)
    min_num, min_dec = min_raw.split("/")
    min = float(min_num) / float(min_dec)
    sec_num, sec_dec = sec_raw.split("/")
    sec = float(sec_num) / float(sec_dec)

    return float(deg) + float(min) / 60 + float(sec) / 3600


def _to_dms(value: float) -> Tuple[int, int, float]:
    """Return degree/minute/seconds for a decimal
    >>> _to_dms(38.889469)
    (38, 53, 22.0884)
    >>> _to_dms(43.7325)
    (43, 43, 57.0)
    >>> _to_dms(-43.7325)
    (43, 43, 57.0)
    """
    value = abs(value)
    deg = int(value)
    min = (value - deg) * 60
    sec = (min - int(min)) * 60

    return deg, int(min), round(sec, 8)


def _to_exif_dms(value: float) -> str:
    """Return degree/minute/seconds string formated for the exif metadata for a decimal
    >>> _to_exif_dms(38.889469)
    '38/1 53/1 55221/2500'
    """
    from fractions import Fraction

    d, m, s = _to_dms(value)
    f = Fraction.from_float(s).limit_denominator()  # limit fraction precision
    num_s, denomim_s = f.as_integer_ratio()
    return f"{d}/1 {m}/1 {num_s}/{denomim_s}"
