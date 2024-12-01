# GPT-4o translation of CocoaNEC 2.0 to necpp

I'm saving it here, because that was pretty impressive work from GPT-4 and I want to save it for future.
 Essentially, I spent day trying to figure out how to install original NEC 2.0 or the CPP version on my mac, but without success. I couldn't compile it. I tried adjusting code here and there following compiler errors, but I'm pretty mediocre programmer, so no success. A reliable way to use it is via python library *necpp* which is basically binding for mentioned lib. I wanted to avoid it, because I really wanted to take it as an opportunity to learn program synthesis and maybe Rosette, but in the end I am going to use python.  
Soo, I read documentation and examples from necpp on how to write an equivalent code to what I've got in CocoaNEC and it wasn't that easy. Some arguments overlap, but there's a lot more stuff in original lib than CocoaNEC, especially power and radiation pattern are abstracted away in CocoaNEC. There is *Card Deck* in the program that I correctly identified as what NEC format is for the whole environment. So, first I tried to use it as reference, but I failed miserably. Then I spoke with GPT-4o and the results were brilliant, I only had to provide the documentations for every function, because at first it did exactly what I did, haha.  
So, here's the convo:

## My prompt

Help me translate this deck file into nec2cpp code:

``````
CM dipole 2024-12-1 21:24
CE ----------
GW   1  21  -0.17321  10.20000  0.000000  0.173210  10.20000  0.000000  0.005000
GE  0
FR  0    1    0    0  433.0000  0.000000
EX  0    1   11    1  1.000000  0.000000                                        
XQ
RP  0    1  360 1000  90.00000     0.000     0.000     1.000 5.000E+03
RP  0  360    1 1000   -90.000  0.000000     1.000     0.000 5.000E+03
RP  0   91  120 1001     0.000     0.000     2.000     3.000 5.000E+03
XQ
EN
``````

## GPT-4o code (final)

```
#include <nec2cpp.h>

int main() {
    nec_context nec;

    // Comment
    nec.comment("CM dipole 2024-12-1 21:24");

    // Wire structure
    nec.gw(1, 21, -0.17321, 10.20000, 0.00000, 0.173210, 10.20000, 0.00000, 0.005000);

    // Geometry end
    nec.ge(0);

    // Frequency range
    nec.fr_card(0, 1, 433.0000, 0.000000);

    // Excitation
    nec.ex_card(
        nec_context::EXCITATION_VOLTAGE, // Excitation type: Voltage source
        1,                              // Source tag number
        11,                             // Source segment number
        1,                              // Impedance/admittance flag
        1.000000,                       // Real part of voltage
        0.000000,                       // Imaginary part of voltage
        0.000000, 0.000000, 0.000000, 0.000000 // Unused parameters
    );

    // Radiation pattern #1: Full 3D sweep (theta: 0 to 360, phi: 0 to 360)
    nec.rp_card(
        0,            // Calculation mode: normal space-wave field
        360,          // Number of theta steps
        1000,         // Number of phi steps
        0,            // Output format: major/minor/total gain
        0,            // Normalization: no normalization
        0,            // Power gain
        0,            // No averaging
        90.0,         // Initial theta angle
        0.0,          // Initial phi angle
        1.0,          // Theta increment
        1.0,          // Phi increment
        5000.0,       // Radial distance
        0.0           // Gain normalization factor
    );

    // Radiation pattern #2: Single theta angle, full phi sweep
    nec.rp_card(
        0,            // Calculation mode: normal space-wave field
        1,            // Single theta angle
        1000,         // Number of phi steps
        0,            // Output format: major/minor/total gain
        0,            // Normalization: no normalization
        0,            // Power gain
        0,            // No averaging
        -90.0,        // Initial theta angle
        0.0,          // Initial phi angle
        0.0,          // Theta increment (irrelevant for single angle)
        1.0,          // Phi increment
        5000.0,       // Radial distance
        0.0           // Gain normalization factor
    );

    // Radiation pattern #3: Restricted region (theta: 0 to 90, phi: 0 to 120)
    nec.rp_card(
        0,            // Calculation mode: normal space-wave field
        91,           // Number of theta steps
        120,          // Number of phi steps
        0,            // Output format: major/minor/total gain
        0,            // Normalization: no normalization
        0,            // Power gain
        0,            // No averaging
        0.0,          // Initial theta angle
        0.0,          // Initial phi angle
        1.0,          // Theta increment
        1.0,          // Phi increment
        5000.0,       // Radial distance
        0.0           // Gain normalization factor
    );

    // End of input
    nec.en();

    return 0;
}
```

## Explanations from GPT-4o

**1st version**:  
Comment (CM): Translated to nec.comment().  
Geometry (GW): Translated to nec.gw() with wire tag, number of segments, start coordinates, end coordinates, and radius.  
Geometry end (GE): Translated to nec.ge().  
Frequency (FR): Translated to nec.fr() with relevant frequency parameters.  
Excitation (EX): Translated to nec.ex() specifying the excitation tag, segment, and voltage parameters.  
Radiation Patterns (RP): Translated to multiple nec.rp() calls based on the given deck.  
End (EN): Translated to nec.en().  
  
  
**1st correction**:  
Frequency Card (FR): Replaced the previous nec.fr() with nec.fr_card().  
in_ifrq = 0 (linear step).  
in_nfrq = 1 (single frequency).  
in_freq_mhz = 433.0000 (starting frequency in MHz).  
in_del_freq = 0.000000 (no increment).  
  
**2nd correction**:  
Excitation Card (ex_card):  
itmp1: Set to EXCITATION_VOLTAGE, which corresponds to type 0 for an applied voltage source.  
itmp2: Source tag number (1 in this case, matching the GW tag).  
itmp3: Source segment number (11 as specified).  
itmp4: Admittance/impedance flag (set to 1 to enable printing).  
tmp1: Real part of the voltage, set to 1.000000.  
tmp2: Imaginary part of the voltage, set to 0.000000.  
Remaining parameters (tmp3 to tmp6): Set to 0.000000, as they are unused in this specific excitation.  
  
**3rd correction**:  
calc_mode: Set to 0 for normal mode (free-space or ground-included wavefields).  
output_format: Set to 0 for major/minor/total gain.  
normalization: Set to 0 for no normalization.  
theta0, phi0, delta_theta, delta_phi: Specify the starting angles and increments for theta and phi sweeps.  
radial_distance: Set to 5000.0 meters for far-field calculations.  
gain_norm: Set to 0.0, meaning normalization to maximum gain if requested (not applicable here as normalization is off).  
