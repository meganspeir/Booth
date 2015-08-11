The Making & Re-factoring of Booth:
==========

The idea came from wanting to have a photobooth present at my 1 year wedding celebration. The drawbacks to other implementations of photobooths were mainly the cost and in the digital realm, not having complete control over the photograph.

Because the project started out in this selfish vain, it was easiest to imagine things as I was going to need them. I was the only user and only my event mattered. So the project took on two main parts. The Raspberry Pi photobooth. And the Flask web app, Guest Book (formerly Capture). (TODO: makes more sense to separate the two completely).

Photobooth:
==========

A Raspberry Pi built into a physical "mini booth".

The script booth.py uses the WiringPi 2.0 library to allow interfacing with the GPIO pins of the Raspberry Pi.

First, initializes the pins:
    - The input button that is pressed on the booth by a user to wake camera
    - The red light button that alerts the user that the camera is being triggered (see tap function)
    - A pin to focus the camera
    - A pin to "shutter" and take the picture

The ready function checks for an internet connection and will return an IP address for successful connection. If no connection is available, the booth relies on the Pi to store the photos until they can be sent to the app.

The reset function accounts for a quirk with the Pi regarding the usb cable connected to the camera. At times the Pi will think the USB attached to the camera has been disconnected so this is a fail safe to make sure if that happens it will automatically reset.

The stack function initializes a unique id for the set of photos that will be taken for the current group.

Take-photo finally takes the picture!

The tether function takes the pictures from the camera and moves them onto the Pi.

With good-extension we make sure that we only accept photos with extensions that are specified to be okay.

Uniquify uses hashing to provide each photo with a unique filename.

Upload/offline moves and renames the photos from the Pi to the computers local filesystem.

Nifty Add-On
==========

Inside the booth there is also a small AdaFruit printer. Check out the code in printer.py to see how to make the printer say whatever.

Guest Book:
==========

A digital guestbook web application that is a timeline of photos and messages for events. Made with Python, Flask, Postgres, SQLAlchemy, Gphoto2 library, EXIF, Twilio API (for messages), nginx, html, css, javascript.

In its current state the only photo input is from the Raspberry Pi photobooth.
Watch.py is set to run on every call from the application to the db (server?).
It will check a local folder for photos with good extensions, extract datetime information and transform it to a format that the database can read using regex.
The photos will then be stored in the database and removed from the folder to avoid duplicate processing.

The database tables are defined in models.py. One for messages, one for photos and a table called entries that joins the two to be able to display them in timeline fashion.

Views.py displays everything from the database in the style of a single page app. Upon refresh the watch.py script is triggered and views.py will return any new content from the database.

Maybe one day...
==========

- Photo post processing
- Support GIF
- Social Integration
    - Pull tweets of a given hashtag into the timeline?
- Multiple users and events
- In line comments for photos
- Claim a photo
- Moar Javascript
- Photo Ratings (Event photo stacks top rated photo represents that of the stack, like iPhoto)
- Event sentiment analysis based on text messages?
- Screenshots!
- Demo
