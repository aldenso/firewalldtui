#!/usr/bin/env python2
import locale, re, os
from dialog import Dialog
from subprocess import Popen, PIPE

if not os.geteuid == 0 and not os.getenv("SUDO_UID"):
    exit("You need root privilegs to run utility. \nPlease try again.")


locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

d.set_background_title("Firewall Administration Menu")
listzones = []
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

def getstatus():
    cmd="firewall-cmd --state"
    p = Popen(cmd, stdout=PIPE, shell=True)
    state, error = p.communicate()
    cmd="firewall-cmd --version"
    p = Popen(cmd, stdout=PIPE, shell=True)
    version, error = p.communicate()
    if state.rstrip() == "running":
        d.msgbox("Firewalld Service is Running, Firewalld version: %s" % version.rstrip())
        main()
    else:
        d.msgbox("Firewalld Service is NOT Running")
        main()

def listallzones():
    listofzones()
    showlist = []
    for item in listzones:
        showlist.append(item[0])
    code = d.msgbox("Available Zones: \n %s " % showlist)
    if code == d.OK:
        zoneactions()

def getdefzone():
    cmd="firewall-cmd --get-default-zone"
    p = Popen(cmd, stdout=PIPE, shell=True)
    default, error = p.communicate()
    code = d.msgbox("The default zone is: \n %s" % default)
    if code == d.OK:
        zoneactions()

