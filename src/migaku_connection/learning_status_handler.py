from .migaku_http_handler import MigakuHTTPHandler
import re
import json
from anki.collection import Collection


import aqt


def collection_get_next_card_batch(collection: Collection, start, incrementor):
    return collection.db.all(F'''
        SELECT c.ivl, n.flds, c.ord, n.mid
        FROM cards AS c
        INNER JOIN notes AS n ON c.nid = n.id
        WHERE c.type != 0
        ORDER BY c.ivl
        LIMIT {start}, {incrementor};
    ''')


class LearningStatusHandler(MigakuHTTPHandler):

    def get(self):
        self.finish('LearningStatusHandler')

    def post(self):
        print('here we go')

        if self.checkVersion():
            fetch_models_templates = self.get_body_argument('fetchModelsAndTemplates', default=False)
            if fetch_models_templates is not False:
                self.finish(self.fetch_models_and_templates())
                return

            start = self.get_body_argument('start', default=None)
            if start is not None:
                incrementor = self.get_body_argument('incrementor', default=False)
                self.finish(self.get_cards(start, incrementor))
                return

        self.finish('Invalid Request')

    def get_field_ordinate_dictionary(self, field_entries):
        return { field['name']: field['ord'] for field in field_entries}

    def get_fields(self, templateSide, fieldOrdinatesDict):
        pattern = r'{{([^#^\/][^}]*?)}}'
        matches = re.findall(pattern, templateSide)
        fields = self.get_cleaned_field_array(matches)
        fieldsOrdinates = self.get_field_ordinates(fields, fieldOrdinatesDict)
        return fieldsOrdinates

    def get_field_ordinates(self, fields, fieldOrdinates):
        ordinates = []
        for field in fields:
            if field in fieldOrdinates:
                ordinates.append(fieldOrdinates[field])
        return ordinates

    def get_cleaned_field_array(self, fields):
        no_dupes = []
        for field in fields:
            field_name = self.get_cleaned_field_name(field).strip()
            if not field_name in no_dupes and field_name not in ['FrontSide', 'Tags', 'Subdeck', 'Type', 'Deck', 'Card']:
                no_dupes.append(field_name)
        return no_dupes

    def get_cleaned_field_name(self, field_name):
        idx = field_name.rfind(':')
        if idx >= 0:
            field_name = field_name[idx + 1:]
        return field_name.strip()

    def fetch_models_and_templates(self):
        model_data = {}
        models = aqt.mw.col.models.all()
        for model in models:
            mid = str(model['id'])
            templates = model['tmpls']
            template_array = []
            field_ordinates = self.get_field_ordinate_dictionary(model['flds'])
            for template in templates:
                front_fields = self.get_fields(template['qfmt'], field_ordinates)
                name = template['name']
                back_fields = self.get_fields(template['afmt'], field_ordinates)

                template_array.append({
                    'frontFields': front_fields,
                    'backFields': back_fields,
                    'name': name,
                })
            if mid not in model_data:
                model_data[mid] = {
                    'templates': template_array,
                    'fields': field_ordinates,
                    'name': model['name'],
                }
        return json.dumps(model_data)

    BRACKET_RE = re.compile('\\[[^]\n\u001F]*?\\]') # (U+001F): Unit Separator

    def get_cards(self, start, incrementor):
        cards = collection_get_next_card_batch(aqt.mw.col, start, incrementor)
        for card in cards:
            card[1] = self.BRACKET_RE.sub('', card[1])
        return json.dumps(cards)
