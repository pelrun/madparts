#version 120
varying vec2 pos;
uniform vec2 jydscale;
void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x *= jydscale.x;
  vert.y *= jydscale.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert;
  pos = vec2(gl_Vertex);
}
