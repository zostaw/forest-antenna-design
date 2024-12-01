import necpp
import random

def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())

def calc_yagi(freq, chromosome):

    segments = 21
    height = 10.2
    wire_thickness = 2.55e-4

    
    nec = necpp.nec_create()
    handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[0][2]/2, height, 0, chromosome[0][2]/2, height, 0, wire_thickness, 1, 1))

    if (len(chromosome) > 0) and chromosome[1][0]:
        handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[1][2]/2, height, -chromosome[1][1], chromosome[1][2]/2, height, -chromosome[1][1], wire_thickness, 1, 1))
    if (len(chromosome) > 1):
        for director in chromosome[2:]:
            if director[0]:
                handle_nec(necpp.nec_wire(nec, 1, segments, -director[2]/2, height, director[1], director[2]/2, height, director[1], wire_thickness, 1, 1))

    handle_nec(necpp.nec_geometry_complete(nec, 0))
    handle_nec(necpp.nec_fr_card(nec, 0, 1, freq, 0))
    handle_nec(necpp.nec_ex_card(nec, 0, 1, 11, 1, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)) 
    handle_nec(necpp.nec_rp_card(nec, 0, 360, 1000, 0, 0, 0, 0, 90.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 1, 1000, 0, 0, 0, 0, -90.0, 0.0, 0.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 91, 120, 0, 0, 0, 0, 0.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    result_index = 0
    
    z = complex(necpp.nec_impedance_real(nec,result_index), 
                necpp.nec_impedance_imag(nec,result_index))
    g = necpp.nec_gain_max(nec, 0)
    
    necpp.nec_delete(nec)

    return (z, g)


def random_chromosome(wire_len_limits, distance_step, max_distance_steps, wires):
    if not isinstance(wires, int):
        raise("wires must be a positive integer")
    if wires < 1:
        raise("Chromosome must have at least one wire (dipole), but has none.")
    existance = lambda a: (False if a<0.5 else True)
    return [(existance(random.uniform(0, 1)), distance_step*random.randint(0, max_distance_steps), random.uniform(wire_len_limits[0], wire_len_limits[1])) for _ in range(wires)]


"""
Gene: binary number
Chromosome: [dipole, reflector, director1, director2, ...] where each dipole/reflector/director is set of (existance, distance, length) - for dipole existance and distance are ignored

Rules:
1. if directors are too close to each other - the chromosome dies
"""


if __name__ == "__main__":
    freq = 433.0 # MHz
    c = 300 # Mm/s
    wave_length = c/freq
    dipole_length = 0.5*wave_length


    wire_len_limits = (0.005, 0.3) # [m]
    distance_step = 0.005 # [m]
    max_distance_steps = 200
    elements = 4

    # first_chromosome = [(True, 0, 1e-1), (False, 1e-2, 1e-1), (True, 1e-2, 1e-1), (False, 1e-2, 1e-1), (False, 1e-2, 1e-1), (False, 1e-2, 1e-1)]
    first_chromosome = random_chromosome(wire_len_limits, distance_step, max_distance_steps, elements)

    (z, g) = calc_yagi(freq, first_chromosome)

    print("Impedance \t(%6.1f,%+6.1fI) Ohms" % (z.real, z.imag))
    print(f"Gain \t {g} dBm")

