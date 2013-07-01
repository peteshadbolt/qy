#version 3.6; // 3.7
#default{ finish{ ambient 0.0 diffuse 0.4 phong 0.3}}
global_settings{assumed_gamma 1}

// camera                                                   
#declare camsize= .007;
camera{ orthographic location  <20,20,15> right camsize*640*x up camsize*480*y look_at <1,1,0> sky <0,0,1>}
//light_source {<5,-10,35> color rgb 1.0 area_light <23, 0, 0> <0, 23, 0> 4, 4 adaptive 1 jitter orient fade_distance 100 fade_power 2}
light_source {<5,10,15> color rgb 1.0 area_light <13, 0, 0> <0, 13, 0> 4, 4 adaptive 1 jitter orient fade_distance 100 fade_power 2}

//light_source {<5,10,10> color rgb 1 fade_distance 100 fade_power 2}

                                    
// column
#declare bs=.05;                         
#declare column = box {<0, 0, 0> <1-bs, 1-bs, 1>}
            
////////////////////// GEOMETRY STARTS HERE               

                                                                      
// floor                                                                      
plane {z, -1.2 pigment{color rgb <1,1,1>} finish{ambient 1}}

// axes
#declare lt=.01;

cylinder { <0,0,-1> <0,0,1> lt pigment{color rgb <0,0,0>}}
cylinder { <0,2,-1> <0,2,1> lt pigment{color rgb <0,0,0>}}
cylinder { <2,0,-1> <2,0,1> lt pigment{color rgb <0,0,0>}}
cylinder { <2,2,-1> <2,2,1> lt pigment{color rgb <0,0,0>}}

cylinder { <0,0,-1> <0,2,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <0,0,-1> <2,0,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <0,2,-1> <2,2,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <2,0,-1> <2,2,-1> lt pigment{color rgb <0,0,0>}}

cylinder { <0,0,1> <0,2,1> lt pigment{color rgb <0,0,0>}}
cylinder { <0,0,1> <2,0,1> lt pigment{color rgb <0,0,0>}}
cylinder { <0,2,1> <2,2,1> lt pigment{color rgb <0,0,0>}}
cylinder { <2,0,1> <2,2,1> lt pigment{color rgb <0,0,0>}}

cylinder { <.5,0,-1> <.5,2,-1> lt pigment{color rgb .8}}
cylinder { <1.5,0,-1> <1.5,2,-1> lt pigment{color rgb .8}}
cylinder { <0,.5,-1> <2,.5,-1> lt pigment{color rgb .8}}
cylinder { <0,1.5,-1> <2,1.5,-1> lt pigment{color rgb .8}}


cylinder { <2,.5,-1> <2.2,.5,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <2,1.5,-1> <2.2,1.5,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <.5,2,-1> <.5,2.2,-1> lt pigment{color rgb <0,0,0>}}
cylinder { <1.5,2,-1> <1.5,2.2,-1> lt pigment{color rgb <0,0,0>}}