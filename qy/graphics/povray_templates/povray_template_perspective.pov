#version 3.6; // 3.7
#default{ finish{ ambient 0.1 diffuse 0.9 phong 0.2}}
global_settings{assumed_gamma 1.0}

camera{perspective location <-3,-1.5,2>*1 look_at <0,0,-.2> sky <0,0,1>}

//light_source {<-2,-2,5> color rgb <1,1,1> shadowless}   

light_source {
  0*x                 // light's position (translated below)
  color rgb 1.0       // light's color
  area_light
  <1, 0, 0> <0, 1, 0> // lights spread out across this distance (x * z)
  4, 4                // total number of lights in grid (4x*4z = 16 lights)
  adaptive 0          // 0,1,2,3...
  jitter              // adds random softening of light
  circular            // make the shape of the light circular
  orient              // orient light
  translate <-2, -2, 5>   // <x y z> position of light
}


plane{<0,0,1>, -2 pigment{color rgb <1,1,1>} finish{ ambient 0.9 diffuse 0.9}}

// verticals             
cylinder {<1,1,-1>  <1,1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,-1,-1>  <-1,-1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<1,-1,-1>  <1,-1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,1,-1>  <-1,1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}

// main diagonal
cylinder {<-1,-1,-1>  <1,1,1>  .005 pigment{color rgb <0,0,1>} no_shadow}

// horizontals
cylinder {<1,-1,1>  <1,1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,-1,1>  <-1,1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<1,-1,-1>  <1,1,-1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,-1,-1>  <-1,1,-1>  .005 pigment{color rgb <0,0,0>} no_shadow}

// others
cylinder {<-1,1,1>  <1,1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,-1,1>  <1,-1,1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,-1,-1>  <1,-1,-1>  .005 pigment{color rgb <0,0,0>} no_shadow}
cylinder {<-1,1,-1>  <1,1,-1>  .005 pigment{color rgb <0,0,0>} no_shadow}




