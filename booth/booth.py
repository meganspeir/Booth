"""All together now.

Analog camera control and uploader.

"""

import os
import hashlib
import socket
import subprocess
import time

import Image
import wiringpi2 as wiring

from uuid import uuid4

from Printer import *

from config import EXTENSIONS, FILENAME_LENGTH, FILES_FOLDER, DESTINATION, \
    OFFLINE, INPUT, OUTPUT, PUD_UP, OFF, ON, RELEASE, PRESS, BUTTON, \
    RED_LIGHT, FOCUS_BUTTON, SHUTTER_BUTTON, until_held, until_tapped, \
    until_all_ready, until_first_pose, until_focused, until_released, \
    next_pose, poses, printer


class Booth(object):

    def initialize(self):
        """Initializes pin setup for WiringPi"""
        # Setup pin numbering (sequential)
        wiring.wiringPiSetup()
        # Setup pin IO
        wiring.pinMode(BUTTON, INPUT)
        wiring.pullUpDnControl(BUTTON, PUD_UP)
        wiring.pinMode(RED_LIGHT, OUTPUT)
        wiring.pinMode(FOCUS_BUTTON, OUTPUT)
        wiring.pinMode(SHUTTER_BUTTON, OUTPUT)

    def ready(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('capture.local', 0))
            printer.println('Ready to capture.')
            printer.println('The server is online.')
            printer.println('IP address is ' + s.getsockname()[0])
            printer.feed(5)
        except:
            printer.println('Ready to capture.')
            printer.boldOn()
            printer.println('The server is offline.')
            printer.boldOff()
            printer.println('Photos will be stored locally.')
            printer.feed(5)

    def tap(self):
        print "Tapped..."
        wiring.digitalWrite(RED_LIGHT, ON)
        wiring.delay(200)
        wiring.digitalWrite(RED_LIGHT, OFF)
        wiring.delay(200)
        wiring.digitalWrite(RED_LIGHT, ON)
        wiring.delay(200)
        wiring.digitalWrite(RED_LIGHT, OFF)

    def hold(self):
        print "Held..."

    def reset(self):
        """Reset the USB and wake the camera"""
        # Reset the USB
        subprocess.call('gphoto2 --reset', shell=True)
        # Wake the camera
        wiring.digitalWrite(FOCUS_BUTTON, PRESS)
        wiring.delay(100)
        wiring.digitalWrite(FOCUS_BUTTON, RELEASE)
        # Initialize the camera
        subprocess.call('gphoto2 --auto-detect', shell=True)

    def stack(self):
        """Generate stack ID"""
        stack_id = hashlib.sha1(unicode(uuid4())).hexdigest()[:12]
        print stack_id

    def take_photo(self):
        """Analog camera control."""
        # Initiate the picture session through BUTTON PRESS
        # Wait the user to get in place
        print "Go get ready..."
        wiring.delay(until_all_ready)
        # Pictures can be taken at any time
        wiring.digitalWrite(RED_LIGHT, ON)
        print "We're ready. Hope you are too."
        wiring.delay(until_first_pose)
        # Trigger camera
        for pose in range(0, poses):
            wiring.digitalWrite(FOCUS_BUTTON, PRESS)
            wiring.delay(until_focused)
            print "Smile!"
            wiring.digitalWrite(SHUTTER_BUTTON, PRESS)
            wiring.delay(until_released)
            wiring.digitalWrite(SHUTTER_BUTTON, RELEASE)
            wiring.digitalWrite(FOCUS_BUTTON, RELEASE)
            print "Oh! Capture"
            wiring.delay(next_pose)

    def tether(self):
        """The solution until real tethering."""
        # Pictures cannot be taken
        wiring.digitalWrite(RED_LIGHT, OFF)
        # Download pictures from camera
        subprocess.call('gphoto2 --get-all-files', shell=True)
        # Remove pitures from camera
        subprocess.call('gphoto2 --delete-all-files --recurse', shell=True)
        # Return camera to ready state

    def good_extension(self, filename):
        """Only allow files that we say. Case insensitive"""
        return '.' in filename and \
            filename.lower().rsplit('.', 1)[1] in EXTENSIONS

    def uniquify(self, file):
        """Creates a unique filename for each file."""
        extension = os.path.splitext(file)[1]
        hash = hashlib.sha1(unicode(uuid4()))
        filename = hash.hexdigest()[:FILENAME_LENGTH] + extension.lower()
        return filename

    def upload(self, source, filename):
        """Uploads file so no further processing will take place"""
        destination = os.path.join(DESTINATION, filename)
        subprocess.call('scp -C "%s" %s' % (source, destination), shell=True)
        os.unlink(source)
        print "moved"

    def offline(self, source, filename):
        """Renames and moves file so no further processing will take place"""
        destination = os.path.join(OFFLINE, filename)
        subprocess.call('mv "%s" %s' % (source, destination), shell=True)
        print "offlined"

    def print_receipt(self):
        """Print a receipt and URL for the photo"""
        printer.justify('C')
        printer.boldOn()
        printer.println('Thank You For Visiting')
        printer.boldOff()
        printer.printImage(Image.open('images/mark.png'), True)
        printer.setSize('S')
        printer.println('Group text with the number below\n'
                        'so Megan can test her project.\n'
                        'Include me in your conversations.')
        printer.setSize('L')
        printer.println('(XXX) XXX-XXXX')
        printer.setSize('S')
        printer.println('www.meganspeir.com')
        printer.feed(5)

    def process(self, folder):
        """Uniquifies and uploads files."""
        files = os.listdir(folder)
        path = [os.path.join(folder, file) for file in files]
        for file in path:
            if self.good_extension(file):
                filename = self.uniquify(file)
                try:
                    self.upload(file, filename)
                except:
                    self.offline(file, filename)

if __name__ == "__main__":
    booth = Booth()
    try:
        time.sleep(30)
        booth.initialize()
        booth.ready()
        previous_state = wiring.digitalRead(BUTTON)
        previous_time = time.time()
        tapped = False
        held = False
        while(True):
            state = wiring.digitalRead(BUTTON)
            t = time.time()
            if state != previous_state:
                previous_state = state
                previous_time = t
            else:
                if (t - previous_time) >= until_held:
                    if held:
                        booth.hold()
                        held = False
                        tapped = False
                elif (t - previous_time) >= until_tapped:
                    if state:
                        if tapped:
                            booth.reset()
                            booth.tap()
                            booth.take_photo()
                            booth.tether()
                            booth.process(FILES_FOLDER)
                            booth.print_receipt()
                            tapped = False
                            held = False
                    else:
                        tapped = True
    except KeyboardInterrupt:
        print "\nExiting..."
