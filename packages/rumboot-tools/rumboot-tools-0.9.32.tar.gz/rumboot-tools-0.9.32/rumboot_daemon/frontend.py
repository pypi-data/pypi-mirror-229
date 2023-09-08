from rumboot.chipDb import ChipDb
from rumboot.ImageFormatDb import ImageFormatDb
from rumboot.resetSeq import ResetSeqFactory
from rumboot.cmdline import arghelper
from rumboot.terminal import terminal
from rumboot.server import server
import os
import argparse
import rumboot_xrun
import rumboot
from parse import *

def cli():
    resets  = ResetSeqFactory("rumboot.resetseq")
    formats = ImageFormatDb("rumboot.images")
    chips   = ChipDb("rumboot.chips")

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="rumboot-daemon {} - Collaborative board access daemon\n".format(rumboot.__version__) +
                                    rumboot.__copyright__)
    helper = arghelper()
    helper.add_terminal_opts(parser)
    helper.add_file_handling_opts(parser)
    helper.add_resetseq_options(parser, resets)
    parser.add_argument("-L", "--listen",
                        help="Specify address:port to listen (default 0.0.0.0:10000)",
                        nargs=1, metavar=('listen'), default=["0.0.0.0:10000"],
                        required=False)
    parser.add_argument("-m", "--max-usage-time",
                        help="Specify maximum time a client can use the board before being kicked (seconds)",
                        default = 360,
                        type = int,
                        required=False)
    parser.add_argument("--execute-binaries-from-temp-dir",
                        help="Super-special debug mode. Mock a bootrom, receive upload binaries and exec them",
                        action="store_true",
                        required=False)

    opts = parser.parse_args()
    if opts.execute_binaries_from_temp_dir:
        opts.port = "loop://"

    chip, term, reset = helper.create_core_stuff_from_options(opts)

    c = helper.detect_chip_type(opts, chips, formats)

    if opts.log:
        term.logstream = opts.log

    srv = server(term, opts.listen[0], opts.max_usage_time, opts.execute_binaries_from_temp_dir)
    srv.set_reset_seq(reset)

    if "file" in opts:
        srv.preload_binaries(opts.file)

    return srv.loop()
    
