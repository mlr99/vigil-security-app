"""Storage-side operations for ingested datasets (database rows + uploaded files)."""

import os

from models.db import db
from models.event_model import EventLog


class DatasetService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    # This was implemented for in-app testing convenience, but I don't see anything wrong with leaving it in.
    def clear_all(self):
        """Remove every ingested event and uploaded CSV, as if nothing was ever ingested.

        Returns the number of event records deleted. Rolls back and re-raises on failure.
        """
        try:
            deleted = db.session.query(EventLog).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        self._remove_uploaded_files()
        return deleted

    def _remove_uploaded_files(self):
        if not os.path.isdir(self.upload_folder):
            return
        for name in os.listdir(self.upload_folder):
            path = os.path.join(self.upload_folder, name)
            if os.path.isfile(path) and name.lower().endswith('.csv'):
                os.remove(path)