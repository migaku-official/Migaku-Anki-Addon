import json
import re
import random
import time
from collections import defaultdict
import asyncio

import aqt

from .migaku_http_handler import MigakuHTTPHandler
from .. import util

from . import srs_util
from .srs_util import handle_card, nt_migaku_lang


class SrsCheckHandler(MigakuHTTPHandler):
    def get(self):
        self.write(
            {
                "ok": aqt.mw.col is not None and self.connection.is_connected(),
                "version": "3",
            }
        )


class SrsImportInfoHandler(MigakuHTTPHandler):
    def get(self):
        col = aqt.mw.col
        if col is None:
            self.clear()
            self.set_status(503)
            self.finish("Collection not loaded")
            return

        decks = []

        # [[deckId, noteTypeId, cardTypeIdx]]
        raw_deck_card_types = col.db.all(
            """
            SELECT DISTINCT
                cards.did, notes.mid, cards.ord
            FROM
                cards
            LEFT OUTER JOIN
                notes
            ON
                cards.nid = notes.id
        """
        )

        deck_note_types = defaultdict(set)
        deck_card_ords = defaultdict(set)

        for deckId, noteTypeId, cardTypeOrd in raw_deck_card_types:
            deck_note_types[deckId].add(noteTypeId)
            deck_card_ords[(deckId, noteTypeId)].add(cardTypeOrd)

        for deck_info in col.decks.all_names_and_ids(
            skip_empty_default=True, include_filtered=False
        ):
            deck_id = deck_info.id
            deck_name = deck_info.name

            cids = col.decks.cids(deck_id, children=False)
            card_count = len(cids)

            card_types = []

            for note_type_id in deck_note_types[deck_id]:
                note_type = col.models.get(note_type_id)
                tmpls = note_type["tmpls"]
                fields = [f["name"] for f in note_type["flds"]]

                for card_ord in deck_card_ords[(deck_id, note_type_id)]:
                    for tmpl in tmpls:
                        if tmpl["ord"] != card_ord:
                            continue
                        is_migaku = not nt_migaku_lang(note_type) is None
                        card_types.append(
                            {
                                "id": f"{note_type_id}\u001f{card_ord}",
                                "name": note_type["name"] + " - " + tmpl["name"],
                                "fields": fields,
                                "isMigaku": is_migaku,
                            }
                        )
                        break

            decks.append(
                {
                    "id": deck_id,
                    "name": deck_name.replace("::", " ➜ "),
                    "cardCount": card_count,
                    "cardTypes": card_types,
                }
            )

        self.write({"decks": decks})


