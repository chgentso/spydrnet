"""
=====================================
Display Information Functions
=====================================

Some example functions that can be run to display information in a netlist.
1) Print the hierarchy in a netlist
2) Print each library with its definitions in a netlist
3) Print wire connects between ports in a netlist

"""

import spydrnet as sdn

netlist = sdn.load_example_netlist_by_name("fourBitCounter")

#print the hierarchy of a netlist
def hierarchy(current_instance,indentation=""):
    print(indentation,current_instance.name," --instance of",current_instance.reference.name,"--")
    for child in current_instance.reference.children:
        hierarchy(child,indentation+"     ")

#prints a list of all libraries and definitions in a netlist
def libraries_definitions(my_netlist):
    for library in my_netlist.libraries:
        definitions = list(definition.name for definition in library.definitions)
        print("DEFINITIONS IN '",library.name,"':",definitions)

#prints the connections in a netlist
def print_connections(current_netlist):
    print("CONNECTIONS:")
    for instance in current_netlist.get_instances():
        print("Instance name:",instance.name)
        for pin in instance.pins:
            IN = "EXTERNAL"
            OUT = "EXTERNAL"        
            for pin in pin.wire.pins:
                instance = list(instance.name for instance in pin.get_instances())
                for port in pin.get_ports():
                    #for each pin, get the associate port and check the direction
                    if port.direction is sdn.IN:
                        if IN is "EXTERNAL":
                            IN = port.name + " of " + str(instance)
                        else:
                            IN = IN + ", " + port.name + " of " + str(instance)
                    elif port.direction is sdn.OUT:
                        if OUT is "EXTERNAL":
                            OUT = port.name + " of " + str(instance)
                        else:
                            OUT = OUT + ", " + port.name + " of " + str(instance)
            print("\t",OUT,"connects to",IN)


print("HIERARCHY:")
hierarchy(netlist.top_instance)
libraries_definitions(netlist)
print_connections(netlist)