class DbRouter:
    """
    A router to control all database operations on models in 
    different applications.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'timeline':
            return 'timeline_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'timeline':
            return 'timeline_db'
        return 'default'
    
"""
    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if both models are in the same database
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'users_app':
            return db == 'users_db'
        elif app_label == 'inventory_app':
            return db == 'inventory_db'
        return db == 'default'
"""


#TODO: From youtube:
"""
class DbRouter:
    def db_for_read(self, model, ** hints):
        if model ._ meta.app_label == 'core':
            return 'default'
        elif model ._ meta.app_label == 'courses':
            return 'course_db'
        return None

    def db_for_write(self, model, ** hints):
        if model ._ meta.app_label == 'core':
            return 'default'
        elif model ._ meta.app_label == 'courses':
            return 'course_db'
        return None
"""