from solver import MineSAT

_CLEAN_99_BOARD = [
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????"
]

_TEST_BOARD = [
    "????????",
    "????????",
    "?2???3??",
    "????1111",
    "?1??1000",
    "??2?1000",
    "????1111",
    "?????1??"
]

_CHALLENGE_BOARD = [
    '??????',
    '???2??',
    '???4??',
    '?2??2?',
    '?2222?',
    '?1001?'
]

MS = MineSAT(_TEST_BOARD)
tiles = MS.find_safe_tiles()
print(tiles)