from __future__ import division

import sys
import time
import math
import random
import os

from mygl import gl, glu, glut, Shader


class App(object):
    
    def __init__(self, argv):
    
        # Initialize GLUT and out render buffer.
        glut.init(argv)
        glut.initDisplayMode(glut.DOUBLE | glut.RGBA | glut.DEPTH | glut.MULTISAMPLE)
    
        # Initialize the window.
        self.width = 800
        self.height = 600
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
    
        # Turn on a bunch of OpenGL options.
        gl.enable(gl.CULL_FACE)
        gl.enable(gl.DEPTH_TEST)
        gl.enable(gl.COLOR_MATERIAL)
        gl.enable('blend')
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
        gl.enable('multisample')
        

        self.fbo = gl.genFramebuffers(1)
        gl.bindFramebuffer(gl.FRAMEBUFFER, self.fbo)

        self.render_texture = gl.genTextures(1)
        gl.bindTexture(gl.TEXTURE_2D, self.render_texture)
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, self.width, self.height, 0, gl.RGB, gl.UNSIGNED_BYTE, 0)

        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, self.render_texture, 0)


        gl.bindFramebuffer(gl.FRAMEBUFFER, 0)

        self.dilate = 0

        self.fixed = Shader('''
            void main(void) {
                gl_Position = ftransform();
            }
        ''', '''
            void main(void) {
                gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
            }
        ''')

        self.shader = Shader('''
            void main(void) {
                gl_Position = ftransform();
                gl_TexCoord[0] = gl_MultiTexCoord0;
            }
        ''', '''
            uniform sampler2D texture1;
            uniform float width, height;
            uniform float dilate;
            void main(void) {

                float dmin = -dilate;
                float dmax = dilate + 0.5;
                float dx = 1.0;

                vec4 texel = vec4(0.0, 0.0, 0.0, 1.0);
                for (float x = dmin; x < dmax; x+=dx) {
                    for (float y = dmin; y < dmax; y+=dx) {
                        texel = max(texel, texture2D(texture1, gl_TexCoord[0].st + vec2(x / width, y / height)));
                    }
                }

                gl_FragColor = texel * vec4(gl_FragCoord.x / width, gl_FragCoord.y / height, 0.0, 1.0);
            }
        ''')

        self.curves = [(
            random.random() * 10 + 1,
            random.random() * 2 * 3.14159,
            random.random(),
        ) for _ in xrange(10)]
        self.frame = 0

        # Attach some GLUT event callbacks.
        glut.reshapeFunc(self.reshape)
        glut.displayFunc(self.display)
        glut.keyboardFunc(self.keyboard)
        
        self.frame_rate = 24.0
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)
        
    
    def keyboard(self, key, mx, my):
        if key == '\x1b': # ESC
            exit(0)
        elif key == 'f':
            glut.fullScreen()
        elif key == 'a':
            self.dilate += 1
        elif key == 'z':
            self.dilate = max(0, self.dilate - 1)
        else:
            print 'unknown key %r at %s,%d' % (key, mx, my)
            
    def run(self):
        return glut.mainLoop()

    def reshape(self, width, height):
        """Called when the user reshapes the window."""
        self.width = width
        self.height = height
        
        gl.viewport(0, 0, width, height)
        gl.matrixMode(gl.PROJECTION)
        gl.loadIdentity()
        gl.ortho(0, width, 0, height, -100, 100)
        gl.matrixMode(gl.MODELVIEW)
        gl.loadIdentity()
        gl.translate(0.5, 0.5, 0)
        
    def timer(self, value):
        self.frame += 1
        glut.postRedisplay()
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)

    def display(self):
    
        gl.bindFramebuffer(gl.FRAMEBUFFER, self.fbo)

        # Wipe the window.
        gl.enable('depth_test')
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)

        gl.loadIdentity()
        
        gl.disable('texture_2d')
        self.fixed.use()
        gl.color(1, 1, 1, 1)

        for freq, offset, amp in self.curves:
            with gl.begin('line_strip'):
                for x in xrange(0, self.width + 1, 10):
                    gl.vertex(x, self.height * (0.5 + 0.5 * amp * math.sin(4 * self.frame / self.frame_rate + offset + x * freq / self.width)), 0)

        gl.bindFramebuffer(gl.FRAMEBUFFER, 0)
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.enable('texture_2d')
        gl.enable('depth_test')
        gl.color(1, 1, 1, 1)

        print 'I need to print so it doesnt explode.'
        self.shader.use()
        location = gl.getUniformLocation(self.shader._prog, "texture1")
        if location >= 0:
            gl.uniform1i(location, 0)
        location = gl.getUniformLocation(self.shader._prog, "width")
        if location >= 0:
            gl.uniform1f(location, float(self.width))
        location = gl.getUniformLocation(self.shader._prog, "height")
        if location >= 0:
            gl.uniform1f(location, float(self.height))
        location = gl.getUniformLocation(self.shader._prog, "dilate")
        if location >= 0:
            gl.uniform1f(location, float(self.dilate))

        with gl.begin('polygon'):
            gl.texCoord(0, 0)
            gl.vertex(0, 0)
            gl.texCoord(1, 0)
            gl.vertex(self.width, 0)
            gl.texCoord(1, 1)
            gl.vertex(self.width, self.height)
            gl.texCoord(0, 1)
            gl.vertex(0, self.height)

        glut.swapBuffers()

        
if __name__ == '__main__':
    app = App(sys.argv)
    exit(app.run())

    