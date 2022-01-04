import json
import aqt
from .migaku_http_handler import MigakuHTTPHandler



class ProfileDataProvider(MigakuHTTPHandler):


    def get(self):
        self.finish('LearningStatusHandler')


    def post(self):
        if self.check_version():

            if not self.is_ready():
                self.set_status(409)
                self.finish('Invalid Request')
                return


            fetch_data = self.get_body_argument('fetchProfileData', default=False)
            if fetch_data:
                profile_data = self.compose_profile_data()
                profile_data_json = json.dumps(profile_data)
                self.finish(profile_data_json)
                return

        self.finish('Invalid Request')


    def compose_profile_data(self):
        profile_data = {}
        profile_data['decks'] =  self.compose_deck_data()
        profile_data['noteTypes'] = self.compose_note_type_data()
        return profile_data


    def compose_deck_data(self):
        return [
            {
                'id': deck['id'],
                'name': deck['name'],
            }
            for deck in aqt.mw.col.decks.all()
        ]


    def compose_note_type_data(self):
        note_type_data = []
        note_types = aqt.mw.col.models.all()

        handled_ids = set()

        for note_type in note_types:
            note_type_id = str(note_type["id"])

            if note_type_id not in handled_ids:
                handled_ids.add(note_type_id)

                field_data = [
                    {
                        'name': field['name'],
                        'ordinal': field['ord'],
                    }
                    for field in note_type['flds']
                ]

                is_cloze = note_type['type'] == 1

                note_type_data.append({
                    'id': note_type_id,
                    'name': note_type['name'],
                    'fields': field_data,
                    'cloze':  is_cloze,
                })

        return note_type_data


    def is_ready(self):
        return not aqt.mw.col is None
