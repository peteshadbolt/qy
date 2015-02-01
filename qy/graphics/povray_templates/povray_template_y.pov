#version 3.6; // 3.7
#default{ finish{ ambient 0.1 diffuse 0.9 phong 0.2}}
global_settings{assumed_gamma 1.0}

camera{orthographic  right 6.4*x*.8    up 4.8*y*.8  location <0,2,0> look_at <0,0,0> sky <0,0,1>}

light_source {<-2,5,-2> color rgb <1,1,1> shadowless}   

plane{<0,1,0>, -2 pigment{color rgb <1,1,1>} finish{ ambient 0.2 diffuse 0.9}}

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




