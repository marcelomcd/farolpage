# utils.py
def get_progress_color(percent):
    percent = max(0, min(percent, 100))
    if percent < 50:
        r = 255
        g = int(5.1 * percent)
        b = 0
    else:
        r = int(255 - (5.1 * (percent - 50)))
        g = 255
        b = 0
    return f'rgb({r},{g},{b})'