class SrsSampleCardHandler(MigakuHTTPHandler):
    last_cid = None

    SRC_RE = re.compile(r"src=\"(.*?)\"")
    URL1_RE = re.compile(r"url\(\"(.*?)\"\)")
    URL2_RE = re.compile(r"url\((.*?)\)")

    AUDIO_AV_REF_RE = re.compile(r"\[anki:play:a:(\d+)\]")

    AUDIO_HTML = """
        <style>
            .replay-button {
                text-decoration: none;
                display: inline-flex;
                vertical-align: middle;
                margin: 3px;
                cursor: pointer;
            }

            .replay-button svg {
                width: 40px;
                height: 40px;
            }

            .replay-button svg circle {
                fill: #fff;
                stroke: #414141;
            }

            .replay-button svg path {
                fill: #414141;
            }
        </style>
        <script>
            var __audioElem = document.createElement('audio');

            async function __playAudio(url) {
                await __audioElem.pause();
                __audioElem.src = url;
                await __audioElem.play();
            }
        </script>
    """

    AUDIO_AV_HTML = """
        <a class="replay-button soundLink" onclick="__playAudio('{}'); return false;">
            <svg class="playImage" viewBox="0 0 64 64" version="1.1">
                <circle cx="32" cy="32" r="29"></circle>
                <path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"></path>
            </svg>
        </a>
    """

    def fix_av(self, string, avTags):
        def repl(match):
            try:
                idx = int(match.group(1))
                avTag = avTags[idx]
            except (ValueError, IndexError):
                return match.group(0)

            url = aqt.mw.serverURL() + avTag.filename

            return self.AUDIO_AV_HTML.format(url)

        return self.AUDIO_AV_REF_RE.sub(repl, string)

    def fix_src(self, string):
        def repl_src(match):
            src = match.group(1)
            if not src.startswith("http"):
                src = aqt.mw.serverURL() + src
            return f'src="{src}"'

        def repl_url1(match):
            src = match.group(1)
            if not src.startswith("http"):
                src = aqt.mw.serverURL() + src
            return f'url("{src}")'

        def repl_url2(match):
            src = match.group(1)
            if not src.startswith("http"):
                src = aqt.mw.serverURL() + src
            return f"url({src})"

        string = self.SRC_RE.sub(repl_src, string)
        string = self.URL1_RE.sub(repl_url1, string)
        string = self.URL2_RE.sub(repl_url2, string)
        return string

    async def post(self):
        col = aqt.mw.col
        if col is None:
            self.clear()
            self.set_status(503)
            self.finish("Collection not loaded")
            return

        data = json.loads(self.request.body)

        deckId = int(data["deckId"])
        deck = aqt.mw.col.decks.get(deckId, default=False)
        deckName = deck["name"]

        parts = data["cardTypeId"].split("\u001f")
        noteTypeId = int(parts[0])
        cardTypeIdx = int(parts[1])

        noteType = aqt.mw.col.models.get(noteTypeId)
        noteTypeName = noteType["name"]

        cardIds = aqt.mw.col.find_cards(
            f'"note:{noteTypeName}" card:{cardTypeIdx+1} "deck:{deckName}"'
        )

        cardId = None
        frontHtml = ""
        backHtml = ""

        last_card = data.get("lastCard", False)

        if cardIds:
            if last_card and self.last_cid in cardIds:
                cardId = SrsSampleCardHandler.last_cid
            else:
                cardId = random.choice(cardIds)
                SrsSampleCardHandler.last_cid = cardId
            card = aqt.mw.col.get_card(cardId)

            frontHtml = (
                "<!DOCTYPE html><body>"
                + self.AUDIO_HTML
                + self.fix_av(self.fix_src(card.question()), card.question_av_tags())
                + "</body></html>"
            )
            backHtml = (
                "<!DOCTYPE html><body>"
                + self.AUDIO_HTML
                + self.fix_av(self.fix_src(card.answer()), card.answer_av_tags())
                + "</body></html>"
            )

        lang = data.get("lang")
        mappings = data.get("mappings")
        card_info = None

        if not mappings is None and cardId:
            card_info = await handle_card(
                cid=cardId,
                lang=lang,
                mappings=mappings,
                card_types=data.get("cardTypes", []),
                preview=True,
            )

        self.write(
            {
                "cardId": cardId,
                "frontHtml": frontHtml,
                "backHtml": backHtml,
                "cardInfo": card_info,
            }
        )


