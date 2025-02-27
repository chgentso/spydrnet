"""
====================================
Four Bit Counter To Five Bit Counter
====================================

Extend a four bit counter to a 5 bit counter.
"""


import spydrnet as sdn

# Gets the outer_pin for a given port identifier
# instance: sdn.Instance to find the pin on
# identifier: The string identifier the the port we want
# Returns associated outer_pin or None if instance
# Note: Only works with ports of length 1


def get_pin(instance, identifier):
    # Loop through each key-map pair of instance's pin
    for inner_pin, outer_pin in instance.pins.items():
        # Check if the port has the correct identifier
        if inner_pin.port['EDIF.identifier'] == identifier:
            # If port as the right identifier, return the outer_pin
            return outer_pin
    # Return None if instance does not have matching port
    return None


# Loads the example
ir = sdn.load_example_netlist_by_name("fourBitCounter")

# Retrieves needed libraries and definitions
primitives_library = next(
    x for x in ir.libraries if x['EDIF.identifier'] == 'hdi_primitives')
work_library = next(x for x in ir.libraries if x['EDIF.identifier'] == 'work')
fdce_definition = next(
    x for x in primitives_library.definitions if x['EDIF.identifier'] == 'FDCE')
obuf_definition = next(
    x for x in primitives_library.definitions if x['EDIF.identifier'] == 'OBUF')

# The example does not contain a needed primitive definition so we need to create it
# Create a new definition and places it in primitives_library
lut6_definition = primitives_library.create_definition()
# Sets the identifier of the primitive
lut6_definition['EDIF.identifier'] = "LUT6"
# Create the input ports for the new primitive
for ii in range(6):
    # Create a new port for the definition
    input_port = lut6_definition.create_port()
    # Sets the direction of the new port
    input_port.direction = sdn.IN
    # Create the pins that the new port will use
    input_port.create_pins(1)
    # Sets the identifier for the new port
    input_port['EDIF.identifier'] = 'I{}'.format(ii)
# Need to create the output port for the new primitive
# Create a new port for the definition
output_port = lut6_definition.create_port()
# Set the direction of the new port
output_port.direction = sdn.OUT
# Create the pins that the new port will use
output_port.create_pins(1)
# Set the identifier that the new port will use
output_port['EDIF.identifier'] = "O"

# Gets the definition that represents the top module
top_def = ir.top_instance.reference

# Create a new flip-flop instance within the top module
ff = top_def.create_child()
# Sets the definition reference for the new instance
ff.reference = fdce_definition
# Set the identifier for the new instance
ff['EDIF.identifier'] = 'out_reg_4_'
# Set the original identifier for the new instance (Being use to be consistence with example)
ff['EDIF.original_identifier'] = 'out_reg[4]'
properties = list()
# Create properties for the new instance
properties.append({'identifier': 'INIT', 'value': "1'b0"})
ff['EDIF.properties'] = properties

# Create a new LUT6 instance within the top module
lut6 = top_def.create_child()
# Set the identifier for the new instance
lut6['EDIF.identifier'] = 'out_4_lut6'
# Set the definition reference for the new instance
lut6.reference = lut6_definition
# Create properties for the new instance
properties = [{'identifier': 'INIT', 'value': "64'h7FFF8000FFFE0001"}]
lut6['EDIF.properties'] = properties

# Create a new OBUF instance within the top module
myOBUF = top_def.create_child()
# Set the definition reference for the new instance
myOBUF.reference = obuf_definition
# Set the identifier for the new instance
myOBUF['EDIF.identifier'] = 'out_OBUF_4__inst'
# Set the original identifier for the new instance (Being use to be consistence with example)
myOBUF['EDIF.original_identifier'] = 'out_OBUF[4]_inst'

# Create variables to hold cables within the design
inc_wire = None
out0 = None
out1 = None
out2 = None
out3 = None
clk = None
enable = None
rst = None