def setdefzone():
    selectedzone = ""
    listofzones()
    code, tags = d.radiolist("Select the zone you want to set as Default." ,
                            choices=listzones,
                            title="Zone Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
    if code == d.OK:
        if tags:
            selectedzone = str(tags)
            cmd="firewall-cmd --set-default-zone=%s" % selectedzone
            p = Popen(cmd, stdout=PIPE, shell=True)
            default, error = p.communicate()
            code = d.msgbox("The default zone is: \n %s" % selectedzone)
            if code == d.OK:
                zoneactions()
        else:
            d.msgbox("You must select a zone.")
            setdefzone()
    else:
        del listzones[:]
        zoneactions()

def zoneactions():
    code, tags = d.menu("Select Actions to perform",
            choices= [("(1)", "List All Zones"),
            ("(2)", "Get Default Zone"),
            ("(3)", "Set Default Zone"),
            ("(4)", "Get Active Zones"),
            ("(5)", "Add Interface to Zone"),
            ("(6)", "Change Interface to Zone"),
            ("(7)", "Remove Interface from Zone")],
            title="Zone Selection",
            backtitle="Firewall Administration Menu Tui Version")
    if code == d.OK:
        if tags == "(1)":
            listallzones()
        elif tags == "(2)":
            getdefzone()
        elif tags == "(3)":
            setdefzone()
        elif tags == "(4)":
            pass
        elif tags == "(6)":
            pass
        elif tags == "(7)":
            pass
        elif tags == "(8)":
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

def portsactions():
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
                portsactions()
        else:
            main()

        portsactionsmenu()


    else:
        portsactionsmenu()

def listpermports():
    ports=[]
    cmd="firewall-cmd --list-ports --permanent --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permports, error = p.communicate()
    if not permports:
        d.msgbox("No active Ports for zone: %s, better check services" % selectedzone)
    else:
        for permport in permports.split():
            item = permport
            ports.append(item)
        d.msgbox("Ports Active in zone: %s" % ports)
    portsactions()

def listnonpermports():
    ports=[]
    cmd="firewall-cmd --list-ports --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    permports, error = p.communicate()
    if not permports:
        d.msgbox("No active Ports for zone: %s, better check services" % selectedzone)
    else:
        for permport in permports.split():
            item = permport
            ports.append(item)
        d.msgbox("Ports Active in zone: %s" % ports)
    portsactions()

def addpermports():
    code, tags = d.inputbox("Add ports for zone: %s example --> port1/tcp,port2/udp..." % selectedzone)
    if code == d.OK:
        if tags:
            for item in tags.split(","):
                if not re.search(r"^\d+(\/)(tcp|udp)", item):
                    d.msgbox("You introduce a value not permitted")
                    addpermports()
                else:
                    for item in tags.split(","):
                        #it doesn't matter if is already enabled
                        cmd="firewall-cmd --add-port=%s --permanent --zone=%s" % (item, selectedzone)
                        p = Popen(cmd, stdout=PIPE, shell=True)
                        addports, error = p.communicate()
                    d.msgbox("Ports succesfully enabled")
                    if code == d.OK:
                        portsactions()
        else:
            d.msgbox("You must introduce ports to enable. example(22/tcp,80/tcp,68/udp...)")
            addpermports()
    else:
        portsactions()

def addnonpermports():
    code, tags = d.inputbox("Add ports for zone: %s example --> port1/tcp,port2/udp..." % selectedzone)
    if code == d.OK:
        if tags:
            for item in tags.split(","):
                if not re.search(r"^\d+(\/)(tcp|udp)", item):
                    d.msgbox("You introduce a value not permitted")
                    addnonpermports()
                else:
                    for item in tags.split(","):
                        #it doesn't matter if it's already enabled
                        cmd="firewall-cmd --add-port=%s --zone=%s" % (item, selectedzone)
                        p = Popen(cmd, stdout=PIPE, shell=True)
                        addports, error = p.communicate()
                    d.msgbox("Ports succesfully enabled")
                    if code == d.OK:
                        portsactions()
        else:
            d.msgbox("You must introduce ports to enable. example(22/tcp,80/tcp,68/udp...)")
            addnonpermports()
    else:
        portsactions()

def removepermports():
    listports = []
    cmd="firewall-cmd --list-ports --permanent --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    ports, error = p.communicate()
    if not ports:
        d.msgbox("No active ports in zone: %s" % selectedzone)
        portsactionsmenu()
    else:
        for port in ports.split():
            tags = False
            item = port, "" ,False
            listports.append(item)
        code, tags = d.checklist("Select Ports to disable Permanent" ,
                                 choices=listports,
                                 title="Ports Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
        if code == d.OK:
            if not tags:
                d.msgbox("You didn't select a port to disable")
                removepermports()
            else:
                for item in tags:
                    cmd="firewall-cmd --remove-port=%s --permanent --zone=%s" % (item, selectedzone)
                    p = Popen(cmd, stdout=PIPE, shell=True)
                    standard = p.communicate()
                d.msgbox("Ports permanently disable in zone.")
                portsactionsmenu()
        else:
            portsactionsmenu()

def removenonpermports():
    listports = []
    cmd="firewall-cmd --list-ports --zone=%s" % selectedzone
    p = Popen(cmd, stdout=PIPE, shell=True)
    ports, error = p.communicate()
    if not ports:
        d.msgbox("No active ports in zone: %s" % selectedzone)
        portsactionsmenu()
    else:
        for port in ports.split():
            tags = False
            item = port, "" ,False
            listports.append(item)
        code, tags = d.checklist("Select Ports to disable non-permanently" ,
                                 choices=listports,
                                 title="Ports Selection",
                                 backtitle="Firewall Administration Menu "
                                 "Tui Version")
        if code == d.OK:
            if not tags:
                d.msgbox("You didn't select a port to disable")
                removenonpermports()
            else:
                for item in tags:
                    cmd="firewall-cmd --remove-port=%s --zone=%s" % (item, selectedzone)
                    p = Popen(cmd, stdout=PIPE, shell=True)
                    standard = p.communicate()
                d.msgbox("Ports non-permanently disable in zone.")
                portsactionsmenu()
        else:
            portsactionsmenu()

def portsactionsmenu():
        global selectedzone
        code, tags = d.menu("Select Action to perform in zone: %s" % selectedzone,
                choices= [("(1)", "List Permanent Ports"),
                ("(2)", "List non-permanent Ports"),
                ("(3)", "Add Permanent Ports"),
                ("(4)", "Add non-permanent Ports"),
                ("(5)", "Remove Permanent Ports"),
                ("(6)", "Remove non-permanent Ports")],
                title="Ports Actions",
                backtitle="Firewall Administration Menu Tui Version")
        if code == d.OK:
            if tags == "(1)":
                listpermports()
            elif tags == "(2)":
                listnonpermports()
            elif tags == "(3)":
                addpermports()
            elif tags == "(4)":
                addnonpermports()
            elif tags == "(5)":
                removepermports()
            elif tags == "(6)":
                removenonpermports()
        else:
            selectedzone = ""
            main()

def querypermmasq():
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
                cmd="firewall-cmd --query-masquerade --permanent --zone=%s" % selectedzone
                p = Popen(cmd, stdout=PIPE, shell=True)
                query, error = p.communicate()
                if query.rstrip() == "yes":
                    code = d.msgbox("For Zone %s the masquerade is set to %s " % (selectedzone, query.rstrip()))
                    if code == d.OK:
                        selectedzone = ""
                        masqueradeactionsmenu()
                else:
                    code = d.msgbox("For zone %s the masquerade is set to no" % selectedzone)
                    if code == d.OK:
                        selectedzone = ""
                        masqueradeactionsmenu()
            else:
                d.msgbox("You have to select a zone...")
                querypermmasq()
        else:
            #main()
            selectedzone = ""
            masqueradeactionsmenu()
    else:
        selectedzone = ""
        masqueradeactionsmenu()   

def masqueradeactionsmenu():
    global selectedzone
    code, tags = d.menu("Select Action to perform:",
            choices= [("(1)", "Add Permanent Masquerade"),
            ("(2)", "Add non-permanent Masquerade"),
            ("(3)", "Query Permanent Masquerade"),
            ("(4)", "Query non-permanent Masquerade"),
            ("(5)", "Remove Permanent Masquerade"),
            ("(6)", "Remove non-permanent Masquerade")],
            title="Masquerade Actions",
            backtitle="Firewall Administration Menu Tui Version")
    if code == d.OK:
        if tags == "(1)":
            pass
        elif tags == "(2)":
            pass
        elif tags == "(3)":
            querypermmasq()
        elif tags == "(4)":
            pass
        elif tags == "(5)":
            pass
        elif tags == "(6)":
            pass
    else:
        selectedzone = ""
        main()

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
            getstatus()
        elif tags == "(2)":
            zoneactions()
        elif tags == "(3)":
            serviceactions()
        elif tags == "(4)":
            portsactions()
        elif tags == "(5)":
            pass
        elif tags == "(6)":
            masqueradeactionsmenu()
        elif tags == "(7)":
            pass
        elif tags == "(8)":
            pass
        else:
            code, tag = d.menu("OK, then you have two options:",
                           choices=[("(1)", "Leave example"),
                                    ("(2)", "Leave example")])

if __name__  == "__main__":
    main()