class SrsImportHandler(MigakuHTTPHandler):
    async def post(self):
        data = json.loads(self.request.body)

        # t = int(time.time())
        # json.dump(data, open(F'test_import_data_{t}.json', 'w'), indent=2)

        deck_id = int(data["deckId"])
        offset = int(data["offset"])
        limit = int(data["limit"])
        lang = data["lang"]
        mappings = data["mappings"]
        card_types = data["cardTypes"]
        user_token = data["userToken"]
        srs_today = data["srsToday"]
        is_free_trial = data.get("isFreeTrial", False)
        free_trial_remaining_cards = data.get("freeTrialRemainingCards", 999999999)
        debug = data.get("debug", False)

        card_ids = aqt.mw.col.findCards(f"did:{deck_id}")

        if is_free_trial:
            # If total cards are 50 or less, import them all
            if len(card_ids) <= 50:
                limit = min(len(card_ids), free_trial_remaining_cards)
                card_ids = card_ids[offset : offset + limit]
            else:
                # Initialize cards_by_type as an empty dictionary
                cards_by_type = {}

                for cid in card_ids:
                    card = aqt.mw.col.getCard(cid)
                    card_type_name = card.template()["name"]

                    # Update cards_by_type with the fetched card type name
                    if card_type_name not in cards_by_type:
                        cards_by_type[card_type_name] = []
                    cards_by_type[card_type_name].append(cid)

                total_cards = sum(len(cards) for cards in cards_by_type.values())
                total_slots = min(50, free_trial_remaining_cards)
                cards_to_import = {}

                # First, guarantee at least one slot for each card type
                for ctype in cards_by_type:
                    if len(cards_by_type[ctype]) > 0:
                        cards_to_import[ctype] = 1
                        total_slots -= 1

                # Distribute remaining slots among card types
                while total_slots > 0:
                    for ctype in sorted(
                        cards_to_import,
                        key=lambda k: len(cards_by_type[k]),
                        reverse=True,
                    ):
                        if cards_to_import[ctype] < len(cards_by_type[ctype]):
                            cards_to_import[ctype] += 1
                            total_slots -= 1
                            if total_slots == 0:
                                break

                # Display the number of cards to be imported for each type and the total cards for each type
                for ctype, cards in cards_by_type.items():
                    print(f"Total cards of type {ctype}: {len(cards)}")
                    print(f"Importing {cards_to_import[ctype]} cards of type {ctype}")

                # Fetch cards based on the calculated numbers
                new_card_ids = []
                for ctype, count in cards_to_import.items():
                    new_card_ids += cards_by_type[ctype][:count]

                card_ids = new_card_ids

        else:
            card_ids = card_ids[offset : offset + limit]

        srs_util.upload_data_size = 0
        media_gather = set()
        syntax_gather = set()

        # Gather media and syntax from cards
        gather_tasks = []
        for cid in card_ids:
            task = handle_card(
                cid=cid,
                lang=lang,
                mappings=mappings,
                card_types=card_types,
                user_token=user_token,
                srs_today=srs_today,
                preview=False,
                gather_media=media_gather,
                gather_syntax=syntax_gather,
            )
            gather_tasks.append(task)

        t0 = time.time()
        await asyncio.gather(*gather_tasks)
        t_gather = time.time() - t0

        # Build caches
        t0 = time.time()
        syntax_cache = await srs_util.build_syntax_cache(syntax_gather)
        t_syntax = time.time() - t0

        t0 = time.time()
        media_cache = await srs_util.build_media_cache(media_gather, user_token)
        t_media = time.time() - t0

        # Create actual card data
        tasks = []
        for cid in card_ids:
            task = handle_card(
                cid=cid,
                lang=lang,
                mappings=mappings,
                card_types=card_types,
                user_token=user_token,
                srs_today=srs_today,
                preview=False,
                syntax_cache=syntax_cache,
                media_cache=media_cache,
            )
            tasks.append(task)

        t0 = time.time()
        card_infos = await asyncio.gather(*tasks)
        card_infos = [ci for ci in card_infos if ci]
        t_cards = time.time() - t0

        # Get the deck name
        deck_name = aqt.mw.col.decks.get(deck_id, default=False)["name"]
        deck_name = deck_name.replace("::", " ➜ ")

        response = {
            "count": len(card_ids),
            "cards": card_infos,
            "deckName": deck_name,
        }

        if debug:
            response["tGather"] = t_gather
            response["tSyntax"] = t_syntax
            response["tMedia"] = t_media
            response["tCards"] = t_cards
            response["uploadSize"] = srs_util.upload_data_size

        self.write(response)