# Loop through each cable in the top module searching for specific cables
for cable in top_def.cables:
    if cable['EDIF.identifier'] == 'inc_dec_IBUF':
        inc_wire = cable.wires[0]
    # elif cable['EDIF.identifier'] == 'out_OBUF_0_':
    #     out0 = cable.wires[0]
    # elif cable['EDIF.identifier'] == 'out_OBUF_1_':
    #     out1 = cable.wires[0]
    # elif cable['EDIF.identifier'] == 'out_OBUF_2_':
    #     out2 = cable.wires[0]
    # elif cable['EDIF.identifier'] == 'out_OBUF_3_':
    #     out3 = cable.wires[0]
    elif cable['EDIF.identifier'] == 'out_OBUF':
        out0 = cable.wires[0]
        out1 = cable.wires[1]
        out2 = cable.wires[2]
        out3 = cable.wires[3]

    elif cable['EDIF.identifier'] == 'clk_IBUF_BUFG':
        clk = cable.wires[0]
    elif cable['EDIF.identifier'] == 'enable_IBUF':
        enable = cable.wires[0]
    elif cable['EDIF.identifier'] == 'rst_IBUF':
        rst = cable.wires[0]

# Connect exiting cables to the input port of the LUT6 instance
inc_wire.connect_pin(get_pin(lut6, 'I5'))
out0.connect_pin(get_pin(lut6, 'I0'))
out1.connect_pin(get_pin(lut6, 'I1'))
out2.connect_pin(get_pin(lut6, 'I2'))
out3.connect_pin(get_pin(lut6, 'I3'))

# Create a new cable for the new flip-flop output
out4_cable = top_def.create_cable()
# Set the identifier for the new cable
out4_cable['EDIF.identifier'] = 'out_OBUF_4_'
out4 = out4_cable.create_wire()
# Connect the new cable to remaining input port of the LUT6
out4.connect_pin(get_pin(lut6, 'I4'))
# Connect the new cable to the output of the flip-flop
out4.connect_pin(get_pin(ff, 'Q'))
# Connect the new cable to the new OUBF
out4.connect_pin(get_pin(myOBUF, 'I'))

# Create a new cable for the LUT6 output
lut_out_cable = top_def.create_cable()
# Set the original_identifier to match existing format of similar cables
lut_out_cable['EDIF.original_identifier'] = 'out[4]_i_1_n_0'
# Set the identifier to match the existing format of similar cable
lut_out_cable['EDIF.identifier'] = 'out_4__i_1_n_0'
lut_out = lut_out_cable.create_wire()
# Connect the new cable to the output of the LUT6
lut_out.connect_pin(get_pin(lut6, 'O'))
# Connect the new cable to the data port of the flip-flop
lut_out.connect_pin(get_pin(ff, 'D'))

# Connect the clk cable to the clk pin of the flip-flop
clk.connect_pin(get_pin(ff, 'C'))
# Connect enable cable to the clock enable pin of the flip-flop
enable.connect_pin(get_pin(ff, 'CE'))
# Connect the rst cable to the reset pin of the flip-flop
rst.connect_pin(get_pin(ff, 'CLR'))

# Find the output port of the top module
out_port = next(x for x in top_def.ports if x['EDIF.identifier'] == 'out')
# Create a another pin for the output
port_pin = out_port.create_pin()
# Rename the port to match number of pins
out_port['EDIF.original_identifier'] = 'out[4:0]'

# Create a new cable to drive the new output pin
out_cable = top_def.create_cable()
out_cable['EDIF.original_identifier'] = 'out[4]'
out_cable['EDIF.identifier'] = 'out_4_'
out = out_cable.create_wire()

# Connect the new cable to the output of the new OBUF
out.connect_pin(get_pin(myOBUF, 'O'))
# Preserve what wire out is
old_wire = out
# Loop through each pin in the output port
for pin in out_port.pins:
    # Get the wire that is connect to the pin
    temp = pin.wire
    # Check if there is a wire
    if temp is not None:
        # Disconnect the wire if connected
        temp.disconnect_pin(pin)
    # Connect the saved wire to the pin
    old_wire.connect_pin(pin)
    # Check if there was a wire
    if temp is not None:
        # Preserve what the wire was
        old_wire = temp

print()
print("The counter is now a five bit counter.")
