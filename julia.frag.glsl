#version 440

uniform vec2 C; // julia parameter
uniform float min_iter; // (int) skip trap on first iterations
// uniform float frame_count; // (int) frame counter
uniform vec2 trap_origin; // orbit trap centre
uniform float trap_zoom;
// uniform float trap_angle;
// uniform float bw_threshold;
// uniform float jitter_amount;

in vec2 Z0;
out vec4 f_color;

const vec3 igamma = vec3(2.2);
const vec3 gamma = 1.0 / igamma;
const float MAXITER = 150.;
const float BAILOUT2 = 256.0;
const float TAU = 6.283185307179586;
const float PHI = 1.618033988749895;
const vec4 ones = vec4(1.0);
const vec4 zeros = vec4(0.0);
const float tx = 10.5 / 768.;
const vec2 negx = vec2(-1.0, 1.0);

vec3 trap(vec2 Z, vec2 dZ) {
    vec2 X = (Z - vec2(trap_origin)) * .5 * trap_zoom;
    vec3 c = vec3(mix(0.0, 1.0, smoothstep(.2, .8, length(X))));
    return c;
}

void main (void) {
    vec2 Z = Z0;
    vec2 Z2 = Z * Z;
    float Zmag2 = Z2.x + Z2.y;
    vec2 dZ = vec2(1.0, 0);

    float i = 0.0;
    vec3 color = (i >= min_iter) ? trap(Z, dZ) : vec3(1.0);
    for (i = 1.; i < MAXITER; i++) {
        if (Zmag2 < BAILOUT2) {
            dZ = 2.0 * vec2(Z.x * dZ.x - Z.y * dZ.y, Z.x * dZ.y + Z.y * dZ.x);
            Z.y *= 2.0 * Z.x;
            Z.x = Z2.x - Z2.y;
            Z += C;
            Z2 = Z * Z;
            Zmag2 = Z2.x + Z2.y;
            vec3 cc = trap(Z, dZ);
            if (i >= min_iter) {
                color = color * cc;
                // color = min(color, cc);
                // color = mix(color * cc, min(color, cc), 0.25);
            }
        }
    }
    color *= step(BAILOUT2, Zmag2);
    //color.rg = Z0;
    f_color = vec4(color, 1.0);
}
