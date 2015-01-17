#!/usr/bin/env python2
import locale
from dialog import Dialog
from subprocess import Popen, PIPE

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

d.set_background_title("Firewall Administration Menu")
listzones = []
services = []
selectedzone = ""

def listofzones():
	cmd="firewall-cmd --get-zones"
	p = Popen(cmd, stdout=PIPE, shell=True)
	zones, error = p.communicate()
	for zone in zones.split():
		tag = False
		lista = zone, "" ,tag
		listzones.append(lista)
	return listzones


def prueba():
    code, tag = d.menu("OK, this are your options:",
                           choices=[("(10)", "Bye"),
                                    ("(20)", "Adios")])

def zoneactions():
    code, tags = d.menu("Select Actions to perform",
            choices= [("(1)", "List All Zones"),
            ("(2)", "Set Default Zone"),
            ("(3)", "Get Active Zones"),
            ("(4)", "Add Interface to Zone"),
            ("(5)", "Change Interface to Zone"),
            ("(6)", "Remove Interface from Zone")],
            title="Zone Selection",
            backtitle="Firewall Administration Menu Tui Version")
    if code == d.OK:
        if tags == "(1)":
            pass
        elif tags == "(2)":
            pass
        elif tags == "(3)":
            pass
        elif tags == "(4)":
            pass
        elif tags == "(5)":
            pass
    else:
        main()

def listpermservices():
    services = []
    cmd="firewall-cmd --list-services --permanent --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permservices, error = p.communicate()
    if not permservices:
        d.msgbox("No active Services for zone: %s" % selectedzone)
    else:
        for permservice in permservices.split():
            item = permservice
            services.append(item)
        d.msgbox("Services Active in zone: %s" % services)

    serviceactions()

def listnonpermservices():
    services = []
    cmd="firewall-cmd --list-services --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permservices, error = p.communicate()
    if not permservices:
        d.msgbox("No active Services for zone: %s" % selectedzone)
    else:
        for permservice in permservices.split():
            item = permservice
            services.append(item)
        d.msgbox("Services Active in zone: %s" % services)

    serviceactions()

