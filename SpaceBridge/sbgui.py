#
#  updatergui.py
#
# Author: Reuben Balik <reuben@hologram.io>
#
# License: Copyright (c) 2016 Hologram All Rights Reserved.
#
# Released under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This is super hacky. Pyinstaller imports future which seems to have a
# bug where certain pieces of tkinter are missing. We want to force
# easygui to use the built-in 2.7 Tkinter and not the future tkinter
import sys
sys.modules['tkinter']=None
import easygui
from Tkinter import *
import re
import tkMessageBox
from sbexceptions import ErrorException, MissingParamException

class SpaceBridgeGUI:
    title = "Hologram SpaceBridge"
    def __init__(self, version):
        title = self.title + ' v' + version
        self.title = title

    def prompt_for_apikey(self):
        return easygui.passwordbox(
                msg="Please paste in your Hologram API key",
                title=self.title)


    def prompt_for_forwards(self, links):
        pfg = PortForwardGui(self.title)
        return pfg.prompt_for_forwards(links)

    
    def prompt_for_keygen(self):
        message = ("We're going to generate a set of secure keys to protect "
        "your connection to your device. These keys will be generated by the "
        "Hologram API. The Hologram servers will only store the public key and "
        "the private key will be saved to your computer.\n"
        "If you have a key already that you want to use or want to generate "
        "one on your own hit cancel and run with the --upload-publickey and --privatekey arguments.")
        res = easygui.ccbox(msg=message, title=self.title)
        return res


    def show_message(self, message):
        return easygui.msgbox(
                msg=message,
                title=self.title)


    def show_error_message(self, message):
        tkMessageBox.showerror(self.title, message)


    def show_exception(self):
        return easygui.exceptionbox(
                title=self.title)


    def prompt_for_orgid(self, orgs):
        org_list = []
        org_map = {}
        for org in orgs:
            org_list.append(org['name'])
            org_map[org['name']] = org['id']
        res = easygui.choicebox(
                msg='What organization will you be connecting to?',
                title=self.title,
                choices=org_list)
        if res == None:
            return None
        return org_map[res]


    def tunnel_running(self, fwdmessage):
        msg = "Tunnel is running\n\n" + fwdmessage +\
                "\nClick OK to close the tunnel and exit"
        self.show_message(msg)


class PortForwardGui:
    port_widgets = []
    tkroot = None
    result = None
    def __init__(self, title):
        self.linkre = re.compile(r' \[link#(\d+) ')
        self.title = title


    # builds a string to put into the dropdown box
    def build_link_string(self, link):
        res = link['devicename']
        res += " [link#%s device#%s]"%(str(link['id']), str(link['deviceid']))
        return res


    # parses the string that we generated and returns the link id
    def parse_link_string(self, linkstring):
        mo = re.search(self.linkre, linkstring)
        if mo is None:
            return None
        return mo.group(1)


    def button_callback(self):
        self.result = []
        for pw in self.port_widgets:
            device = pw['mv']
            devicestring = device.get()
            dp = pw['dp'].get(1.0, 'end-1c')
            lp = pw['lp'].get(1.0, 'end-1c')
            if devicestring and dp and lp:
                if not dp.isdigit() or not lp.isdigit():
                    tkMessageBox.showerror(self.title, "Ports must be a number")
                    return
                linkid = self.parse_link_string(devicestring)
                forward = [linkid, int(dp), int(lp)]
                self.result.append(forward)
        self.tkroot.destroy()


    def focus_next(self, event):
        event.widget.tk_focusNext().focus()
        return("break")


    def prompt_for_forwards(self, links):
        linkstrings = []
        for link in links:
            linkstrings.append(self.build_link_string(link))
        self.tkroot = Tk()
        self.tkroot.title(self.title)
        self.tkroot.bind_class("Text", "<Tab>", self.focus_next)

        frame_top = Frame(self.tkroot)
        frame_top.pack(expand = True)

        l1 = Label(frame_top, text="Configure your tunnels")
        l1.pack()

        frame2 = Frame(self.tkroot)
        frame2.pack(expand = True)
        frame_form = Frame(frame2)
        frame_form.pack(expand = True)

        l2 = Label(frame_form, text="Device")
        l2.grid(row=0, column=0)
        l3 = Label(frame_form, text="Device Port")
        l3.grid(row=0, column=1)
        l4 = Label(frame_form, text="Local Port")
        l4.grid(row=0, column=2)
        forwardrow = 1

        for i in range(5):
            port_widgets = self.add_new_forward(
                    frame_form, linkstrings, forwardrow)
            self.port_widgets.append(port_widgets)
            forwardrow += 1

        frame_bottom = Frame(frame2, pady=20)
        frame_bottom.pack()
        b = Button(frame_bottom, text="Done", command=self.button_callback)
        b.pack()

        self.tkroot.mainloop()
        return self.result


    def add_new_forward(self, master, links, forwardrow):
        menuvalue = StringVar(master)
        lst = OptionMenu(master, menuvalue, *links)
        lst.config(width=15)
        lst.grid(row=forwardrow, column=0)
        dport = Text(master, height=1, width=7)
        dport.grid(row=forwardrow, column=1)
        lport = Text(master, height=1, width=7)
        lport.grid(row=forwardrow, column=2)
        return {"mv":menuvalue, "dp":dport, "lp":lport}

