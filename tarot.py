#!/usr/bin/env python3
"""Tarot (Timex, 1983) for the TS1000 / ZX81, ported to Python.

The original tape held two BASIC programs: CARDS, which shows the meaning of
every card, and READING, which lays out an 11-card spread for your question.
This port draws both on an emulated 32x22 ZX81 screen and uses the original
text and block graphics, decoded from cards.p and reading.p.

Usage:
    python3 tarot.py            # menu
    python3 tarot.py cards      # browse the cards
    python3 tarot.py reading    # get a reading
    python3 tarot.py gallery    # print every card's art in order
"""

import os
import random
import sys
import time
from dataclasses import dataclass


@dataclass
class Suit:
    name: str
    letter: str
    header: str
    intro: str
    art: list
    number_row: int
    meanings: list


@dataclass
class Major:
    title: str
    intro: str
    art: list
    meaning: str


# --- Data extracted verbatim from cards.p and reading.p ---
# {...} marks inverse-video characters.

SUITS = [
    Suit(
        name='WANDS',
        letter='W',
        header='WANDS INDICATE-',
        intro='ENTERPRISE, NEW IDEAS,  ▛▀▀▀▀▀▜ ENERGY, PRAISE, GROWTH  ▌   ▜ ▐ AND LIFES RENEWAL...    ▌   ▐ ▐',
        art=[
            '▌   ▐ ▐',
            '▌   ▐ ▐',
            '▌OF ▐ ▐',
            '▌THE▝ ▐',
            '▌WANDS▐',
            '▙▄▄▄▄▄▟',
        ],
        number_row=5,
        meanings=[
            'A BEGINNING, NEW ENTERPRISE',
            'DOMINION, RICHES, GOOD FORTUNE',
            'COMMERCE, BUSINESS PARTNERSHIP',
            'ROMANCE, PROSPERITY, REFUGE',
            'STRIFE, STRUGGLING TO SUCCEED',
            'TRIUMPHANT NEWS, ADVANCEMENT',
            'STIFF COMPETITION, OPPOSITION',
            'LOVE PANGS, HASTE, MOVEMENT',
            'PREPAREDNESS, RESERVE STRENGTH',
            'HEAVY BURDEN, PROBLEMS SOLVED',
            'BRINGS GOOD TIDINGS; A CHILD',
            'A RIVAL; NEW ADDRESS, ABSENCE',
            'MAGNETIC WOMAN; ENTERPRISING',
            'FAMILY MAN; GOOD MARRIAGE',
        ],
    ),
    Suit(
        name='CUPS',
        letter='C',
        header='CUPS INDICATE-',
        intro='EMOTIONS, HAPPINESS,    ▛▀▀▀▀▀▜ LOVE, KNOWLEDGE, BEAUTY ▌ ▐█▌ ▐ AND THE GOOD LIFE...    ▌ ▐█▌ ▐',
        art=[
            '▌  █  ▐',
            '▌ ▝▀▘ ▐',
            '▌     ▐',
            '▌OF   ▐',
            '▌CUPS ▐',
            '▙▄▄▄▄▄▟',
        ],
        number_row=6,
        meanings=[
            'ABUNDANCE, LOVE, SPIRITUALITY',
            'LOVE AFFAIR, UNION, HARMONY',
            'ABUNDANCE, VICTORY, HEALING',
            'CONTEMPLATION, RE-EVALUATION',
            'REGRET, MARITAL BITTERNESS',
            'CHILDHOOD MEMORIES, RENEWAL',
            'UNFOCUSED IDEAS, GREAT DREAMS',
            'ABANDONED PROJECT, LOVELORN',
            'SATISFACTION, ROBUST HEALTH',
            'HAPPY FAMILY LIFE, SUCCESS',
            'CONSIDERATE YOUTH; NEW METHOD',
            'ROMANTIC MAN; AN INVITATION',
            'BELOVED WOMAN; HAPPY MARRIAGE',
            'FRIENDLY BACHELOR; GENEROSITY',
        ],
    ),
    Suit(
        name='SWORDS',
        letter='S',
        header='SWORDS INDICATE-',
        intro='AGGRESSION, AMBITION,   ▛▀▀▀▀▀▜ COURAGE, MISFORTUNE,    ▌   ▐ ▐ STRIFE, DESTRUCTION...  ▌   ▐ ▐',
        art=[
            '▌   ▐ ▐',
            '▌   ▐ ▐',
            '▌OF ▜▘▐',
            '▌THE▝ ▐',
            '▌SWORD▐',
            '▙▄▄▄▄▄▟',
        ],
        number_row=5,
        meanings=[
            'GREAT FORCE, POWER, CONQUEST',
            'STALEMATE, A FAMILY TRUCE',
            'DELAY, SORROW, LOVE LOST',
            'RETREAT, CONVALESCENCE',
            'PHYSICAL CONQUEST, CONFLICT',
            'TRIUMPH, REPRESENTATION',
            'PARTIAL SUCCESS, UNCERTAINTY',
            'UNCERTAINTY, BONDAGE, CRISIS',
            'MISERY, DEATH OF A LOVED ONE',
            'MISFORTUNE, END OF DELUSIONS',
            'VIGILANT YOUTH; WARY, ALERT',
            'DOMINEERING MAN; SKILLFUL',
            'QUICK-WITTED WOMAN; SADNESS',
            'AUTHORITATIVE MAN; WISDOM',
        ],
    ),
    Suit(
        name='PENTACLES',
        letter='P',
        header='PENTACLES INDICATE-',
        intro='MONEY, INTEREST, TRADE, ▛▀▀▀▀▀▜ MATERIALISM, INDUSTRY   ▌  ▟▖ ▐ AND THE MAGICAL ARTS... ▌ ▜██▘▐',
        art=[
            '▌ ▗▀▚ ▐',
            '▌     ▐',
            '▌OF   ▐',
            '▌PENT-▐',
            '▌ACLES▐',
            '▙▄▄▄▄▄▟',
        ],
        number_row=5,
        meanings=[
            'ECSTASY, WEALTH, PROSPERITY',
            'HARMONIOUS CHANGE, DIPLOMACY',
            'ARTFUL MASTER, CONSTRUCTION',
            'POSSESSIVE, MISERLY, SELFISH',
            'DESTITUTION, LOVE GONE ASTRAY',
            'PHILANTHROPY, SHARED WEALTH',
            'GROWTH, ENDEAVOR, A SOULMATE',
            'APPRENTICESHIP, EMPLOYMENT',
            'ACCOMPLISHMENT, WELL-BEING',
            'FAMILY LINEAGE, INHERITANCE',
            'DILIGENT YOUTH; SCHOLARSHIP',
            'METHODICAL MAN; PATIENCE',
            'INTELLIGENT WOMAN; GENEROSITY',
            'MAN OF CHARACTER; RELIABILITY',
        ],
    ),
]

