from .MigakuHTTPHandler import MigakuHTTPHandler
import re
import json
from anki.collection import Collection


def getNextBatchOfCards(self, start, incrementor):
    return self.db.all("SELECT c.ivl, n.flds, c.ord, n.mid FROM cards AS c INNER JOIN notes AS n ON c.nid = n.id WHERE c.type != 0 ORDER BY c.ivl LIMIT %s, %s;" % (start, incrementor))


Collection.getNextBatchOfCards = getNextBatchOfCards


class LearningStatusHandler(MigakuHTTPHandler):

    def get(self):
        self.finish("LearningStatusHandler")

    def post(self):
        if self.checkVersion():
            fetchModels = self.get_body_argument(
                "fetchModelsAndTemplates", default=False)
            if fetchModels is not False:
                self.finish(self.fetchModelsAndTemplates())
                return
            start = self.get_body_argument("start", default=False)
            if start is not False:
                incrementor = self.get_body_argument(
                    "incrementor", default=False)
                self.finish(self.getCards(start, incrementor))
                return
        self.finish("Invalid Request")

    def getFieldOrdinateDictionary(self, fieldEntries):
        fieldOrdinates = {}
        for field in fieldEntries:
            fieldOrdinates[field["name"]] = field["ord"]
        return fieldOrdinates

    def getFields(self, templateSide, fieldOrdinatesDict):
        pattern = r"{{([^#^\/][^}]*?)}}"
        matches = re.findall(pattern, templateSide)
        fields = self.getCleanedFieldArray(matches)
        fieldsOrdinates = self.getFieldOrdinates(fields, fieldOrdinatesDict)
        return fieldsOrdinates

    def getFieldOrdinates(self, fields, fieldOrdinates):
        ordinates = []
        for field in fields:
            if field in fieldOrdinates:
                ordinates.append(fieldOrdinates[field])
        return ordinates

    def getCleanedFieldArray(self, fields):
        noDupes = []
        for field in fields:
            fieldName = self.getCleanedFieldName(field).strip()
            if not fieldName in noDupes and fieldName not in ["FrontSide", "Tags", "Subdeck", "Type", "Deck", "Card"]:
                noDupes.append(fieldName)
        return noDupes

    def getCleanedFieldName(self, field):
        if ":" in field:
            split = field.split(":")
            return split[len(split) - 1]
        return field

    def fetchModelsAndTemplates(self):
        modelData = {}
        models = self.mw.col.models.all()
        for idx, model in enumerate(models):
            mid = str(model["id"])
            templates = model["tmpls"]
            templateArray = []
            fieldOrdinates = self.getFieldOrdinateDictionary(model["flds"])
            for template in templates:
                frontFields = self.getFields(template["qfmt"], fieldOrdinates)
                name = template["name"]
                backFields = self.getFields(template["afmt"], fieldOrdinates)

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

    def getCards(self, start, incrementor):
        cards = self.mw.col.getNextBatchOfCards(start, incrementor)
        bracketPattern = "\[[^]\n]*?\]"
        for card in cards:
            card[1] = re.sub(bracketPattern, "", card[1])
        return json.dumps(cards)
