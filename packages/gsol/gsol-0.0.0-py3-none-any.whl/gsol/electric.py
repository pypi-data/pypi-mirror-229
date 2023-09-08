import math

def awg_to_number(awg):
    """Convert AWG sizes like '1/0', '2/0' to -1, -2, etc."""
    if isinstance(awg, str) and "/" in awg:
        return -int(awg.split("/")[0])
    return int(awg)

def awg_diameter(awg):
    n = awg_to_number(awg)
    return 0.005 * (92 ** ((36 - n) / 39))

def cross_sectional_area(awg):
    d = awg_diameter(awg)
    return math.pi * (d / 2) ** 2
    

def get_resistivity(material, temperature=70):
    """Return resistivity based on material and operating temperature."""
    # Given resistivity at reference temperature and temperature coefficients
    RESISTIVITY_COPPER_20C = 1.724e-8
    ALPHA_COPPER = 4.29e-3
    RESISTIVITY_ALUMINUM_20C = 2.65e-8
    ALPHA_ALUMINUM = 3.8e-3
    T_REF = 20  # Reference temperature in Celsius
    
    if material == "copper" or material == "cu":
        return RESISTIVITY_COPPER_20C * (1 + ALPHA_COPPER * (temperature - T_REF))
    elif material == "aluminum" or material == "al":
        return RESISTIVITY_ALUMINUM_20C * (1 + ALPHA_ALUMINUM * (temperature - T_REF))
    else:
        raise ValueError("Invalid material. Choose either 'copper' or 'aluminum'.")



def get_derating_factor(conduit):
    """Return derating factor based on conduit material."""
    if conduit.lower() == "pvc":
        return 1
    elif conduit.lower() == "aluminum" or conduit.lower() == "al":
        return 0.8
    elif conduit.lower() == "steel" or conduit.lower() == "s":
        return 0.7
    else:
        raise ValueError("Invalid conduit. Choose 'PVC', 'aluminum', or 'steel'.")

def voltage_drop(awg, material, conduit, current, phase, length, supply=None, temperature=75):
    resistivity = get_resistivity(material, temperature)
    A = cross_sectional_area(awg) * 0.00064516  # Convert square inches to square meters
    R = resistivity / A
    derating_factor = get_derating_factor(conduit)
    
    if phase == 1:
        drop = (2 * current * length * R * derating_factor) / 1000
    elif phase == 3:
        drop = (math.sqrt(3) * current * length * R * derating_factor) / 1000
    else:
        raise ValueError("Invalid phase. Choose either 1 or 3.")
    
    if supply:
        percentage_drop = (drop / supply) * 100
        return percentage_drop * 100
    else:
        return drop

EMT_INCHES = [0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4]

def conduit_size(awg, num_of_wires, unit="inch", tubing="EMT"):
    """Calculate the conduit size required based on AWG size and number of wires."""
    wire_area_total = cross_sectional_area(awg) * num_of_wires
    if num_of_wires > 2:
        conduit_area_required = wire_area_total / 0.40 
    else:
        conduit_area_required = wire_area_total / 0.53
    conduit_diameter = math.sqrt(conduit_area_required / math.pi) * 2
    if unit.lower() == "mm":
        conduit_diameter *= 25.4
    if tubing.lower() == "emt":
        conduit_diameter = min(size for size in EMT_INCHES if size >= conduit_diameter)
    return conduit_diameter
