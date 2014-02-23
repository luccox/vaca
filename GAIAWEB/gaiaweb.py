#!/usr/bin/python2
# -*- coding: utf-8 -*-


import cherrypy
import os


class GaiaWeb(object):

    def _htmlize(self, head='', header='', body=''):
        html = '''<!DOCTYPE html>
    <head>
        <title>.:: GAIA DATAVIEW ::.</title>
        <link rel='stylesheet' type='text/css' href='css/style.css'>
        %s
    </head>
    <body>
    <div id="container">
        <div id="header">
        %s
        </div>
        <div id="body">
            %s
        </div>
        <div id="footer">
            <a href='https://github.com/luccox/vaca' title='Fork me on Github!'>github</a>
        </div>
    </div>
    </body>
</html>
'''
        return html % (head, header, body)



    def index(self):
        b = '''<a href='/chart' title='Jump to chart'>
                   <IMG class='displayed' src='data/GAIADATAVIEW.png'>
               </a>'''
        html = self._htmlize(body=b)
        return html

    index.exposed = True


    def chart(self):
        # http://spaceforaname.com/galleryview/
        h = '''<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
               <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js"></script>
               <script type="text/javascript" src="js/jquery.timers-1.2.js"></script>
               <script type="text/javascript" src="js/jquery.easing.1.3.js"></script>
               <script type="text/javascript" src="js/jquery.galleryview-3.0-dev.js"></script>
               <link type="text/css" rel="stylesheet" href="css/jquery.galleryview-3.0-dev.css" />
               <script>
	$(function(){
		$('#myGallery').galleryView({
			transition_speed: 600,
			show_filmstrip: false,
			panel_animation: 'fade',
			show_infobar: false
		});
	});
</script>
'''
        charts = ''
        for img in sorted(os.listdir('/home/luccox/GAIA/KAMI/wally/')):
            charts += '''<li><img src="img/%s" alt="%s" />''' % (img, img)


        b = ''' <div id="centrazo">
                    <ul id="myGallery">
                        %s
                    </ul>
                </div>''' % charts

        html = self._htmlize(head=h, body=b)
        return html

    chart.exposed = True

    def default(self):
        cherrypy.response.status = 404
        return 'Page not Found!'

    default.exposed = True


if __name__ == '__main__':
    cherrypy.response.headers['Content-Type'] = 'image/png'
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 10801
    cherrypy.tree.mount(GaiaWeb(), '/', '/home/luccox/GAIA/GAIAWEB/gaiaweb.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