MAJOR = [
    Major(
        title='0-THE FOOL',
        intro='STEPS FEARLESSLY OFF A  ▛▀▀▀▀▀▜ LEDGE. HE ALONE CARRIES ▌ */* ▐ THE WAND OF COSMIC WILL ▌ /{"}  ▐ AND SUPERCONSCIOUSNESS. ▌ ▙█▜ ▐',
        art=[
            '▌  █▄ ▐',
            '▌ ▗▌▝ ▐',
            '▌ ▔▒▒▒▐',
            '▌  ▒▒▒▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='AN IMPORTANT CHOICE IN LIFE',
    ),
    Major(
        title='1-THE MAGICIAN',
        intro='STANDS ON HIS PLATFORM  ▛▀▀▀▀▀▜ SURROUNDED BY MAGICAL   ▌ <=> ▐ COSMIC SYMBOLS.         ▌ ▖{"}  ▐',
        art=[
            '▌+▀{?}▜/▐',
            '▌  {*}  ▐',
            '▌ ▗█▖ ▐',
            '▌ ▓▓▓ ▐',
            '▌ ▓▓▓ ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='MASTERY, WISDOM, CREATIVITY',
    ),
    Major(
        title='2-THE HIGH PRIESTESS',
        intro='STANDS BETWEEN THE      ▛▀▀▀▀▀▜ PILLARS OF POSITIVE AND ▌-▗▄▖+▐ NEGATIVE LIFE FORCES.   ▌█▝{"}▘▒▐',
        art=[
            '▌█▐{*}▌▒▐',
            '▌█▝█▘▒▐',
            '▌█ █ ▒▐',
            '▌█▗█▖▒▐',
            '▌█>=<▒▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='HIDDEN INFLUENCES, DUALITY',
    ),
    Major(
        title='3-THE EMPRESS',
        intro='RESTS ON HER THRONE,    ▛▀▀▀▀▀▜ CROWNED BY STARS; SHE   ▌ *   ▐ RADIATES LIFE ENERGY.   ▌*▄*  ▐',
        art=[
            '▌▝{"}▘ 0▐',
            '▌▐{+}▙/ ▐',
            '▌▐▄▄█ ▐',
            '▌▐ ▐▐▖▐',
            '▌{OOOOO}▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='MARRIAGE, WEALTH, FERTILITY',
    ),
    Major(
        title='4-THE EMPEROR',
        intro='COMMANDINGLY STANDS     ▛▀▀▀▀▀▜ BETWEEN THE RAMS HEAD   ▌ *▄* ▐ SYMBOLS OF MARS; LORD   ▌ ▂{"}▂ ▐ OF THOUGHT AND REASON.  ▌▜▐{+}▌/▐',
        art=[
            '▌▐▀▓▀ ▐',
            '▌▚ ▓ ▞▐',
            '▌{"}▗█▖{"}▐',
            '▌▄▄▄▄▄▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='POWER, INTELLECT OVER PASSION',
    ),
    Major(
        title='5-THE HIEROPHANT',
        intro='STANDS BEFORE TWO NEW   ▛▀▀▀▀▀▜ INITIATES, THE RULING   ▌* {+}▗▙▐ POWER OF CEREMONY.      ▌▐({"})▌▐',
        art=[
            '▌▝▀█▜▌▐',
            '▌ ▗▄▖▌▐',
            '▌ ▐█▌▘▐',
            '▌+▀ ▀+▐',
            '▌▙{"}▄{"}▟▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='RITUAL, CONFORMITY, CONVENTION',
    ),
    Major(
        title='6-THE LOVERS',
        intro='STAND TOGETHER AMONG    ▛▀▀▀▀▀▜ THE TREES OF UNITY AND  ▌▞▄▚▄▞▐ DUALITY; THE SERPENT    ▌ {"}▝{"}▘▐ AND THE APPLE NEARBY.   ▌▐██{W}▌▐',
        art=[
            '▌▝█▀█▘▐',
            '▌ █ █ ▐',
            '▌▝▀▘▀(▐',
            '▌▄▛▙{"}O▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='SACRED OR PROFANE LOVE, CHOICE',
    ),
    Major(
        title='7-THE CHARIOT',
        intro='THE SPHINXES OF MERCY   ▛▀▀▀▀▀▜ AND JUSTICE CAN TEAR    ▌  *  ▐ THE CHARIOTEER IN TWO   ▌ ({"}) ▐ IF HIS RESOLVE WEAKENS. ▌▖▟{+}▙▗▐',
        art=[
            '▌▙▓▒▓▟▐',
            '▌▌▄▔▄▐▐',
            '▌▝{"}▀"▘▐',
            '▌▗█▄█▖▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='CONQUEST, TRIUMPH, GREATNESS',
    ),
    Major(
        title='8-STRENGTH',
        intro='A WOMAN OF MAGIC CLOSES ▛▀▀▀▀▀▜ THE MOUTH OF A LION;    ▌*▗▄▖*▐ COSMIC FORCES OFFER NO  ▌*▝{"}▘*▐ RESISTANCE TO HER FEAT. ▌*▛{W}▜*▐',
        art=[
            '▌ ▀{-}▝ ▐',
            '▌ ▚██▛▐',
            '▌  ▟▗▌▐',
            '▌▄▄▄▄▄▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='TRIUMPH OF LOVE, ENERGY, POWER',
    ),
    Major(
        title='9-THE HERMIT',
        intro='A LONE FIGURE ATOP A    ▛▀▀▀▀▀▜ MOUNTAIN LIGHTS THE WAY ▌.▗▄▖.▐ TO THE UNION OF COSMIC  ▌▄▝{"}▘▛▐ WILL AND CONSCIOUSNESS. ▌▒▟█▙▌▐',
        art=[
            '▌▀▐█▌▌▐',
            '▌.▐█▌▌▐',
            '▌ ▗█▖▌▐',
            '▌▂▒▒▒▂▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='WISDOM, PRUDENCE, GUIDANCE',
    ),
    Major(
        title='10-WHEEL OF FORTUNE',
        intro='EMBLAZONED WITH MAGICAL ▛▀▀▀▀▀▜ SYMBOLS, TURNS FOREVER  ▌▞   ▚▐ IN UNCHANGING REALITY.  ▌▗▟▀▙▖▐',
        art=[
            '▌▟>?*▙▐',
            '▌▌£+=▐▐',
            '▌▜/0<▛▐',
            '▌▝▜▄▛▘▐',
            '▌▚   ▞▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='GOOD FORTUNE, TURN OF LUCK',
    ),
    Major(
        title='11-JUSTICE',
        intro='CARRIES THE SCALES OF   ▛▀▀▀▀▀▜ JUSTICE AND THE DOUBLE- ▌▐▗{=}▖ ▐ EDGED SWORD OF THE LAW. ▌▐▝{"}▘ ▐',
        art=[
            '▌▟▟{W}▙ ▐',
            '▌▝▜▀▓▂▐',
            '▌ ▐{A}▌A▐',
            '▌ ▟▔▙▔▐',
            '▌▓▓▓▓▓▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='BALANCED PERSONALITY, EQUALITY',
    ),
    Major(
        title='12-THE HANGED MAN',
        intro='IN A DEEP TRANCE, AND   ▛▀▀▀▀▀▜ SUSPENDED FROM A LIVING ▌▂▂▂▂▂▐ GALLOWS BY ONE LEG; AN  ▌ ▝█▗ ▐ AURA SURROUNDS HIS HEAD.▌ ▐█▀ ▐',
        art=[
            '▌ ▄█▄ ▐',
            '▌ ▙█▟ ▐',
            '▌ ({"}) ▐',
            '▌  ▒  ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='CHANGE OF MIND, PAUSE IN LIFE',
    ),
    Major(
        title='13-DEATH',
        intro='APPEARS AS A SKULL      ▛▀▀▀▀▀▜ BEFORE WHICH ALL ARE    ▌  ▗ ▖▐ POWERLESS; THE FLOWER   ▌▗▄ ▓ ▐ OF LIFE IS NEARBY.      ▌▛▛▛)▘▐',
        art=[
            '▌▜▜▘( ▐',
            '▌▝▀  {"}▐',
            '▌▖ ▖{"}▓▐',
            '▌▀▀▀▔▔▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='RENEWAL, ALTERED CONSCIOUSNESS',
    ),
    Major(
        title='14-TEMPERANCE',
        intro='WITH ONE FOOT IN THE    ▛▀▀▀▀▀▜ MAIN STREAM OF COSMIC   ▌▗▄▖ *▐ CONSCIOUSNESS, AN ANGEL ▌▝{"}▘▄▗▐ POURS THE ESSENCE OF    ▌▐{+}▀█▜▐ LIFE FROM CUP TO CUP.   ▌▐██  ▐',
        art=[
            '▌▐█▙ ▓▐',
            '▌▀▓▀▓▓▐',
            '▌▓▓▓  ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='COORDINATION, MIND OVER MATTER',
    ),
    Major(
        title='15-THE DEVIL',
        intro='ABOVE A BESTIALIZED MAN ▛▀▀▀▀▀▜ AND WOMAN; HIS INVERTED ▌▌▐▄▟ ▐ TORCH MEANS DESTRUCTION.▌▌▛▜▀▌▐',
        art=[
            '▌▓▜{<}█▘▐',
            '▌ ▖▙▌▖▐',
            '▌{"}▘▝{"}▘▐',
            '▌{W}▚▞█▘▐',
            '▌█▞▚█▖▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='DEATH OF OLD SELF, REVOLUTION',
    ),
    Major(
        title='16-THE TOWER',
        intro='STRUCK BY SPIRITUAL     ▛▀▀▀▀▀▜ LIGHTNING FROM ABOVE,   ▌ ▔▂  ▐ THE TOWER CRUMBLES.     ▌ ▙▙▄▌▐',
        art=[
            '▌ ▐▐{/}▗▐',
            '▌ ▐{/}▗ ▐',
            '▌ ▐█{/}▝▐',
            '▌ ▐{/}█ ▐',
            '▌▗███▙▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='A LIFESTYLE CHANGE, BANKRUPTCY',
    ),
    Major(
        title='17-THE STAR',
        intro='RADIATES COSMIC ENERGY  ▛▀▀▀▀▀▜ UPON A MAIDEN STANDING  ▌. ▖. ▐ NEAR THE POOL OF LIFE.  ▌ ▚▙▘ ▐',
        art=[
            '▌▝▜█▀.▐',
            '▌ ▘▌▘)▐',
            '▌.  {"} ▐',
            '▌  ▝{W}▘▐',
            '▌▂▂▗█▖▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='INSPIRATION, DEVOTION, HEALTH',
    ),
    Major(
        title='18-THE MOON',
        intro='REFLECTS SUBCONSCIOUS   ▛▀▀▀▀▀▜ LIGHT UPON THE PATH OF  ▌▗▖▗▖.▐ CONSCIOUS PROGRESS AND  ▌{+}.▜█▖▐ THE CREATIONS OF MAN.   ▌█ .██▐',
        art=[
            '▌█ ▟█▘▐',
            '▌█▙▝▘ ▐',
            '▌  ▂▒▔▐',
            '▌▒▒▔  ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='IMAGINATION, INTUITION, DREAMS',
    ),
    Major(
        title='19-THE SUN',
        intro='SHINES GROWTH AND LIFE  ▛▀▀▀▀▀▜ ON THE NAKED CHILD OF   ▌▚▝▄▘▞▐ MAN AND ALL OF NATURE.  ▌▖▟█▙▗▐',
        art=[
            '▌▐███▌▐',
            '▌▘▜█▛▝▐',
            '▌▞ ▀ ▚▐',
            '▌ ▗{"}▖ ▐',
            '▌ ▗{.}▖ ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='ACHIEVEMENT, BALANCE IN LIFE',
    ),
    Major(
        title='20-JUDGEMENT',
        intro='AN ANGEL BLOWS ON HIS   ▛▀▀▀▀▀▜ TRUMPET TO LIBERATE MAN ▌▙{"}▟▙▖▐ FROM TERRESTRIAL LIMITS.▌▘{+}▘.▘▐',
        art=[
            '▌▄.*▗▄▐',
            '▌{"}  ▝{"}▐',
            '▌█▄{"}▄{W}▐',
            '▌█▗{.}▖█▐',
            '▌▀▘▂▝▀▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='RENEWAL, INNER ENLIGHTENMENT',
    ),
    Major(
        title='21-THE WORLD',
        intro='THE SUCCESSFUL SEEKER   ▛▀▀▀▀▀▜ OF SUPERCONSCIOUSNESS   ▌ ▄▀▄ ▐ DANCES JOYOUSLY WITHIN  ▌▞▗▄▖▚▐ THE WREATH OF NATURE.   ▌▐▝{"}▘▌▐',
        art=[
            '▌▌▙{W}▟▐▐',
            '▌▐▄█ ▌▐',
            '▌▚▘▐▖▞▐',
            '▌ ▀▄▀ ▐',
            '▙▄▄▄▄▄▟',
        ],
        meaning='EARNED REWARD, ASSURED SUCCESS',
    ),
]

BIG_T = [
    '▛▜▛▜',
    '▀▐▌▀',
    ' ▐▌',
]
READING_MEANINGS = [
    'OF THE WANDS-  A BEGINNING, NEW ENTERPRISE',
    'OF THE WANDS-  DOMINION, RICHES, GOOD FORTUNE',
    'OF THE WANDS-  COMMERCE, BUSINESS PARTNERSHIP',
    'OF THE WANDS-  ROMANCE, PROSPERITY, REFUGE',
    'OF THE WANDS-  STRIFE, STRUGGLING TO SUCCEED',
    'OF THE WANDS-  TRIUMPHANT NEWS, ADVANCEMENT',
    'OF THE WANDS-  STIFF COMPETITION, OPPOSITION',
    'OF THE WANDS-  LOVE PANGS, HASTE, MOVEMENT',
    'OF THE WANDS-  PREPAREDNESS, RESERVE STRENGTH',
    'OF THE WANDS-  HEAVY BURDEN, PROBLEMS SOLVED',
    'OF THE WANDS-  BRINGS GOOD TIDINGS; A CHILD',
    'OF THE WANDS-  A RIVAL; NEW ADDRESS, ABSENCE',
    'OF THE WANDS-  MAGNETIC WOMAN; ENTERPRISING',
    'OF THE WANDS-  FAMILY MAN; GOOD MARRIAGE',
    'OF THE CUPS-   ABUNDANCE, LOVE, SPIRITUALITY',
    'OF THE CUPS-   LOVE AFFAIR, UNION, HARMONY',
    'OF THE CUPS-   ABUNDANCE, VICTORY, HEALING',
    'OF THE CUPS-   CONTEMPLATION, RE-EVALUATION',
    'OF THE CUPS-   REGRET, MARITAL BITTERNESS',
    'OF THE CUPS-   CHILDHOOD MEMORIES, RENEWAL',
    'OF THE CUPS-   UNFOCUSED IDEAS, GREAT DREAMS',
    'OF THE CUPS-   ABANDONED PROJECT, LOVELORN',
    'OF THE CUPS-   SATISFACTION, ROBUST HEALTH',
    'OF THE CUPS-   HAPPY FAMILY LIFE, SUCCESS',
    'OF THE CUPS-   CONSIDERATE YOUTH; NEW METHOD',
    'OF THE CUPS-   ROMANTIC MAN; AN INVITATION',
    'OF THE CUPS-   BELOVED WOMAN; HAPPY MARRIAGE',
    'OF THE CUPS-   FRIENDLY BACHELOR; GENEROSITY',
    'OF THE SWORD-  GREAT FORCE, POWER, CONQUEST',
    'OF THE SWORD-  STALEMATE, A FAMILY TRUCE',
    'OF THE SWORD-  DELAY, SORROW, LOVE LOST',
    'OF THE SWORD-  RETREAT, CONVALESCENCE',
    'OF THE SWORD-  PHYSICAL CONQUEST, CONFLICT',
    'OF THE SWORD-  TRIUMPH, REPRESENTATION',
    'OF THE SWORD-  PARTIAL SUCCESS, UNCERTAINTY',
    'OF THE SWORD-  UNCERTAINTY, BONDAGE, CRISIS',
    'OF THE SWORD-  MISERY, DEATH OF A LOVED ONE',
    'OF THE SWORD-  MISFORTUNE, END OF DELUSIONS',
    'OF THE SWORD-  VIGILANT YOUTH; WARY, ALERT',
    'OF THE SWORD-  DOMINEERING MAN; SKILLFUL',
    'OF THE SWORD-  QUICK-WITTED WOMAN; SADNESS',
    'OF THE SWORD-  AUTHORITATIVE MAN; WISDOM',
    'OF PENTACLES-  ECSTASY, WEALTH, PROSPERITY',
    'OF PENTACLES-  HARMONIOUS CHANGE, DIPLOMACY',
    'OF PENTACLES-  ARTFUL MASTER, CONSTRUCTION',
    'OF PENTACLES-  POSSESSIVE, MISERLY, SELFISH',
    'OF PENTACLES-  DESTITUTION, LOVE GONE ASTRAY',
    'OF PENTACLES-  PHILANTHROPY, SHARED WEALTH',
    'OF PENTACLES-  GROWTH, ENDEAVOR, SOULMATE',
    'OF PENTACLES-  APPRENTICESHIP, EMPLOYMENT',
    'OF PENTACLES-  ACCOMPLISHMENT, WELL-BEING',
    'OF PENTACLES-  FAMILY LINEAGE, INHERITANCE',
    'OF PENTACLES-  DILIGENT YOUTH; SCHOLARSHIP',
    'OF PENTACLES-  METHODICAL MAN; PATIENCE',
    'OF PENTACLES-  INTELLIGENT WOMAN; GENEROSITY',
    'OF PENTACLES-  MAN OF CHARACTER; RELIABILITY',
    'THE FOOL-      AN IMPORTANT CHOICE IN LIFE',
    'THE MAGICIAN-  MASTERY, WISDOM, CREATIVITY',
    'HIGH PRIESTESS-HIDDEN INFLUENCES, DUALITY',
    'THE EMPRESS-   MARRIAGE, WEALTH, FERTILITY',
    'THE EMPEROR-   POWER, INTELLECT OVER PASSION',
    'THE HIEROPHANT-RITUAL, CONFORMITY, CONVENTION',
    'THE LOVERS-    SACRED OR PROFANE LOVE, CHOICE',
    'THE CHARIOT-   CONQUEST, TRIUMPH, GREATNESS',
    'STRENGTH-      TRIUMPH OF LOVE, ENERGY, POWER',
    'THE HERMIT-    WISDOM, PRUDENCE, GUIDANCE',
    'WHEEL/FORTUNE- GOOD FORTUNE, TURN OF LUCK',
    'JUSTICE-       BALANCED PERSONALITY, EQUALITY',
    'THE HANGED MAN-CHANGE OF MIND, PAUSE IN LIFE',
    'DEATH-         RENEWAL, ALTERED CONSCIOUSNESS',
    'TEMPERANCE-    COORDINATION, MIND OVER MATTER',
    'THE DEVIL-     DEATH OF OLD SELF, REVOLUTION',
    'THE TOWER-     LIFESTYLE CHANGE, BANKRUPTCY',
    'THE STAR-      INSPIRATION, DEVOTION, HEALTH',
    'THE MOON-      IMAGINATION, INTUITION, DREAMS',
    'THE SUN-       ACHIEVEMENT, BALANCE IN LIFE',
    'JUDGEMENT-     RENEWAL, INNER ENLIGHTENMENT',
    'THE WORLD-     EARNED REWARD, ASSURED SUCCESS',
]
READING_LABELS = [
    '{W1}█',
    '{W2}█',
    '{W3}█',
    '{W4}█',
    '{W5}█',
    '{W6}█',
    '{W7}█',
    '{W8}█',
    '{W9}█',
    '{W10}',
    '{W11}',
    '{W12}',
    '{W13}',
    '{W14}',
    '{C1}█',
    '{C2}█',
    '{C3}█',
    '{C4}█',
    '{C5}█',
    '{C6}█',
    '{C7}█',
    '{C8}█',
    '{C9}█',
    '{C10}',
    '{C11}',
    '{C12}',
    '{C13}',
    '{C14}',
    '{S1}█',
    '{S2}█',
    '{S3}█',
    '{S4}█',
    '{S5}█',
    '{S6}█',
    '{S7}█',
    '{S8}█',
    '{S9}█',
    '{S10}',
    '{S11}',
    '{S12}',
    '{S13}',
    '{S14}',
    '{P1}█',
    '{P2}█',
    '{P3}█',
    '{P4}█',
    '{P5}█',
    '{P6}█',
    '{P7}█',
    '{P8}█',
    '{P9}█',
    '{P10}',
    '{P11}',
    '{P12}',
    '{P13}',
    '{P14}',
    '{0}██',
    '{1}██',
    '{2}██',
    '{3}██',
    '{4}██',
    '{5}██',
    '{6}██',
    '{7}██',
    '{8}██',
    '{9}██',
    '{10}█',
    '{11}█',
    '{12}█',
    '{13}█',
    '{14}█',
    '{15}█',
    '{16}█',
    '{17}█',
    '{18}█',
    '{19}█',
    '{20}█',
    '{21}█',
]
BANNER = [
    ' ▐██████████████████████████',
    ' ▐█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜█',
    ' ▐█▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜▐█',
    ' ▐█▐▐▀█▀▌███ █▀█ ▟▀▜▖▛▜▛▜▐▐█',
    ' ▐█▐▝▘█▝▘▐ ▌ ▐▄▛ █ ▐▌▀▐▌▀▐▐█',
    ' ▐█▐  █  ▟▄▙ ▐ ▜ █ ▐▌ ▐▌ ▐▐█',
    ' ▐█▐ ▐█▌▐█ █▌█▌█▌▜▄▟▘ ██ ▐▐█',
    ' ▐█▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟▐█',
    ' ▐█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟█',
    ' ▐██████████████████████████',
]
BIG_A = [
    '▐██▌',
    ' ▌▐',
    '▗▙▟▖',
]
INTRO_PAGES = [
    '█▌▐█S SCIENCE COMES TO REALIZE  WHAT TAROT USERS HAVE LONG      UNDERSTOOD -THAT EVENTS IN      TIME AND SPACE CAN BE ALTERED   BY OBSERVING THEM- WE FIND WE   HAVE A POWERFUL NEW MEDIUM TO   HELP US REACH THE TAROT. THE    COMPUTER CAN NOW BE WHAT THE    CARDS HAVE ALWAYS BEEN: A WAY   OF READING -OF TOUCHING- THE    ETERNAL TAROT...',
    '█▌▐█T THE HEART OF THE TAROT    EXPERIENCE IS THE READING. WE   ASK A QUESTION, THE CARDS ARE   CAST AND APPEAR IN A LAYOUT     BEFORE US. THEIR MESSAGE MAY    NOT BE CLEAR AT FIRST. WE MAY   HAVE TO THINK DEEPLY, AND EVEN  MEDITATE UPON THE MEANINGS, BUT THE TAROT ALWAYS HAS AN ANSWER-',
]
LAYOUT = [
    '     ▓▓▓              ▓▓▓       ',
    '     ▓▓▓              ▓▓▓       ',
    '     ▓▓▓CROWNS        ▓▓▓FINAL  ',
    '     ▓▓▓YOU       ▓▓▓ ▓▓▓OUTCOME',
    '     ▓▓▓          ▓▓▓ ▓▓▓       ',
    '   SIGNIFICATOR   ▓▓▓           ',
    '▓▓▓  ▓▓▓          ▓▓▓FAMILY    ',
    '▓▓▓ ▒▒▒▒▒CROSSES  ▓▓▓OPINION    ',
    '▓▓▓ ▒▒▒▒▒YOU                    ',
    '▓▓▓ ▒▒▒▒▒      ▓▓▓      ▓▓▓     ',
    '▓▓▓  ▓▓▓COVERS ▓▓▓BEFORE▓▓▓     ',
    'BEHIND  YOU    ▓▓▓YOU   ▓▓▓YOUR ',
    'YOU            ▓▓▓      ▓▓▓HOPES',
    '     ▓▓▓       ▓▓▓  ▓▓▓ ▓▓▓     ',
    '     ▓▓▓            ▓▓▓         ',
    '     ▓▓▓BENEATH     ▓▓▓YOUR     ',
    '     ▓▓▓YOU         ▓▓▓FEARS    ',
    '     ▓▓▓            ▓▓▓         ',
]
RESULTS_HEADER = ['▐▜▛▌', ' ▐▌', ' ██HE TAROT READING IS DIRECTLY RELATED TO YOUR QUESTION...']


# --- ZX81 screen emulation ---

INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()
REVERSE, NORMAL = '\x1b[7m', '\x1b[0m'


class Quit(Exception):
    pass


class Screen:
    """A 32x22 character display with ZX81 PRINT semantics."""

    WIDTH, HEIGHT = 32, 22

    def __init__(self):
        self.cls()

    def cls(self):
        self.cells = [[(' ', False)] * self.WIDTH for _ in range(self.HEIGHT)]
        self.row = self.col = 0

    def write(self, text, markup=True):
        inverse = False
        for ch in text:
            if markup and ch in '{}':
                inverse = ch == '{'
                continue
            if self.col >= self.WIDTH:
                self.newline()
            if self.row < self.HEIGHT:
                self.cells[self.row][self.col] = (ch, inverse)
            self.col += 1

    def newline(self):
        self.row += 1
        self.col = 0

    def print(self, text='', markup=True):
        self.write(text, markup)
        self.newline()

    def print_at(self, row, col, text, markup=True):
        self.row, self.col = row, col
        self.print(text, markup)

    def print_tab(self, col, text):
        # TAB to a column we've already passed moves to the next line.
        if self.col > col:
            self.newline()
        self.col = col
        self.print(text)

    def render(self, color):
        lines = []
        for row in self.cells:
            line, inverse = '', False
            for ch, inv in row:
                if inv != inverse and color:
                    line += REVERSE if inv else NORMAL
                    inverse = inv
                line += ch
            lines.append('  ' + line + (NORMAL if inverse else ''))
        return lines

    def show(self):
        lines = self.render(INTERACTIVE)
        clear = '\x1b[H\x1b[2J' if INTERACTIVE else '\n'
        sys.stdout.write(clear + '\n'.join(lines) + '\n')
        sys.stdout.flush()


def read_key():
    """Read one keypress, uppercased. Enter comes back as '\\n'."""
    if not INTERACTIVE:
        line = sys.stdin.readline()
        if not line:
            raise Quit
        return (line.strip()[:1] or '\n').upper()
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getwch()
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if ch in ('\x03', '\x04'):
        raise Quit
    return '\n' if ch == '\r' else ch.upper()


def wait_key(scr, key):
    """Like 'IF INKEY$<>"C" THEN GOTO ...', but Enter works too."""
    scr.show()
    while read_key() not in (key, '\n'):
        pass


def read_line(scr):
    scr.show()
    try:
        return input('  > ').strip().upper()
    except EOFError:
        raise Quit


def ask_number(scr, lo, hi):
    while True:
        try:
            n = int(read_line(scr))
        except ValueError:
            continue
        if lo <= n <= hi:
            return n


def pause(scr, seconds):
    scr.show()
    if INTERACTIVE:
        time.sleep(seconds)


def big_title(scr, text):
    for line in BIG_T:
        scr.print(line)
    scr.print(' ██' + text)


# --- CARDS ---

def cards_continue(scr):
    scr.print_at(21, 14, '"C" TO CONTINUE-')
    wait_key(scr, 'C')


def draw_suit(scr, suit):
    scr.print(suit.header)
    scr.print(suit.intro)
    for line in suit.art:
        scr.print_tab(24, line)


def draw_major(scr, card):
    scr.print(card.title)
    scr.print(card.intro)
    for line in card.art:
        scr.print_tab(24, line)
    scr.print()
    scr.print_at(11, 0, 'MEANING-')
    scr.print(card.meaning.ljust(30))


def show_suit(scr, suit):
    draw_suit(scr, suit)
    for n, meaning in enumerate(suit.meanings, 1):
        scr.print_at(suit.number_row, 25, f'{suit.letter}{n}')
        scr.print_at(11, 0, 'MEANING-')
        scr.print(meaning.ljust(30))
        cards_continue(scr)


def show_major(scr):
    for card in MAJOR:
        draw_major(scr, card)
        cards_continue(scr)
        scr.cls()


def cards(scr):
    scr.cls()
    big_title(scr, 'HE TAROT CARDS-')
    scr.print()
    for line in ('THE ILLUSTRATED MAJOR ARCANA', 'SYMBOLICALLY REPRESENT THE',
                 'METAPHYSICAL BASIS OF OUR', 'QUEST FOR ENLIGHTENMENT.', '',
                 'THE MINOR ARCANA CONSTITUTE', 'A COMPREHENSIVE PSYCHOLOGICAL',
                 'EVALUATION OF MAN.', ''):
        scr.print(line)
    while True:
        for line in ('CHOOSE ONE (ENTER 1,2,OR 3)', '', '1-MAJOR CARDS', '2-MINOR CARDS', '3-END PROGRAM'):
            scr.print(line)
        choice = ask_number(scr, 1, 3)
        scr.cls()
        if choice == 3:
            return
        if choice == 1:
            show_major(scr)
            continue
        big_title(scr, 'HE MINOR CARDS-')
        for line in ('ONE TO TEN,11-PAGE, 12-KNIGHT,', '13-QUEEN AND 14-KING.', '',
                     'CHOOSE A SUIT-', '', '1-WANDS', '2-CUPS', '3-SWORDS', '4-PENTACLES'):
            scr.print(line)
        suit = SUITS[ask_number(scr, 1, 4) - 1]
        scr.cls()
        show_suit(scr, suit)
        scr.cls()


# --- GALLERY ---

def gallery(scr):
    """Print every card screen in order, without waiting for keys."""
    color = sys.stdout.isatty()

    def dump():
        lines = scr.render(color)
        while lines and not lines[-1].strip():
            lines.pop()
        print('\n'.join(lines) + '\n')

    for card in MAJOR:
        scr.cls()
        draw_major(scr, card)
        dump()
    for suit in SUITS:
        scr.cls()
        draw_suit(scr, suit)
        dump()
        for n, meaning in enumerate(suit.meanings, 1):
            print(f'  {suit.letter}{n:<3} {meaning}')
        print()


# --- READING ---

# Where each card lands on the layout, in draw order:
# significator, crosses, covers, beneath, behind, crowns,
# before, fears, family, hopes, outcome.
POSITIONS = [(8, 5), (12, 5), (10, 5), (17, 5), (10, 0), (4, 5),
             (13, 15), (17, 20), (7, 18), (13, 24), (4, 22)]
RESULT_LABELS = ['SIGNIFIES YOU:', 'AURA ABOUT IT:', 'IN OPPOSITION:', 'FOUNDATION OF:',
                 'WHAT HAS PAST:', 'WHAT MIGHT BE:', 'IN THE FUTURE:', 'YOU FEAR THIS:',
                 'FAMILY THINKS:', 'YOU ASPIRE TO:', 'FINAL OUTCOME:']


def reading_continue(scr):
    scr.print_at(21, 0, '        PRESS "C" TO CONTINUE-')
    wait_key(scr, 'C')


def ask_question(scr):
    while True:
        scr.cls()
        scr.print()
        big_title(scr, 'YPE IN YOUR QUESTION-')
        scr.print(' (ONE LINE, PLEASE)')
        question = read_line(scr)
        if len(question) <= 30:
            return question


def lay_out_cards(scr, question, picks):
    scr.cls()
    scr.print('NOW, CONCENTRATE...')
    pause(scr, 1)
    scr.print()
    for line in LAYOUT:
        scr.print(line)
    scr.print_at(0, 0, ' ' * 20)
    scr.print_at(0, 0, f'"{question}"', markup=False)
    for (row, col), card in zip(POSITIONS, picks):
        scr.print_at(21, 6, 'PRESS "T" TO TURN CARDS-')
        wait_key(scr, 'T')
        scr.print_at(row, col, READING_LABELS[card])
    reading_continue(scr)


def interpret(scr, question, picks):
    scr.cls()
    for line in RESULTS_HEADER:
        scr.print(line)
    scr.print(f'"{question}"', markup=False)
    for i, (label, card) in enumerate(zip(RESULT_LABELS, picks)):
        if i == 5:
            reading_continue(scr)
            scr.cls()
        scr.print()
        pause(scr, 0.6)
        scr.print(label + READING_LABELS[card] + READING_MEANINGS[card].ljust(45))
    reading_continue(scr)


def reading(scr):
    scr.cls()
    scr.print_at(5, 0, BANNER[0])
    for line in BANNER[1:]:
        scr.print(line)
    scr.print()
    scr.print('   (C)1983  COMPUTER PHOOD')
    pause(scr, 2)
    for page in INTRO_PAGES:
        scr.cls()
        scr.print()
        for line in BIG_A:
            scr.print(line)
        scr.print(page)
        reading_continue(scr)
    while True:
        question = ask_question(scr)
        picks = random.sample(range(78), 11)
        lay_out_cards(scr, question, picks)
        interpret(scr, question, picks)
        scr.cls()
        scr.print_at(2, 0, 'IF THIS READING WAS NOT CLEAR,  PRESS "N" FOR A NEW READING.')
        scr.print()
        scr.print('ANY OTHER KEY TO FINISH.')
        scr.show()
        if read_key() != 'N':
            return


# --- Launcher ---

def main():
    scr = Screen()
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else None
    modes = {'cards': cards, 'reading': reading, 'gallery': gallery}
    if mode is not None and mode not in modes:
        sys.exit(__doc__.split('Usage:')[1].rstrip())
    try:
        if mode:
            modes[mode](scr)
            return
        while True:
            scr.cls()
            big_title(scr, 'AROT')
            scr.print()
            for line in ('TIMEX SINCLAIR 1000, 1983', '', '1-THE TAROT CARDS', '2-A TAROT READING', '3-QUIT'):
                scr.print(line)
            choice = ask_number(scr, 1, 3)
            if choice == 3:
                return
            (cards if choice == 1 else reading)(scr)
    except (Quit, KeyboardInterrupt):
        pass
    finally:
        if INTERACTIVE:
            sys.stdout.write(NORMAL + '\n')


if __name__ == '__main__':
    main()
