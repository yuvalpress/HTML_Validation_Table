from bs4 import BeautifulSoup #for html editing

#for system control
import os
import shutil

#for creating and appending to log file
import logging

#for reading from excel file
import xlrd

#Choose files and folders interface
from tkinter import filedialog
from tkinter import Tk

from time import sleep

#for executing subprocesses
import subprocess

import paramiko #FOr linux commands execution

from netaddr import IPNetwork

def ping(ip): #Check ping response

    #ping requested server
    try:
        ping = subprocess.Popen(
            ["ping", "-n", "1", '{}'.format(ip)],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        out, error = ping.communicate()
    except:
        logging.error(error)

    if "TTL" in str(out):
        return True
    else: return False

def whichServer(ex): #Check which servers are found inside the main excel sheet
    wb = xlrd.open_workbook(ex)
    sheet = wb.sheet_by_name("Servers")
    serverTypes = []
    for i in range(5, sheet.nrows, +1):
        if sheet.cell_value(i, 3) not in serverTypes:
            serverTypes.append(sheet.cell_value(i, 3))
    
    return serverTypes

def allFromType(ex, serverName, cols): #Get all servers from specific type from the main excel sheet
    wb = xlrd.open_workbook(ex)
    sheet = wb.sheet_by_name("Servers")
    allServersOfType = {}

    for i in range(5, sheet.nrows, +1):
        if sheet.cell_value(i, 3) in serverName:
            allServersOfType[map(lambda v: str(sheet.cell_value(4, v)), cols)] = list(map(lambda v: str(sheet.cell_value(i, v)), cols))


    return allServersOfType 

def idracIPFields(exValues, psValues): #Check the iDrac ip address, subnet and default gateway
    if exValues == psValues:
        return "<td class='bg-success'>iDrac IP OK</td>"
    else:
        tag = '<td class="bg-danger">'
        for ipPartExValue, ipPartValue, value in zip(exValues, psValues, ["IP", "Subnet", "Gateway"]):
            if ipPartExValue != ipPartValue:
                tag += value + ":" + ipPartValue + " "
        tag += "</td>"
        return tag

def ipFields(exValues, psValues): #Check the management ip address, subnet and default gateway

    if exValues == psValues:
        return "<td class='bg-success'>IP OK</td>"
    else:
        tag = '<td class="bg-danger">'
        for ipPartExValue, ipPartValue, value in zip(exValues, psValues, ["IP", "Subnet", "Gateway"]):
            if ipPartExValue != ipPartValue:
                tag += value + ":" + ipPartValue + " "
        tag += "</td>"
        return tag

def iniTable(ex, serverName, cols): #Initialize the start of a new table
    table = "<div class=\"mainDiv\"><h1>{}</h1><table class='table mainTable'><thead class='thead-dark'><tr>".format(serverName + " Servers") #Create start of table
    idracTable = "<table class='table mainTable'><thead class='thead-dark'><tr><th scope='col'>iDrac Name</th><th scope='col'>Service Tag</th><th scope='col'>IP Address</th><th scope='col'>LOM\\Dedicated</th><th scope='col'>Console Type</th><th scope='col'>Raid Type</th></tr></thead><tbody>"

    #Get data from excel sheet
    wb = xlrd.open_workbook(ex)
    sheet = wb.sheet_by_name("Servers")

    for i in range(len(cols)): table += "<th scope='col'>" + sheet.cell_value(4, cols[i]) + "</th>"
    table += "</tr></thead><tbody>"
    
    return table, idracTable

def td(check, value, title, isLinux=None, nameserver1=None, nameserver2=None): #Check a value of specific setting got in the check and value expressions for excel value and retrieved scripts value and the title of the setting
    
    if title == "Hostname":
        tag = "<td class='bg-success'>{}</td>".format(value) if str(check) == str(value) else "<td class='bg-danger'>{}</td>".format(value)
        logging.info("Hostname was added to tr tag")

    elif title == "OS":
        if isLinux:
            tag = "<td class='bg-success'>{}</td>".format(value) if str(value) in str(check) else "<td class='bg-danger'>{}</td>".format(value)
        else:
            tag = "<td class='bg-success'>{}</td>".format(value) if str(check) in str(value) or str(check)[:-2] in str(value) else "<td class='bg-danger'>{}</td>".format(value)
        logging.info("Operating System was added to tr tag")

    elif title == "License":
        tag = "<td class='bg-success'>License Applied</td>" if "true" in str(check) else "<td class='bg-danger'>No License Applied</td>"
        logging.info("License was added to tr tag")

    elif title == "NTP":
        if isLinux:
            tag = "<td class='bg-success'>{}</td>".format(value) if str(value) in str(check) else "<td class='bg-danger'>{}</td>".format(value)
        else:
            tag = "<td class='bg-success'>{}</td>".format(value) if str(check) == str(value) else "<td class='bg-danger'>{}</td>".format(value)
        logging.info("NTP was added to tr tag")

    elif title == "Raid":
        tag = "<td class='bg-success'>{}</td>".format(value) if str(check) in str(value) else "<td class='bg-danger'>{}</td>".format(value)
        logging.info("Raid Configuration was added to tr tag")

    elif title == "Domain":
        if isLinux: #if linux server
            if nameserver1 != None and nameserver2 != None:
                if str(value) in str(check) and str(nameserver1) in str(check) and str(nameserver2) in str(check):
                    print("hi success")
                    tag = "<td class='bg-success'>{}</td>".format(value)
                else: 
                    tag = "<td class='bg-danger'>{}</td>".format(value)

            elif nameserver1 != None and nameserver2 == None:
                if str(nameserver1) in str(check) and str(value) in str(check):
                    print("hello")
                    tag = "<td class='bg-success'>{}</td>".format(value)
                else: 
                    tag = "<td class='bg-danger'>{}</td>".format(value)
                    print("hello")

            elif nameserver2 != None and nameserver1 == None:
                if str(nameserver2) in str(check) and str(value) in str(check):
                    print("bla")
                    tag = "<td class='bg-success'>{}</td>".format(value)
                else: 
                    tag = "<td class='bg-danger'>{}</td>".format(value)
                    print("bla")

        else: #if windows server      
            tag = "<td class='bg-success'>{}</td>".format(value) if str(value) in str(check) else "<td class='bg-danger'>{}</td>".format(value)
    
    elif title == "Teaming":
        tag = "<td class='bg-success'>Teaming Applied</td>" if check != None else "<td class='bg-danger'>Teaming Not Applied</td>"

    elif title == "Timezone":
        tag = "<td class='bg-success'>{}</td>".format(value) if str(check) == str(value) else "<td class='bg-danger'>{}</td>".format(value)


    return tag

def datastoreTd(ex, ip): #Create datastores tag bt getting the sheet of datastores supposed to be found on the esx server and ip address of the esx server
    logging.info("--------------------------------------------------------------------------------------------------------------------------")
    logging.info("Started Datastores Validations")
    tag = '' #Create datastores drop down td tag

    #read datastores data from excel file
    wb = xlrd.open_workbook(ex)
    sheet = wb.sheet_by_name("Datastores")
    datastores = []

    #get all data cells
    for i in range(1, sheet.nrows, +1):
        datastores.append(sheet.cell_value(i, 0))
    logging.info("Fetched all data from Datastores sheet")
    
    sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\ESXi\\datastores.ps1' {}".format(os.environ['USERPROFILE'], ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Execute datastores script
    lines = sub.stdout.readlines()

    names = (str(lines[4]).strip("b'").strip("\\r\\n")).split(',') #Get datastores names from script
    sizes = (str(lines[5]).strip("b'").strip("\\r\\n")).split(',') #Get datastores sizes from script
    adapterNames = (str(lines[6]).strip("b'").strip("\\r\\n")).split(',') #Get storage devices names
    adapterTargets = (str(lines[7]).strip("b'").strip("\\r\\n")).split(',') #Get storage adapters targets
    adapterDCount = (str(lines[8]).strip("b'").strip("\\r\\n")).split(',') #Get storage devices count
    adapterPaths = (str(lines[9]).strip("b'").strip("\\r\\n")).split(',') #Get storage adapters paths
    logging.info("Fetched all data from Datastores script")

    success = [] #list created to store True values for every datastore name found in retrieved datastores names

    #Check if all datastores exists with the right name
    for rName in range(0, len(datastores)):
        for subName in range(0, len(names)):
            if datastores[rName] == names[subName]:
                logging.info("Datastore {} exists".format(datastores[rName]))
                success.append(True)
                break
    
    #Create the datastore tag with drop down menu
    if len(success) == len(datastores) == len(names):
        logging.info("All datastores are exist with the right names")

        tag += "<td class='bg-success'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">Name</th><th scope=\"col\">Size</th></tr></thead><tbody>".format("Datastores", len(names))
        for i in range(0, len(names)):
            tag += "<tr><td>{}</td><td>{}</td></tr>".format(names[i], sizes[i])
        logging.info("Finished datastores tag creation")
        tag += "</tbody></table>"

        if adapterNames[0] != '':
            tag += "<div class='dropdown-divider'></div>"
            for i in range(0, len(adapterNames)):
                tag += "<a class='dropdown-item text-1' href='#'><strong>Adapter:</strong> {} - <strong>Targets:</strong> {} - <strong>Devices:</strong> {} - <strong>Paths:</strong> {}</a>".format(adapterNames[i], adapterTargets[i], adapterDCount[i], adapterPaths[i])
            logging.info("Finished storage adapters tag creation")

    else:
        logging.info("Not all Datastores exists")

        tag += "<td class='bg-danger'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">Name</th><th scope=\"col\">Size</th></tr></thead><tbody>".format("Datastores", len(datastores))
        for i in range(0, len(names)):
            tag += "<tr><td>{}</td><td>{}</td></tr>".format(names[i], sizes[i])
        logging.info("Finished datastores tag creation")
        tag += "</tbody></table>"

        if adapterNames[0] != '':
            tag += "<div class='dropdown-divider'></div>"
            print(adapterNames)
            for i in range(0, len(adapterNames)):
                print(i)
                tag += "<a class='dropdown-item text-1' href='#'><strong>Adapter:</strong> {} - <strong>Targets:</strong> {} - <strong>Devices:</strong> {} - <strong>Paths:</strong> {}</a>".format(adapterNames[i], adapterTargets[i], adapterDCount[i], adapterPaths[i])

    tag += "</div></div></div></td>" #Close tag

    return tag

def vmsTd(supposed, ip): #Create virtual machines tag by getting a number of how many machines supposed to be found and ip address of esxi server
    logging.info("--------------------------------------------------------------------------------------------------------------------------")
    logging.info("Started Virtual Machines Validations")
    tag = '' #Create datastores drop down td tag   

    sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\ESXi\\vms.ps1' {}".format(os.environ['USERPROFILE'], ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Execute datastores script
    lines = sub.stdout.readlines()

    #Check if vms exists on current esx server and assign values to variables as needed
    if str(lines[4]).strip("b'").strip("\\r\\n") != 'false':
        vmsName = (str(lines[4]).strip("b'").strip("\\r\\n")).split(',') #Get virtual machines names from script
        vmsOS = (str(lines[5]).strip("b'").strip("\\r\\n")).split(',') #Get virtual machines operating systems from script
        vmsMemory = (str(lines[6]).strip("b'").strip("\\r\\n")).split(',') #Get virtual machines Memory from script
        vmsCores = (str(lines[7]).strip("b'").strip("\\r\\n")).split(',') #Get virtual machines Cores from script

    else: vmsName, vmsOS, vmsMemory, vmsCores = ['false'], ['false'], ['false'], ['false']
    
    logging.info("Fetched all data from Virtual Machines script")

    # print("supposed:", supposed, "length vmsName:", len(vmsName), "first:", vmsName[0])
    if int(supposed) == len(vmsName) or int(supposed) == 0 and vmsName[0] == "false":
        if vmsName[0] != 'false':
            logging.info("All Virtual Machines exists")

            tag += "<td class='bg-success'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">VM Name</th><th scope=\"col\">OS</th><th scope=\"col\">Memory</th><th scope=\"col\">Cores</th></tr></thead><tbody>".format("Virtual Machines", supposed)

            for i in range(0, len(vmsName)):
                tag += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(vmsName[i], vmsOS[i], vmsMemory[i], vmsCores[i])
            tag += "</tbody></table>"

        else:
            logging.info("NO virtual Machines exist, as needed")

            tag += "<td class='bg-success'>{} - {}</td>".format("Virtual Machines", supposed)

        logging.info("Finished Virtual Machines tag creation")
    
    else:
        if vmsName[0] != 'false':
            logging.error("Not all Virtual Machines exists")

            tag += "<td class='bg-danger'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">VM Name</th><th scope=\"col\">OS</th><th scope=\"col\">Memory</th><th scope=\"col\">Cores</th></tr></thead><tbody>".format("Virtual Machines", supposed)
            for i in range(0, len(vmsName)):
                tag += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(vmsName[i], vmsOS[i], vmsMemory[i], vmsCores[i])
            tag += "</tbody></table>"
        
        else:
            logging.info("NO virtual Machines exist")

            tag += "<td class='bg-danger'>{} - {}</td>".format("Virtual Machines", supposed)

        logging.info("Finished Virtual Machines tag creation")

    if len(vmsName[0]) != 0:
        tag += "</div></div></div></td>" #Close tag
        return tag
    else:
        return tag

def vswitchTd(supposed, ip): #This method creates a vswitch and portgroups tag by getting a number of vswitches needed to be located and the ip address of the esx server
    logging.info("--------------------------------------------------------------------------------------------------------------------------")
    logging.info("Started Virtual Switches Validations")
    tag = '' #Create datastores drop down td tag   

    sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\ESXi\\vswitch_pgroup.ps1' {}".format(os.environ['USERPROFILE'], ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Execute datastores script
    lines = sub.stdout.readlines()

    vsNames = (str(lines[4]).strip("b'").strip("\\r\\n")).split(',') #Get virtual switches names from script
    vsCoNames = (str(lines[5]).strip("b'").strip("\\r\\n")).split(',') #Get virtual switches names that corespondes to the pgCoNames variable
    pgCoNames = (str(lines[6]).strip("b'").strip("\\r\\n")).split(',') #Get port groups names that corespondes to the vsCoNames variable

    if int(supposed) == len(vsNames):
        if len(vsNames) != 0:
            logging.info("All Virtual Switches exists")

            tag += "<td class='bg-success'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">VSwitch Name</th><th scope=\"col\">PortGroups</th></tr></thead><tbody>".format("Virtual Switches", len(vsNames))
            for vs in range(0, len(vsNames)):
                pgs = []
                for pg in range(0, len(pgCoNames)):
                    if vsNames[vs] in vsCoNames[pg]:
                        pgs.append(pgCoNames[pg])
                tag += "<tr><td>{}</td><td>{}</td></tr>".format(vsNames[vs], ', '.join(pgs))
            tag += "</tbody></table>"
        
        else:
            logging.info("No Virtual Switches exist, as needed")

            tag += "<td class='bg-success'>{} - {}</td>".format("Virtual Switches", len(vsNames))

        logging.info("Finished Virtual Switches tag creation")
    
    else:
        if len(vsNames) != 0:
            logging.info("Not all Virtual Switches exists")

            tag += "<td class='bg-danger'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">VSwitch Name</th><th scope=\"col\">PortGroups</th></tr></thead><tbody>".format("Virtual Switches", supposed)
            for vs in range(0, len(vsNames)):
                pgs = []
                for pg in range(0, len(pgCoNames)):
                    if vsNames[vs] in vsCoNames[pg]:
                        pgs.append(pgCoNames[pg])
                tag += "<tr><td>{}</td><td>{}</td></tr>".format(vsNames[vs], ', '.join(pgs))
            tag += "</tbody></table>"

        else:
            logging.info("No Virtual Switches exist")

            tag += "<td class='bg-danger'>{} - {}</td>".format("Virtual Switches", len(vsNames))

        logging.info("Finished Virtual Switches tag creation")
    
    if len(vsNames) != 0:
        tag += "</div></div></div></td>" #Close tag
        return tag
    else:
        return tag

def intoFile(htmlFile, section, tag="tag", name="str"):
    page = open(htmlFile) #open html file
    tag = BeautifulSoup(tag, "html.parser") #Convert string to bs4 format
    soup = BeautifulSoup(page.read(), "html.parser") #read html page content

    if section == "name":
        soup.find("h1").insert(0, name + " Project" + " Validation")

    if section == "start": #if a tag represents start of html page or table
        if "table" in str(tag): #if the tag represents a new table then enter it after the last existing table is exist of right after the div tag
            if "table" not in str(soup):
                soup.find("body").find("h1").insert_after(tag)

            elif "table" in str(soup):
                divs = []
                for div in soup.find_all("div", class_="mainDiv"): divs.append(div)

                tables = []
                if "mainDiv" in str(tag):
                    divs[-1].insert_after(tag)
                else:
                    for table in divs[-1].find_all("table", class_='mainTable'): tables.append(table)
                    tables[-1].insert_after(tag)
                
    elif section == "continue": #if the tag represents an extention of an existing table
        if "tr" in str(tag): #if its a table tr content tag
            if len(soup.findAll("tr")) == 1: #if only the thead tr tag exists
                soup.findAll("tbody")[-1].insert(0, tag)

            else: #if more then one tr tag exists then enter the tag after the last one
                body = soup.find_all("tbody")[-1]
                if len(body.find_all("tr")) != 0:
                    soup.findAll("tr")[-1].insert_after(tag)
                else:
                    body.insert_after(tag)

        elif "tbody" in str(tag): #End the tbody tag of the table
            soup.findAll("tr")[-1].insert_after(tag)

    #Save new tag to file
    with open(htmlFile, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

def esxi(ex, page): #A method to create a validation for all esxi servers

    table, idracTable = iniTable(ex, "ESXi", [4,8,14,16,17,18,19,11]) #Create table
    intoFile(page, tag=table, section="start") #Write into file
    logging.info("Initialized start of an ESXi table")
    tag="<tr>" #Declare start of tag
    idracTag="<tr>"

    #get all esxi servers data by specific cells from values list
    servers = allFromType(excel_file, "ESXi", [4,5,6,7,8,9,10,11,13,14,16,17,18,19])
    logging.info("Fetched ESXi servers data")

    #get ip addresses for idrac and mgmt
    commandVars, idracCommandVars = '', ''
    nonPingable = []
    for value in servers:
        item = list(servers[value])
        if ping(item[4]):
            commandVars = commandVars + "'" + item[4] + "'" + ' '
            idracCommandVars = idracCommandVars + "'" + item[1] + "'" + ' '
        else:
            nonPingable.append(item[0])

    commandVars = commandVars[:-1]
    idracCommandVars = idracCommandVars[:-1]
    print(commandVars)
    logging.info("ESXi validation will be performed on servers: {}".format(commandVars))

    if len(commandVars) != 0:
        sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\iDrac\\idrac_data.ps1' {}".format(os.environ['USERPROFILE'], idracCommandVars)], stdout=subprocess.PIPE, stderr=None) #Execute racadm script
        idracIpValues = [i.split() for i in ((str(sub.stdout.readlines()[-1]).strip("b'").strip("\\r\\n'"))[:-6]).split(' next ')]
        
        sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\ESXi\\ip.ps1' {}".format(os.environ['USERPROFILE'], commandVars)], stdout=subprocess.PIPE, stderr=None) #Execute PowerCLI ip script
        ipValues = [i.split() for i in ((str(sub.stdout.readlines()[-1]).strip("b'").strip("\\r\\n'"))[:-6]).split(' next ')]

        sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\ESXi\\config.ps1' {}".format(os.environ['USERPROFILE'], commandVars)], stdout=subprocess.PIPE, stderr=None) #Execute PowerCLI script
        values = [i.split() for i in ((str(sub.stdout.readlines()[-1]).strip("b'").strip("\\r\\n'"))[:-6]).split(' next ')] #Get output from script, clean it and create a list from it


        for data, ipData, idracIPData, exData in zip(values, ipValues, idracIpValues, servers):

            item = list(servers[exData])
            logging.info("Started writing tr tag for ESX Server {}".format(item[4]))
            # print(data[0].split(','), ipData[0].split(','), idracIPData[0].split(','), item)

            #check what is pingable
            tag += td(data[0].split(",")[0], item[0], "Hostname") #Add hostname to tr tag

            tag += ipFields(ipData[0].split(","), [item[4], item[5], item[6]]) #Check management ip address

            tag = tag + ''.join(list(map(td, [data[0].split(",")[i] for i in range(1, len(data[0].split(","))-4)], [item[9], item[10]], ["OS", "License"]))) #Add OS and License to tr tag

            tag += datastoreTd(ex, item[4]) #Add datastores to tr tag

            tag += vmsTd(item[12], item[4]) #Add Virtual Machines to tr tag

            tag += vswitchTd(item[13], item[4]) #Add Virtual Switches to tr tag

            tag = tag + ''.join(list(map(td, [data[0].split(",")[i] for i in range(6, len(data[0].split(",")))], [item[7]], ["NTP"]))) #Add NTP to tr tag

            #Check iDrac hostname
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-1])

            #Check iDrac Service tag
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-2])

            #Check iDrac ip address
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += idracIPFields([idracIPData[0].split(",")[i] for i in range(0, len(idracIPData[0].split(","))-6)], [item[1], item[2], item[3]])

            else: 
                idracTag += "<td class='bg-danger'>No Ping</td>"
            
            #Check iDrac LOM Settings
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-3])

            #Check iDrac vconsole Settings
            if idracIPData[0].split(",")[0] not in "NoPing":
                type = idracIPData[0].split(',')[-4]
                if type == 1:
                    idracTag += "<td class=\"bg-success\">Java</td>"
                else:
                    idracTag += "<td class=\"bg-success\">HTML5</td>"
            
            #Add Raid configuration to tr tag
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += td(idracIPData[0].split(',')[-2], item[8], "Raid")
            else:
                idracTag += "<td class='bg-warning'>No Data Fetched</td>"
            
            tag += "</tr>"
            idracTag += "</tr><tr>"
            intoFile(page, tag=tag, section="continue")
            tag = '<tr>'
            logging.info("Finished writing tr tag for ESX {}".format(item[4]))

    else:
        logging.error("No pingable IP Addresses found for esxi servers.")
    
    #add all unpingable servers to the table
    for name in nonPingable:
        i=1
        tag += "<td class='bg-success'>{}</td>".format(name)
        tag += "<td class='bg-danger'>No Ping</td>"
        while i <= 6:
            i += 1
            tag += "<td class='bg-warning'>No Data Feched</td>"
        tag += "</tr>"
        intoFile(page, tag=tag, section="continue")
        tag = "<tr>"

    intoFile(page, tag="</tbody>" + "</table>" + "</div>", section="continue")
    
    idracTag = idracTag[:-4]
    intoFile(page, tag=idracTable, section="start")
    intoFile(page, tag=idracTag, section="continue")
    logging.info("Finished writing tr tag for the iDrac table of ESX servers {}".format(item[4]))
    intoFile(page, tag="</tbody>" + "</table>", section="continue")

