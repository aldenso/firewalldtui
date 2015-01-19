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
    del listzones[:]
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
    del listzones[:]
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

def getactivezones():
    cmd="firewall-cmd --get-active-zones"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    code = d.msgbox("The Active zones are: \n %s" % output)
    if code == d.OK:
        zoneactions()

def addinttozone():
    cmd="ip l | grep '^[1-9]:' | awk {'print $2'}  | grep -v 'lo' | cut -d':' -f1"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    interfaces = output.split()
    cmd="firewall-cmd --get-active-zones"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    availableinterfaces = [i for i in interfaces if i not in output.split()]
    listofinterfaces = [(i, "", False) for i in availableinterfaces]
    if availableinterfaces:
        code, tagsint = d.checklist("Select interfaces to add to the zone" ,
                            choices=listofinterfaces,
                            title="Interface Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
        if code == d.OK:
            if tagsint:
                for tagint in tagsint:
                    del listzones[:]
                    listofzones()
                    code, tagzone = d.radiolist("Select a zone where to add the interfaces." ,
                            choices=listzones,
                            title="Interface Selection")
                    if code == d.OK:
                        if tagzone:
                            cmd="firewall-cmd --add-interface=%s --zone=%s" % (tagint, tagzone)
                            p = Popen(cmd, stdout=PIPE, shell=True)
                            output, error = p.communicate()
                            code = d.msgbox("You succesfully added the interface to zone.")
                            zoneactions()
                        else:
                            code = d.msgbox("You have to select a zone.")
                            zoneactions()
                    else:
                        zoneactions()
            else:
                code = d.msgbox("You have to select an interface.")
                addinttozone()
        else: zoneactions()
    else:
        code = d.msgbox("No available interfaces. \nThe Active zones are: \n %s" % output)
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
            getactivezones()
        elif tags == "(5)":
            addinttozone()
        elif tags == "(6)":
            pass
        elif tags == "(7)":
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
    del listzones[:]
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
    del listzones[:]
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

def addpermmasq():
    cmd="firewall-cmd --list-all-zones --permanent | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    # check non masq zones and create list with manu tags "[(opt1, "", False), ...]"
    selectmasq4zone = [ (i[0], "", False) for i in masqlist if "no" in i[1]]
    code, tags = d.checklist("Select Zones to add masquerade on" ,
                            choices=selectmasq4zone,
                            title="Zone Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
    if code == d.OK:
        if tags:
            for item in tags:
                cmd="firewall-cmd --add-masquerade --permanent --zone=%s" % item
                p = Popen(cmd, stdout=PIPE, shell=True)
                output, error = p.communicate()
            d.msgbox("Masquerade added on zones: \n %s" % str(tags))
            masqueradeactionsmenu()
        else:
            d.msgbox("You didn't select a zone to set masquerade.")
            addpermmasq() 
    else:
        masqueradeactionsmenu()

def addnonpermmasq():
    cmd="firewall-cmd --list-all-zones | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    # check non masq zones and create list with manu tags "[(opt1, "", False), ...]"
    selectmasq4zone = [ (i[0], "", False) for i in masqlist if "no" in i[1]]
    code, tags = d.checklist("Select Zones to add masquerade on" ,
                            choices=selectmasq4zone,
                            title="Zone Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
    if code == d.OK:
        if tags:
            for item in tags:
                cmd="firewall-cmd --add-masquerade --zone=%s" % item
                p = Popen(cmd, stdout=PIPE, shell=True)
                output, error = p.communicate()
            d.msgbox("Masquerade added on zones: \n %s" % str(tags))
            masqueradeactionsmenu()
        else:
            d.msgbox("You didn't select a zone to set masquerade.")
            addpermmasq() 
    else:
        masqueradeactionsmenu()

def querypermmasq():
    cmd="firewall-cmd --list-all-zones --permanent | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    code = d.msgbox("Status of masquerade for all zones. \n %s" 
                    % masqlist, height=15, width=50 )
    if code == d.OK:
        masqueradeactionsmenu()

def querynonpermmasq():
    cmd="firewall-cmd --list-all-zones | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    code = d.msgbox("Status of masquerade for all zones. \n %s" 
                    % masqlist, height=15, width=50 )
    if code == d.OK:
        masqueradeactionsmenu()
  
def removepermmasq():
    cmd="firewall-cmd --list-all-zones --permanent | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    # check non masq zones and create list with manu tags "[(opt1, "", False), ...]"
    selectmasq4zone = [ (i[0], "", False) for i in masqlist if "yes" in i[1]]
    code, tags = d.checklist("Select Zones to remove masquerade on" ,
                            choices=selectmasq4zone,
                            title="Zone Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
    if code == d.OK:
        if tags:
            for item in tags:
                cmd="firewall-cmd --remove-masquerade --permanent --zone=%s" % item
                p = Popen(cmd, stdout=PIPE, shell=True)
                output, error = p.communicate()
            d.msgbox("Masquerade remove on zones: \n %s" % str(tags))
            masqueradeactionsmenu()
        else:
            d.msgbox("You didn't select a zone to set masquerade.")
            removepermmasq() 
    else:
        masqueradeactionsmenu()

def removenonpermmasq():
    cmd="firewall-cmd --list-all-zones | egrep '^\S|masquerade'"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    masqlist = re.findall(r'(\w+)\n\s+masquerade:\s+(\w+)\n', output)
    # check non masq zones and create list with manu tags "[(opt1, "", False), ...]"
    selectmasq4zone = [ (i[0], "", False) for i in masqlist if "yes" in i[1]]
    code, tags = d.checklist("Select Zones to remove masquerade on" ,
                            choices=selectmasq4zone,
                            title="Zone Selection",
                            backtitle="Firewall Administration Menu "
                            "Tui Version")
    if code == d.OK:
        if tags:
            for item in tags:
                cmd="firewall-cmd --remove-masquerade --zone=%s" % item
                p = Popen(cmd, stdout=PIPE, shell=True)
                output, error = p.communicate()
            d.msgbox("Masquerade remove on zones: \n %s" % str(tags))
            masqueradeactionsmenu()
        else:
            d.msgbox("You didn't select a zone to set masquerade.")
            removenonpermmasq() 
    else:
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
            addpermmasq()
        elif tags == "(2)":
            addnonpermmasq()
        elif tags == "(3)":
            querypermmasq()
        elif tags == "(4)":
            querynonpermmasq()
        elif tags == "(5)":
            removepermmasq()
        elif tags == "(6)":
            removenonpermmasq()
    else:
        selectedzone = ""
        main()

def reloadaction():
    cmd="firewall-cmd --reload"
    p = Popen(cmd, stdout=PIPE, shell=True)
    output, error = p.communicate()
    code, tags = d.msgbox("Reload executed with status: \n %s" % output)
    reloadmenu()

def completereloadaction():
    code = d.yesno("Are you sure? this will kill all stablished sessions.")
    if code == d.OK:
        cmd="firewall-cmd --reload"
        p = Popen(cmd, stdout=PIPE, shell=True)
        output, error = p.communicate()
        code, tags = d.msgbox("Complete Reload executed with status: \n %s" % output)
        reloadmenu()
    else:
        reloadmenu()

def runtoperm():
    code = d.yesno("Are you sure? this will rewrite all your permanent settings.")
    if code == d.OK:
        cmd="firewall-cmd --runtime-to-permanent"
        p = Popen(cmd, stdout=PIPE, shell=True)
        output, error = p.communicate()
        code, tags = d.msgbox("Complete Reload executed with status: \n %s" % output)
        reloadmenu()
    else:
        reloadmenu()

def reloadmenu():
    code, tags = d.menu("Select an Action to perform ",
            choices= [("(1)", "Firewall Reload"),
            ("(2)", "Firewall Complete Reload"),
            ("(3)", "Runtime to Permanent"),],
            title="Reload and Runtime Selection",
            backtitle="Firewalld Administration Menu Tui Version")
    if code == d.OK:
        if tags == "(1)":
            reloadaction()
        elif tags == "(2)":
            completereloadaction()
        elif tags == "(3)":
            runtoperm()
    else:
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
            title="Top Menu - Actions Selection",
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
            reloadmenu()
    else:
        code, tags = d.menu("Please select an Action:",
            choices=[("(1)", "Exit utility"),
            ("(2)", "Back to Top Menu")])
        if code == d.OK:
            if tags == "(1)":
                exit("Thansk for using this tool.")
            elif tags == "(2)":
                main()
        else:
            exit("Thansk for using this tool.")

if __name__  == "__main__":
    main()