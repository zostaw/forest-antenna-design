import necpp

def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())

def calc_yagi(freq, dipole_length):

    segments = 21
    height = 10.2
    wire_thickness = 2.55e-4

    
    nec = necpp.nec_create()
    handle_nec(necpp.nec_wire(nec, 1, segments, -dipole_length/2, height, 0, dipole_length/2, height, 0, wire_thickness, 1, 1))
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




if __name__ == "__main__":
    freq = 433.0 # MHz
    c = 300 # Mm/s
    wave_length = c/freq
    dipole_length = 0.5*wave_length

    (z, g) = calc_yagi(freq, dipole_length)

    print("Impedance \t(%6.1f,%+6.1fI) Ohms" % (z.real, z.imag))
    print(f"Gain \t {g} dBm")

