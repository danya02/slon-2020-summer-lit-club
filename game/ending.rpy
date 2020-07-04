label ending_init:
    "Начинается разветвление на концовки."
    if incident1_visited[0] == "Обсудить с знакомым.":
        jump ending_talked
    jump ending_default

label ending_default:
    "Это концовка по умолчанию. Ничего интересного не произошло."
    return

label ending_talked:
    "Это та концовка, в которой мы обсудили с знакомым сначала."
    return
