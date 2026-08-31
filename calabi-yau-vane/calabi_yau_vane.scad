// Calabi–Yau-inspired weather vane + geomagnetic compass instrument.
// Concept CAD, millimetres. Not a perpetual-motion machine.
// The inner cage floats only when externally supplied air supports it.
$fn = 24;

shell_radius = 62;
ball_radius = 3.2;
tube_outer = 2.4;
tube_inner = 1.35;

function cage_point(t, phase=0) =
    let(a=t+phase, r=33+8*cos(5*a))
    [r*cos(a), .68*r*sin(a), 9*sin(3*a)+4*sin(8*a+phase)];

module hollow_segment(a,b,ro=tube_outer,ri=tube_inner) {
    difference() {
        hull(){ translate(a) sphere(ro); translate(b) sphere(ro); }
        hull(){ translate(a) sphere(ri); translate(b) sphere(ri); }
    }
}

module projected_cage() {
    for (phase=[0,120,240])
        for (i=[0:4:356])
            hollow_segment(cage_point(i,phase),cage_point(i+4,phase));
}

module bearing_shell() {
    // Latitudinal rings of geomagnetically responsive steel balls.
    for (lat=[-60,-30,0,30,60])
        let(z=shell_radius*sin(lat), rr=shell_radius*cos(lat), n=max(8,round(24*cos(lat))))
        for (i=[0:n-1])
            rotate([0,0,360*i/n+(lat==0?7.5:0)])
                translate([rr,0,z]) sphere(ball_radius);
}

module compass() {
    color("gold") rotate_extrude() translate([43,0]) circle(1.3);
    color("crimson") translate([0,14,-1]) cube([2.2,48,2],center=true);
    color("white") translate([0,-14,-1]) cube([2.2,20,2],center=true);
    translate([0,47,0]) linear_extrude(1) text("N",size=7,halign="center");
}

module weather_vane() {
    color("silver") cylinder(h=96,r=1.8,center=true);
    translate([0,0,49]) {
        color("orange") rotate([90,0,0]) cylinder(h=72,r=1.5,center=true);
        color("orange") translate([0,-39,0]) rotate([90,0,0]) cylinder(h=10,r1=0,r2=7);
        color("cyan") translate([0,32,0]) rotate([90,0,0]) linear_extrude(2)
            polygon([[0,-12],[0,12],[18,0]]);
    }
}

module air_bearing() {
    // The honest support mechanism: an external air supply enters this plenum.
    color([.2,.7,1,.35]) difference(){ sphere(49); sphere(48.3); }
    color("deepskyblue") translate([0,0,-58]) cylinder(h=16,r=2.5);
}

module air_microchannels() {
    // Paired inward/outward air channels drive the weather response.
    for (a=[0:45:315]) {
        rotate([0,0,a]) hollow_segment([18,0,-8],[47,0,-18],1.15,.55);
        rotate([0,0,a+22.5]) hollow_segment([16,0,8],[47,0,18],1.15,.55);
        rotate([0,0,a]) translate([48,0,-18]) sphere(1.8);
        rotate([0,0,a+22.5]) translate([48,0,18]) sphere(1.8);
    }
}

module dark_matter_hypothesis_fiducials() {
    // Engraved reference tracks for a literal dark-matter hypothesis test.
    // These are measurement/visualization marks, not pipes that contain DM.
    // H0: no device-correlated residual beyond the background model.
    // H1 (two-sided): a nonzero residual of either sign survives controls.
    for (a=[0:30:330])
        rotate([0,0,a])
            color([.45,.25,.8])
                translate([shell_radius+1.2,0,0]) sphere(.65);
}

color([.3,.55,.8]) projected_cage();
color([.08,.10,.16]) air_microchannels();
dark_matter_hypothesis_fiducials();
air_bearing();
color([.7,.75,.8]) bearing_shell();
compass();
weather_vane();
