from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.actions import action
from flask.ext import login
from flask_wtf import Form
from sleepypuppy import app, db
from sleepypuppy.admin.payload.models import Payload
from models import Capture

import os

class CaptureView(ModelView):
    """
    ModelView override of Flask Admin for Captures.
    """
    # CSRF protection
    form_base_class = Form
    # Check if user is autheticated
    def is_accessible(self):
        return login.current_user.is_authenticated()
    # Override displayed fields
    list_template = 'capture_list_template.html'
    # Restrict captures from being created or edited
    can_create = False
    can_edit = False
    # Column tweaks
    column_list = ('pub_date', 'payload', 'assessments', 'url', 'referrer', 'cookies', 'user_agent', 'dom', 'screenshot')
    column_sortable_list = ('pub_date', 'payload', 'assessments', 'url', 'referrer', 'cookies', 'user_agent', 'screenshot')
    hostname = app.config['HOSTNAME']
    # Make sure payload exists otherwise it's a zombie capture
    column_formatters = dict(payload=lambda v, c, m, p: str(m.payload) if m.payload != None else "Payload Not Found!",\
        assessments=lambda v, c, m, p: str(Payload.query.filter_by(id=m.payload).first().assessments if Payload.query.filter_by(id=m.payload).first() != None else "Not Found")
        )
    form_excluded_columns = ('captures')
    # Allow columns to be searched/sorted
    column_filters = ('payload_id', 'url')
    # Delete screenshots on mass delete
    def delete_screenshots(self,model):
        """
        Remove screenshot assocaited with Capture model
        """
        os.remove("uploads/" + str(model.screenshot) + ".png")
        os.remove("uploads/small_" + str(model.screenshot) + ".png")
    on_model_delete = delete_screenshots

    @action('delete', 'Delete', 'Are you sure you want to delete?')
    def action_delete(self, items):
        for record in items:
            try:
                os.remove("uploads/" + str(Capture.query.filter_by(id=record).first().screenshot) + ".png")
                os.remove("uploads/small_" + str(Capture.query.filter_by(id=record).first().screenshot) + ".png")
            except:
                pass
            page = Capture.query.get(record)
            db.session.delete(page)
            db.session.commit()

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(CaptureView, self).__init__(Capture, session, **kwargs)
