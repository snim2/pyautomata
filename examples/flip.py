def rules(state, neighbours):
    white = (255, 255, 255)
    black = (0, 0, 0)
    if state == white: return black
    return white
