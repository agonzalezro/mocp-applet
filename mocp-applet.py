#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Thanks to http://ywwg.com/wordpress/?p=337
#Licensed under the GNU/GPL v2.0 by alex@mirblu.com

import pygtk, gtk, gnomeapplet, gobject, gnome.ui, pynotify
import sys, os, subprocess
pygtk.require('2.0')

version = '0.22'

class Mocp_Applet(gnomeapplet.Applet):

    # init the object
    def __init__(self, applet, iid):
        self.applet = applet
        self.hbox = gtk.HBox()
        self.first_time = 1;

        # notifications
        pynotify.init('Mocp Applet')

        # menu
        self.propxml="""
        <popup name="button3">
        <menuitem name="Item 1" verb="Terminal" label="_Launch mocp" pixtype="stock" pixname="gtk-execute"/>
        <menuitem name="Item 2" verb="About" label="_About..." pixtype="stock" pixname="gnome-stock-about"/>
        </popup>
    	"""
        self.verbs = [ ( 'About', self.about_info ),
                       ( 'Terminal', self.launch_terminal ) ]
        self.applet.setup_menu(self.propxml,self.verbs,None)

        # buttons hbox
        self.button_play = self.newButton('gtk-media-play')
        self.hbox.add(self.button_play)
        # at first time if mocp isn't playing, don't show the next button
        # FIXME: sometimes goes into this if, but self.get_attr gives me a "STOP" string
        if self.get_attr('state') != 'STOP':
            self.hbox.add(self.newButton('gtk-media-next'))
            self.first_time = 0;

        #change play/pause button state
        self.toggle_play_button_and_show_notify(self.button_play, 'gtk-media-play')

        self.applet.add(self.hbox)
        self.applet.show_all()
  

    # create button without relief and width a stock image
    def newButton(self, icon):
        button = gtk.Button('')
        image = gtk.Image()
        image.set_from_stock(icon, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)
        button.set_relief(gtk.RELIEF_NONE)
        button.connect('button-press-event', self.button_press, icon)

        return button


    # button event catch
    def button_press(self, button, event, name):
        if event.button == 1:
            if name == 'gtk-media-play':
                if self.first_time == 1:
                    self.first_time = 0
                    self.applet.remove(self.hbox)
                    self.hbox.add(self.newButton('gtk-media-next'))
                    self.applet.add(self.hbox)
                    self.applet.show_all()
                    button = self.button_play
                self.play_or_pause()
            if name == 'gtk-media-next':
                self.play_next()

            self.toggle_play_button_and_show_notify(button, name)
                
        elif event.button == 3:
            # right click
            button.emit_stop_by_name('button_press_event')
            self.create_menu()


    # if the player is playing change the button image and show notification if applicable
    def toggle_play_button_and_show_notify(self, button, name):
        if name == 'gtk-media-play':
            if self.get_attr('state') == 'PLAY':
                # starting the player again 
                image = gtk.Image()
                image.set_from_stock("gtk-media-pause", gtk.ICON_SIZE_BUTTON)
                button.set_image(image)
                self.show_notification(button)
            elif self.get_attr('state') == 'PAUSE':
                # pausing the player
                image = gtk.Image()
                image.set_from_stock("gtk-media-play", gtk.ICON_SIZE_BUTTON)
                button.set_image(image)
            elif self.get_attr('state') == 'STOP':
                # I don't know why I need this elif ;_(
                image = gtk.Image()
                image.set_from_stock("gtk-media-play", gtk.ICON_SIZE_BUTTON)
                button.set_image(image)
        else:
            self.show_notification(button)



    # show song info
    def show_notification(self, widget):
        if self.get_attr('song') != '':
            title = self.get_attr('song')
        else:
            title = self.get_attr('file')

        if self.get_attr('artist') != '':
            artist = self.get_attr('artist')
        else:
            artist = '\nNo idV3 info!'

        n = pynotify.Notification(title, artist)
        n.set_urgency(pynotify.URGENCY_NORMAL)
        n.set_timeout(3000)
        helper = gtk.Button()
        icon = helper.render_icon(gtk.STOCK_ABOUT, gtk.ICON_SIZE_DIALOG)
        n.set_icon_from_pixbuf(icon)
        n.attach_to_widget(widget)
        n.show()


    # launch x-terminal from bash
    def launch_terminal(self, event, data=None):
        subprocess.Popen(['bash',  '-c', 'x-terminal-emulator -e mocp'], stdout=subprocess.PIPE)


    # returns STOP, PLAY or PAUSE
    def get_attr(self, attr):
        p = subprocess.Popen(['mocp', '-Q %'+attr], stdout=subprocess.PIPE)
        stdout = p.stdout
        return stdout.readline().strip()


    # if mocp is stopped, start it
    def play_or_pause(self):
        if self.get_attr('state') == 'STOP':
            subprocess.Popen(['mocp', '--play'])
            self.toggle_play_button_and_show_notify(self.button_play, 'gtk-media-play')
        else:
            subprocess.Popen(['mocp', '--toggle-pause'])


    # play the next file
    def play_next(self):
        if (os.path.exists(os.getenv('HOME')+'/.moc/pid')):
            subprocess.Popen(['mocp', '--next'])
        else:
            subprocess.Popen(['mocp', '--play'])


    # the about window
    def about_info(self, event, data=None):
        about = gnome.ui.About('Mocp Applet', version, '(c) 2009 Alexandre González',
                               'Applet to control mocp: play/pause and next.',
                               ['Alexandre González <alex@mirblu.com>'])
        about.show()
#
# EOC: End of class
#


# function to run/register the clas
def factory(applet, iid):
    Mocp_Applet(applet, iid)
    return gtk.TRUE


if __name__ == '__main__':
    gobject.type_register(Mocp_Applet)

    if len(sys.argv) > 1 and sys.argv[1] == 'run-in-window':
        #Create as a window
        main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        main_window.set_title('Mocp Applet')
        main_window.connect('destroy', gtk.main_quit)

        app = gnomeapplet.Applet()
        factory(app, None)
        app.reparent(main_window)

        main_window.show_all()
        gtk.main()

    else:
        #Create as an applet
        gnomeapplet.bonobo_factory('OAFIID:GNOME_MocpApplet_Factory',
                                   gnomeapplet.Applet.__gtype__,
                                   'simple remote control', version,
                                   factory)