def linux(ex, page):

    table, idracTable = iniTable(ex, "Linux", [4,8,12,14,20,21,22,11]) #Create table
    intoFile(page, tag=table, section="start") #Write into file
    logging.info("Initialized start of an Linux table")
    tag="<tr>" #Declare start of tag
    idracTag="<tr>" #Declare start of idracTag

    #get all linux servers data by specific cells from values list
    servers = allFromType(excel_file, "Linux", [4,5,6,7,8,9,10,12,14,20,21,22,11,13])
    logging.info("Fetched Linux servers data")

    #get ip addresses for idrac and mgmt
    mgmtAddresses, idracAddresses = [], ''
    nonPingable = []
    for value in servers:
        item = list(servers[value])
        if ping(item[4]):
            mgmtAddresses.append(item[4])
            idracAddresses = idracAddresses + "'" + item[1] + "'" + ' '
        else:
            nonPingable.append(item[0])

    idracAddresses = idracAddresses[:-1]
    print(mgmtAddresses)
    logging.info("Linux validation will be performed on servers: {}".format(i + "," for i in mgmtAddresses))

    if len(mgmtAddresses) != 0:

        #Run idrac data validation
        sub = subprocess.Popen(["powershell", "& '{}\\Desktop\\Scripts\\One Page Validation\\Get_Data\\iDrac\\idrac_data.ps1' {}".format(os.environ['USERPROFILE'], idracAddresses)], stdout=subprocess.PIPE, stderr=None) #Execute racadm script
        idracValues = [i.split() for i in ((str(sub.stdout.readlines()[-1]).strip("b'").strip("\\r\\n'"))[:-6]).split(' next ')]

        #List of commands to execute
        commands = ["hostname -I | awk '{print $1}'",
                    'ip route | grep "src $MAINIP"' + " | awk '{print $0}' " + "| grep $(ip addr | awk '/state UP/ {print $2}' | sed 's/.$//') | awk '{print $1}'",
                    "ip route show | grep default | grep $(ip addr | awk '/state UP/ {print $2}' | sed 's/.$//') | awk '{print $3}'",
                    'hostname', 
                    'ifconfig', 
                    'yum repolist', 
                    'lsblk', 
                    'cat /etc/resolv.conf', 
                    'cat /etc/chrony.conf', 
                    'cat /etc/sysconfig/network-scripts/ifcfg-team0', 
                    'for i in $(ls /etc/*release); do cat $i; done', 
                    'date',
                    'mv /etc/localtime /etc/localtime.backup',
                    'ln -s /usr/share/zoneinfo/UTC /etc/localtime',
                    'echo '"=UTC"' > /etc/sysconfig/clock',
                    'cat /etc/sysconfig/clock']

        outs = {} #Declare outputs dict
        serversOutput = []

        for address in mgmtAddresses:
            #create client for communication
            client = paramiko.client.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            client.connect(hostname=address, username="root", password="Customer1!")

            #Execute all commands from list on remote server and fetch outputs
            for command, i in zip(commands, range(0, len(commands), +1)):
                stdin, stdout, stderr = client.exec_command(command)
                out = stdout.readlines()

                if i == 0:
                    outs["ip"] = str(out[0]).strip('\n')
                    
                elif i == 1:
                    outs["subnet"] = str(IPNetwork(str(out[0]).strip('\n')).netmask).strip("(")
                    
                elif i == 2:
                    outs["gateway"] = str(out[0]).strip('\n')

                elif i == 3:
                    outs["hostname"] = str(out[0]).strip("\n")

                elif i == 4:
                    outs["network"] = str(out)

                elif i == 5:
                    outs["repo"] = out

                elif i == 6:
                    outs["storage"] = str(out)

                elif i == 7:
                    outs["resolv"] = str(out).replace("\\n",'')

                elif i == 8:
                    outs["chrony"] = str(out)
                    
                elif i == 9:
                    if not out:
                        outs["teaming"] = None
                    else: outs["teaming"] = str(out)
                    
                elif i == 10:
                    outs["release"] = str(out)
                    
                elif i == 11:
                    outs["date"] = str(out[0]).strip("\n")
                    
                elif i == 15:
                    outs["timezone"] = str(out[0]).strip("\n").replace("=", "")

            serversOutput.append(outs)

        #Get nameserver from excel sheet
        wb = xlrd.open_workbook(ex)
        sheet = wb.sheet_by_name("Servers")

        nameserver1 = sheet.cell_value(1,5) #Declare nameserver1
        nameserver2 = sheet.cell_value(1,6) #Declare nameserver2

        #Start validation
        for idracIPData, server, exData in zip(idracValues, serversOutput, servers):

            item = list(servers[exData])
            logging.info("Started writing tr tag for Linux Server {}".format(item[4]))
            # print(data[0].split(','), ipData[0].split(','), idracIPData[0].split(','), item)

            #check what is pingable
            tag += td(server["hostname"], item[0], "Hostname") #Add hostname to tr tag

            tag += ipFields([server["ip"], server["subnet"], server["gateway"]], [item[4], item[5], item[6]]) #add ip mgmt to tr tag

            #add domain td tag to main tag
            if nameserver1 != "" and nameserver2 != "":
                tag += td(server["resolv"], item[7], "Domain", isLinux=True, nameserver1=nameserver1, nameserver2=nameserver2)
            elif nameserver1 != "" and nameserver2 == "":
                tag += td(server["resolv"], item[7], "Domain", isLinux=True, nameserver1=nameserver1)
            elif nameserver1 == "" and nameserver2 != "":
                tag += td(server["resolv"], item[7], "Domain", isLinux=True, nameserver2=nameserver2)

            tag += td(server["release"], item[8], "OS", isLinux=True) #add operating system to tr tag

            #add repositories to tr tag
            tag += "<td class='bg-success'><div class='btn-group flex-wrap'><button type='button' class='m-0 btn btn-default dropdown-toggle' data-toggle='dropdown'>{} - {}<span class='caret'></span></button><div class='dropdown-menu dropdown-menu-right' role='menu'><div class=\"dropdown-item text-1\"><table class=\"table\"><thead class=\"thead-dark\"><tr><th scope=\"col\">Repository</th></tr></thead><tbody>".format("Repositories", len(server["repo"])-2)
            for repo in range(2, len(server["repo"])):
                tag += "<tr><td class=\"td1\">{}{}</td></tr>".format("{}. ".format(repo-1), str(server["repo"][repo]))
            tag += "</div></div></div></td>"

            #add teaming to tr tag
            tag += td(server["teaming"], item[10], "Teaming")

            #add timezone to tr tag
            tag += td(server["timezone"], item[11], "Timezone")

            #add NTP Server to tr tag
            tag += td(server["chrony"], item[12], "NTP", isLinux=True)


            #Check iDrac hostname
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-1])

            #Check iDrac Service tag
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-2])

            #Check iDrac ip address
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += idracIPFields([idracIPData[0].split(",")[i] for i in range(0, len(idracIPData[0].split(","))-6)], [item[1], item[2], item[3]])

            else: 
                idracTag += "<td class='bg-danger'>No Ping</td>"
            
            #Check iDrac LOM Settings
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += "<td class=\"bg-success\">{}</td>".format(idracIPData[0].split(',')[-3])

            #Check iDrac vconsole Settings
            if idracIPData[0].split(",")[0] not in "NoPing":
                vType = idracIPData[0].split(',')[-4]
                if vType == 1:
                    idracTag += "<td class=\"bg-success\">Java</td>"
                else:
                    idracTag += "<td class=\"bg-success\">HTML5</td>"
            
            #Add Raid configuration to tr tag
            if idracIPData[0].split(",")[0] not in "NoPing":
                idracTag += td(idracIPData[0].split(',')[-2], item[8], "Raid")
            else:
                idracTag += "<td class='bg-warning'>No Data Fetched</td>"

            tag = tag + "</tr>"
            idracTag += "</tr><tr>"
            intoFile(page, tag=tag, section="continue")
            tag = '<tr>'
            logging.info("Finished writing tr tag for Linux server {}".format(item[4]))
    else:
        logging.error("No pingable IP Addresses found for esxi servers.")
    
    #Default all non-pingable servers
    for name in nonPingable:
        i=1
        tag += "<td class='bg-success'>{}</td>".format(name)
        tag += "<td class='bg-warning'>No Data Fetched</td>"
        tag += "<td class='bg-danger'>No Ping</td>"
        while i <=7:
            i += 1
            tag += "<td class='bg-warning'>No Data Feched</td>"
        tag += "</tr>"
        intoFile(page, tag=tag, section="continue")
        tag = "<tr>"

    intoFile(page, tag="</tbody>" + "</table>" + "</div>", section="continue")

    idracTag = idracTag[:-4]
    intoFile(page, tag=idracTable, section="start")
    intoFile(page, tag=idracTag, section="continue")
    logging.info("Finished writing tr tag for the iDrac table of ESX servers {}".format(item[4]))
    intoFile(page, tag="</tbody>" + "</table>", section="continue")

