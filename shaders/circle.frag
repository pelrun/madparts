#version 120
varying vec2 pos;
void main() {
  float radius = 0.5;
  float dist = radius * radius - pos.x * pos.x - pos.y * pos.y;
  if (dist > 0)
    gl_FragColor = gl_Color;
}
