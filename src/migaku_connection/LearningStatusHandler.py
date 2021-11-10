from .MigakuHTTPHandler import MigakuHTTPHandler
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
        pattern = r"{{([^#^\/][^}]*?)}}"
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
        noDupes = []
        for field in fields:
            fieldName = self.get_cleaned_field_name(field).strip()
            if not fieldName in noDupes and fieldName not in ["FrontSide", "Tags", "Subdeck", "Type", "Deck", "Card"]:
                noDupes.append(fieldName)
        return noDupes

    def get_cleaned_field_name(self, field_name):
        idx = field_name.rfind(':')
        if idx >= 0:
            field_name = field_name[idx + 1:]
        return field_name.strip()

    def fetch_models_and_templates(self):
        modelData = {}
        models = aqt.mw.col.models.all()
        for idx, model in enumerate(models):
            mid = str(model["id"])
            templates = model["tmpls"]
            templateArray = []
            fieldOrdinates = self.get_field_ordinate_dictionary(model["flds"])
            for template in templates:
                frontFields = self.get_fields(template["qfmt"], fieldOrdinates)
                name = template["name"]
                backFields = self.get_fields(template["afmt"], fieldOrdinates)

                templateArray.append({
                    "frontFields": frontFields,
                    "backFields": backFields,
                    "name": name,
                })
            if mid not in modelData:
                modelData[mid] = {
                    "templates": templateArray,
                    "fields": fieldOrdinates,
                    "name": model["name"],
                }
        return json.dumps(modelData)

    BRACKET_RE = re.compile('\\[[^]\n\u001F]*?\\]') # (U+001F): Unit Separator

    def get_cards(self, start, incrementor):
        cards = collection_get_next_card_batch(aqt.mw.col, start, incrementor)
        for card in cards:
            card[1] = self.BRACKET_RE.sub('', card[1])
        return json.dumps(cards)
