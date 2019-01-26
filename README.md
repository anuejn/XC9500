# XC9500 Reverse Engineering

WIP open source tooling for the XC9500 / XC9500XL series of CPLDs from Xilinx.  
Primary focus of efford is on the XC95144XL for now.

## Useful documentation

To get started the following documents are a good intro into the architecture:

* [The Family Datasheet](https://www.xilinx.com/support/documentation/data_sheets/ds054.pdf)
* [The xc3sprog code and documentation](https://sourceforge.net/projects/xc3sprog/) (or see submodule in `bitstream/xc3sprog`)

## Bitstream Documentation

Nothing is done on this front yet.

For example bitstreams, see the `misc/bitstreams/` folder.

## Simulator

Nothing is done on this front yet.

A complete model of the CPLD is to be written. It should be able to be "programmed" with real bitstreams in jedec format and should behave like a real cpld.

## Yosys Backend

Nothing is done on this front yet.

The primary goal is to be able to go from yosys rtlil to a working bitstream in jedec file format.
Timing optimization / analysis is only secondary for now.