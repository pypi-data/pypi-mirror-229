
import time
import logging


from triplix.core import cli
from triplix.core import configurations


logging.basicConfig(
    level=logging.DEBUG if configurations.configs['debug'] else logging.INFO,
    format='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():

    """Main function of Triplix"""
    # ctime = time.time()
    cli_args = cli.parse_cli_arguments()
    # print(cli_args)
    # print(f'Program ended. It took {time.time() - ctime:0.4f}s')


if __name__ == "__main__":
    main()
