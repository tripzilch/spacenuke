#version 440

uniform vec2 Zextent[4];
in vec2 in_vert;
out vec2 Z0;

void main()
{
	gl_Position = vec4(in_vert, 0.0, 1.0);
    Z0 = Zextent[gl_VertexID];
}
