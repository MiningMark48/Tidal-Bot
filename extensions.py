extensions = {
    "bot": [
        "bot_cmds"
    ],
    "fun": [
        "battleroyale",
        "blackjack",
        "fun",
        "minesweeper",
        "numberguess",
        "pressbutton",
        "rroulette",
        "speedtype",
        "sudoku",
        "trivia",
        "userguess",
        "wouldyourather",
        "xkcd"
    ],
    "images": [
        "memes"
    ],
    "info": [
        "corona",
        "dictionary",
        "info",
        "stock",
        "urbandict",
        "wikipedia"
    ],
    "preferences": [
        "userprefs"
    ],
    "servmng": [
        "reactionroles",
        "rules",
        "rum",
        "servmng",
        "temprole"
    ],
    "utility": [
        "announce",
        "autourlshort",
        "colorgen",
        "lyrics",
        "memesearch",
        "poll",
        "progress",
        "random",
        "reddit",
        "stega",
        "tags",
        "utility"
    ],
    "none": [
        "errors",
        "owner"
    ]
}

def get_extensions():
    exts = []

    for cat in extensions:
        for e in extensions[cat]:
            if cat == "none":
                exts.append(e)
            else:
                exts.append(f"{cat}.{e}")

    return exts
