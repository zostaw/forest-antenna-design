model ( "yagi-uda" )
{

    real height, freq, wave_length, dipole_length, wire_thickness;
    real reflector_length, reflector_spacing;
    real director_length, director_spacing;
    real director2_length, director2_spacing;
    real director3_length, director3_spacing;
    real director4_length, director4_spacing;
    element dipole_wire;

    height = 10.2;
    freq = 433; // Mhz
    c = 300; // Mm/s
    wave_length = c/freq;
    wire_thickness = #14;
    
    // setup env
    setFrequency(freq) ;
    azimuthPlotForElevationAngle(0.0) ;
    elevationPlotForAzimuthAngle(0.0) ;
    freespace();
    //poorGround();
    
    // dipole
    dipole_length = 0.5*wave_length;
    dipole_wire = wire(0, -dipole_length/2, height, 0, dipole_length/2, height, wire_thickness, 20);
    voltageFeed(dipole_wire, 1.0, 0.0);
    
    // reflector
    reflector_length = 0.48*wave_length;
    reflector_spacing = -0.24*wave_length;
    wire(reflector_spacing, -reflector_length/2, height, reflector_spacing, reflector_length/2, height, wire_thickness, 20);
    
 
    
    // director
    director_length = 0.46*wave_length;
    director_spacing = 0.15*wave_length;
    wire(director_spacing, -director_length/2, height, director_spacing, director_length/2, height, wire_thickness, 20);
    
    // director 2
    director2_length = 0.35*wave_length;
    director2_spacing = 0.25*wave_length;
    wire(director2_spacing, -director2_length/2, height, director2_spacing, director2_length/2, height, wire_thickness, 20);
    
    // director 3
    director3_length = 0.45*wave_length;
    director3_spacing = 0.35*wave_length;
    wire(director3_spacing, -director3_length/2, height, director3_spacing, director3_length/2, height, wire_thickness, 20);
    
    // director 4
    director4_length = 0.46*wave_length;
    director4_spacing = 0.57*wave_length;
    wire(director4_spacing, -director4_length/2, height, director4_spacing, director4_length/2, height, wire_thickness, 20);
    

}