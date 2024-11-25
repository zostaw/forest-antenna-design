model ( "dipole" )
{

    real height, length, freq;
    element fed_wire;

    height = 10.2;
    freq = 433; // Mhz
    c = 300; // Mm/s
    length = c/freq/4;
    //wire(0, 0, height + length_source, 0, 0, height+length, #14, 20);
    fed_wire = wire(0, 0, height - length, 0, 0, height + length, #14, 200);
    voltageFeed(fed_wire, 1.0, 0.0);

    setFrequency(freq) ;
    azimuthPlotForElevationAngle(0.0) ;
    elevationPlotForAzimuthAngle(0.0) ;
    freespace();
    //poorGround();

}