import argparse
from main import main   # or your engine entry function


def run():
    parser = argparse.ArgumentParser(description="Event Driven Trading System")

    parser.add_argument(
        "mode",
        choices=["backtest", "live"],
        help="Trading mode"
    )

    parser.add_argument(
        "config",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    if args.mode == "backtest":
        print("Running backtest...")
        main(mode="backtesting", config_file=args.config)

    elif args.mode == "live":
        print("Running live trading...")
        main(mode="live", config_file=args.config)


if __name__ == "__main__":
    run()