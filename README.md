# veracodeIntegration
Veracode integrations scripts

apiWrapper.py
-------------

Usage Example: python3 apiWrapper.py -v "your Veracode API ID" -s "your Veracode API Secret" -m -appname 'YourApplicationName' -version 1.0 -filepath /full/path/to/file.txt -autoscan True -createprofile True

Docker:
Alternatively you can build the Dockerfile which provides the script and run your CI in there. Also published to docker.io as gvit/veracode

Veracode API documentation can be found here: https://help.veracode.com/reader/y_H3nFK8RERrYT6OgB6zvQ/vQFACyO_itp1dSrCAnJRDw
