from sanerfbcal.view import RootView, FbCalendarView
import cherrypy
import os


# Map the routes
root = RootView()
root.b = FbCalendarView(FbCalendarView.CalendarType.BIRTHDAY)
root.u = FbCalendarView(FbCalendarView.CalendarType.UPCOMING_EVENT)

# Change the configuration
cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', '5000')), })
cherrypy.quickstart(root)