if __name__ == '__main__':

    #Create a window for files gathering process
    root = Tk()

    #Choose validations folder's location
    root.withdraw()
    folder_selected = filedialog.askdirectory()

    #Choose excel validation file
    root.withdraw()
    excel_file = filedialog.askopenfilename(filetypes =[('Excel Files', '*.xlsx')])

    #Create log file and folder if not already exist
    try:
        if os.path.isdir('{}\\Logs'.format(folder_selected)):
            shutil.rmtree('{}\\Logs'.format(folder_selected))
        os.mkdir('{}\\Logs'.format(folder_selected))
        logging.basicConfig(filename='{}\\Logs\\log.txt'.format(folder_selected), level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    except (PermissionError) as e:
        logging.error(e)
        os._exit(1)

    #Create new html file from template and assign it to variable
    page = "{}\\report.html".format(folder_selected)
    with open ("Web_Page\\validation.html") as file:
        with open(page, 'w') as p:
            p.write(file.read())

    #Change validations name
    wb = xlrd.open_workbook(excel_file)
    sheet = wb.sheet_by_name("Servers")
    name = sheet.cell_value(1, 7)
    intoFile(page, section="name", name=name)


    #Get servers to validate
    serversList = whichServer(excel_file)

    #start validations process
    for servers in serversList:
        if 'ESXi' in servers:
            logging.info("Called ESXi method")
            esxi(excel_file, page)

        elif 'Linux' in servers:
            logging.info("Called Linux method")
            linux(excel_file, page)