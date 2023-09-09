<!-- markdownlint-disable -->

# API Overview

## Modules

- [`model`](./model.md#module-model)
- [`reader`](./reader.md#module-reader)
- [`writer`](./writer.md#module-writer)

## Classes

- [`model.PictureType`](./model.md#class-picturetype)
- [`reader.CropValues`](./reader.md#class-cropvalues): Cropped equirectangular pictures metadata
- [`reader.GeoPicTags`](./reader.md#class-geopictags): Tags associated to a geolocated picture
- [`reader.InvalidExifException`](./reader.md#class-invalidexifexception): Exception for invalid EXIF information from image
- [`reader.PartialExifException`](./reader.md#class-partialexifexception): Exception for partial / missing EXIF information from image
- [`reader.PartialGeoPicTags`](./reader.md#class-partialgeopictags): Tags associated to a geolocated picture when not all tags have been found
- [`writer.PictureMetadata`](./writer.md#class-picturemetadata): PictureMetadata(capture_time: Optional[datetime.datetime] = None, longitude: Optional[float] = None, latitude: Optional[float] = None, picture_type: Optional[geopic_tag_reader.model.PictureType] = None)

## Functions

- [`reader.decodeMakeModel`](./reader.md#function-decodemakemodel): Python 2/3 compatible decoding of make/model field.
- [`reader.isExifTagUsable`](./reader.md#function-isexiftagusable): Is a given EXIF tag usable (not null and not an empty string)
- [`reader.readPictureMetadata`](./reader.md#function-readpicturemetadata): Extracts metadata from picture file
- [`writer.format_offset`](./writer.md#function-format_offset): Format offset for OffsetTimeOriginal. Format is like "+02:00" for paris offset
- [`writer.localize`](./writer.md#function-localize): Localize a datetime in the timezone of the picture
- [`writer.writePictureMetadata`](./writer.md#function-writepicturemetadata): Override exif metadata on raw picture and return updated bytes


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
