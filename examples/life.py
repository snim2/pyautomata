def rules(state, neighbours):
    """Rules for John Conway's Game of Life.
    """
    white = (255, 255, 255)
    black = (0, 0, 0)    
    live_neighbours = len(filter(lambda x: x.state == white, neighbours.values()))
#    if state == white: print live_neighbours
    if state == white and live_neighbours < 2:
        return black
    elif state == white and live_neighbours > 3:
        return black
    elif state == white:
        return white
    elif state == black and live_neighbours == 3:
        return white
    return state
