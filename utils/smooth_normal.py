def smooth_add_pos(pos1,pos2):
    if pos1==pos2:
        return pos1
    smooth_x = 0.8 * pos1[0] + 0.2 * pos2[0]
    smooth_y = 0.8 * pos1[1] + 0.2* pos2[1]
    return (smooth_x,smooth_y)

    