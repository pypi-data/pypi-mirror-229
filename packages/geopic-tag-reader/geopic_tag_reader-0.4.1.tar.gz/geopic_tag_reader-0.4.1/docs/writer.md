<!-- markdownlint-disable -->

<a href="../geopic_tag_reader/writer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `writer`





---

<a href="../geopic_tag_reader/writer.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `writePictureMetadata`

```python
writePictureMetadata(picture: bytes, metadata: PictureMetadata) → bytes
```

Override exif metadata on raw picture and return updated bytes 


---

<a href="../geopic_tag_reader/writer.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `format_offset`

```python
format_offset(offset: timedelta) → str
```

Format offset for OffsetTimeOriginal. Format is like "+02:00" for paris offset ``` format_offset(timedelta(hours=5, minutes=45))```
'+05:45'
``` format_offset(timedelta(hours=-3))``` '-03:00' 


---

<a href="../geopic_tag_reader/writer.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `localize`

```python
localize(dt: datetime, metadata: ImageData) → datetime
```

Localize a datetime in the timezone of the picture If the picture does not contains GPS position, the datetime will not be modified. 


---

<a href="../geopic_tag_reader/writer.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PictureMetadata`
PictureMetadata(capture_time: Optional[datetime.datetime] = None, longitude: Optional[float] = None, latitude: Optional[float] = None, picture_type: Optional[geopic_tag_reader.model.PictureType] = None) 

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    capture_time: Optional[datetime] = None,
    longitude: Optional[float] = None,
    latitude: Optional[float] = None,
    picture_type: Optional[PictureType] = None
) → None
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