def addpermservices():
    avaiserv2disable = []
    selectionmenu = []
    cmd="firewall-cmd --get-services"
    p = Popen(cmd, stdout=PIPE, shell=True)
    avaiserv, error = p.communicate()
    cmd="firewall-cmd --list-services --permanent --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    actserv, error = p.communicate()
    list1 = avaiserv.rstrip().split()
    list2 = actserv.rstrip().split()
    for item in list1:
        if item not in list2:
            avaiserv2disable.append(item)

    for serv in avaiserv2disable:
        tags = False
        item = serv, "" ,False
        selectionmenu.append(item)
    code, tags = d.checklist("Select Services to enable Permanently" ,
                                 choices=selectionmenu,
                                 title="Services Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
    if code == d.OK:
        if not tags:
            d.msgbox("You didn't select a service to enable")
            addpermservices()
        else:
            for item in tags:
                cmd="firewall-cmd --add-service=%s --permanent --zone=%s" % (item, selectedzone)
                p = Popen(cmd, stdout=PIPE, shell=True)
                standard = p.communicate()
            d.msgbox("Services permanently added to zone.")
            serviceactionsmenu()
    else:
        serviceactionsmenu()

def addnonpermservices():
    avaiserv2disable = []
    selectionmenu = []
    cmd="firewall-cmd --get-services"
    p = Popen(cmd, stdout=PIPE, shell=True)
    avaiserv, error = p.communicate()
    cmd="firewall-cmd --list-services --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    actserv, error = p.communicate()
    list1 = avaiserv.rstrip().split()
    list2 = actserv.rstrip().split()
    for item in list1:
        if item not in list2:
            avaiserv2disable.append(item)

    for serv in avaiserv2disable:
        tags = False
        item = serv, "" ,False
        selectionmenu.append(item)
    code, tags = d.checklist("Select Services to enable non-permanently" ,
                                 choices=selectionmenu,
                                 title="Services Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
    if code == d.OK:
        if not tags:
            d.msgbox("You didn't select a service to enable")
            addpermservices()
        else:
            for item in tags:
                cmd="firewall-cmd --add-service=%s --zone=%s" % (item, selectedzone)
                p = Popen(cmd, stdout=PIPE, shell=True)
                standard = p.communicate()
            d.msgbox("Services non-permanently added to zone.")
            serviceactionsmenu()
    else:
        serviceactionsmenu()

def removepermservices():
    listpermservices = []
    cmd="firewall-cmd --list-services --permanent --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permservices, error = p.communicate()
    if not permservices:
        d.msgbox("No active Services for zone: %s" % selectedzone)
        serviceactionsmenu()
    else:
        for permservice in permservices.split():
            tags = False
            item = permservice, "" ,False
            listpermservices.append(item)
        code, tags = d.checklist("Select Services to disable Permanent" ,
                                 choices=listpermservices,
                                 title="Services Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
        if code == d.OK:
            if not tags:
                d.msgbox("You didn't select a service to disable")
                removepermservices()
            else:
                for item in tags:
                    cmd="firewall-cmd --remove-service=%s --permanent --zone=%s" % (item, selectedzone)
                    p = Popen(cmd, stdout=PIPE, shell=True)
                    standard = p.communicate()
                d.msgbox("Services permanently remove from zone.")
                serviceactionsmenu()
        else:
            serviceactionsmenu()

def removenonpermservices():
    listpermservices = []
    cmd="firewall-cmd --list-services --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permservices, error = p.communicate()
    if not permservices:
        d.msgbox("No active Services for zone: %s" % selectedzone)
        serviceactionsmenu()
    else:
        for permservice in permservices.split():
            tags = False
            item = permservice, "" ,False
            listpermservices.append(item)
        code, tags = d.checklist("Select Services to disable Permanent" ,
                                 choices=listpermservices,
                                 title="Services Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
        if code == d.OK:
            if not tags:
                d.msgbox("You didn't select a service to disable")
                removepermservices()
            else:
                for item in tags:
                    cmd="firewall-cmd --remove-service=%s --zone=%s" % (item, selectedzone)
                    p = Popen(cmd, stdout=PIPE, shell=True)
                    standard = p.communicate()
                d.msgbox("Services permanently remove from zone.")
                serviceactionsmenu()
        else:
            serviceactionsmenu()


def serviceactionsmenu():
        global selectedzone
        code, tags = d.menu("Select Action to perform in zone: %s" % selectedzone,
                choices= [("(1)", "List Permanent Services"),
                ("(2)", "List non-permanent Services"),
                ("(3)", "Add Permanent Services"),
                ("(4)", "Add non-permanent Services"),
                ("(5)", "Remove Permanent Services"),
                ("(6)", "Remove non-permanent Services")],
                title="Services Actions",
                backtitle="Firewall Administration Menu Tui Version")
        if code == d.OK:
            if tags == "(1)":
                listpermservices()
            elif tags == "(2)":
                listnonpermservices()
            elif tags == "(3)":
                addpermservices()
            elif tags == "(4)":
                addnonpermservices()
            elif tags == "(5)":
                removepermservices()
            elif tags == "(6)":
                removenonpermservices()
        else:
            services = []
            selectedzone = ""
            main()

def serviceactions():
    global selectedzone
    if not selectedzone:
        listofzones()
        code, tags = d.radiolist("Select the zone where you want to work" ,
                                 choices=listzones,
                                 title="Zone Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
        if code == d.OK:
            if tags:
                selectedzone = str(tags)

            else:
                d.msgbox("You have to select a zone...")
                serviceactions()
        else:
            main()

        serviceactionsmenu()


    else:
        serviceactionsmenu()

def main():

    code, tags = d.menu("Select an Action to perform ",
            choices= [("(1)", "Check Services Status"),
            ("(2)", "Zones Actions"),
            ("(3)", "Services Actions"),
            ("(4)", "Ports Actions"),
            ("(5)", "Rules Actions"),
            ("(6)", "Masquerade Actions"),
            ("(7)", "Forward Actions"),
            ("(8)", "Reload/CompleteReload/Run2Permanent") ],
            title="Actions Selection",
            backtitle="Firewalld Administration Menu Tui Version")

    if code == d.OK:
        if tags == "(1)":
            prueba()
        elif tags == "(2)":
            zoneactions()
        elif tags == "(3)":
            serviceactions()
        elif tags == "(4)":
            pass
        elif tags == "(5)":
            pass
        elif tags == "(6)":
            pass
        elif tags == "(7)":
            pass
        elif tags == "(8)":
            pass
        else:
            code, tag = d.menu("OK, then you have two options:",
                           choices=[("(1)", "Leave this fascinating example"),
                                    ("(2)", "Leave this fascinating example")])

if __name__  == "__main__":
    main()