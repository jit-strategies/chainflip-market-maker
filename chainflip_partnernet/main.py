import sys
import getopt
from chainflip_partnernet.run_strategy_partnernet import run_stream_strategy, run_jit_strategy


def main(argv):
    opts, args = getopt.getopt(argv, "h:", ['strategy'])
    for opt, arg in opts:
        if opt == '-h':
            print('help command')
            sys.exit()
        elif opt in "--strategy":
            if args[0] == 'stream':
                run_stream_strategy()
            elif args[0] == 'jit':
                run_jit_strategy()
            else:
                print(args[0])
                return
        else:
            return


if __name__ == '__main__':
    main(sys.argv[1:])
