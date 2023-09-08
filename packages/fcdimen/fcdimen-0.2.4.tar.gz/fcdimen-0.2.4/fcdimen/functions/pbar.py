import sys


def progressbar(iterations, prefix="", size=60, out=sys.stdout):
    """Illustrating progress bar in terminal

    Parameters:
    iterations: list
      for loop range as a list

    Returns:
    print strings like a progress bar
    """
    count = len(iterations)
    def show(j):
        x = int(size*j/count)
        y = int((j/count) * 100)
        print("{}[{}{}] {}/100".format(prefix, "="*x, "."*(size-x), y), end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(iterations):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)
