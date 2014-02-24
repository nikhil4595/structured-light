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
        glut.initDisplayMode(2048 |glut.DOUBLE | glut.RGBA | glut.DEPTH | glut.MULTISAMPLE)
        # glut.initDisplayMode(2048)
    
        # Initialize the window.
        self.width = 800
        self.height = 600
        glut.initWindowSize(self.width, self.height)
        glut.createWindow(argv[0])

        gl.clearColor(0, 0, 0, 1)
    
        # Turn on a bunch of OpenGL options.
        # gl.enable(gl.CULL_FACE)
        # gl.enable(gl.DEPTH_TEST)
        # gl.enable(gl.COLOR_MATERIAL)
        # gl.enable('blend')
        # gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
        # gl.enable('multisample')
        

        self.shader = Shader('''
            #version 330

            void main(void) {
                gl_Position = gl_Vertex;
                gl_TexCoord[0] = gl_MultiTexCoord0;
            }
        ''', '''
            #version 330

            uniform int bit_index;

            void main(void) {

                int x = int(floor(gl_FragCoord.x));
                int y = int(floor(gl_FragCoord.y));

                int code = (x * 2) ^ x;
                int bit = code & 1;

                gl_FragColor = vec4(0.0, 0.0, 0,0, 1.0);
                if (bit) {
                    gl_FragColor = vec4(1.0, 1.0, 1.0, 0.0);
                }
            }

        ''')

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
        
    def timer(self, value):
        self.frame += 1
        glut.postRedisplay()
        glut.timerFunc(int(1000 / self.frame_rate), self.timer, 0)

    def display(self):
    
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.enable('texture_2d')
        gl.enable('depth_test')
        gl.color(1, 1, 1, 1)

        self.shader.use()
        # self.shader.uniform1i('bit_index', 1)

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

    