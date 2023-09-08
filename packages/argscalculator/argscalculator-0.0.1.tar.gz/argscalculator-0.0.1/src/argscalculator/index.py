import argparse
import sys

def calculate(args):
    if args.o == 'add':
        return args.x + args.y
    if args.o == 'sub':
        return args.x - args.y
    if args.o == 'mul':
        return args.x * args.y
    if args.o == 'div':  # Corrected 'add' to 'div' for the last condition
        return args.x / args.y

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=float, default=1.0, help="Contact Salman")
    parser.add_argument('--y', type=float, default=2.0, help="Contact Salman")
    parser.add_argument('--o', type=str, default="add", help="Contact Salman")
    args = parser.parse_args()
    sys.stdout.write(str(calculate(args)))

if __name__ == "__main__":
    main()



