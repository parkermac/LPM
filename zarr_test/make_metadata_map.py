import zarr
import s3fs
import os

# 1. Connect to Kopah with your working credentials
fs = s3fs.S3FileSystem(
    key=os.environ['AWS_ACCESS_KEY_ID'],
    secret=os.environ['AWS_SECRET_ACCESS_KEY'],
    client_kwargs={"endpoint_url": "https://s3.kopah.uw.edu"}
)

# 2. Consolidate the metadata for the dataset
zarr.consolidate_metadata(fs.get_mapper('s3://liveocean-test/test18.zarr'))

# 3. Apply your public-read ACL to this newly generated .zmetadata file
# via your command line: s3cmd setacl s3://liveocean-test/test18.zarr/.zmetadata --acl-public
