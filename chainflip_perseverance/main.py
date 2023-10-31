import sys
import getopt

from chainflip_perseverance.run_stream_strategy_perseverance import run_stream_strategy
from chainflip_perseverance.run_jit_strategy_perseverance import run_jit_strategy


def main(argv):

    maker_id = "JIT"  # Set maker id
    opts, args = getopt.getopt(argv, 'h:', ['strategy'])
    for opt, arg in opts:
        if opt == '-h':
            print('help command')
            sys.exit()
        elif opt in '--strategy':
            if args[0] == 'stream':
                run_stream_strategy(maker_id)
            elif args[0] == 'jit':
                run_jit_strategy(maker_id)
            else:
                print(args[0])
                return
        else:
            return


if __name__ == '__main__':
    main(sys.argv[1:])
