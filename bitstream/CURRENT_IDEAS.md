# bitstream structure
Comparing the bitstreams for devices of different size's a column structure becomes visible. In the `jed` file each line always has `NUMBER_OF_FBS` values, seperated by spaces. Reading these top down they form columns. 
Each column contains `108 * 108 = 11664` bits in `108` groups of `9 * 8` bits and then `6 * 6` bits. 

One of these groups looks like this.
```
column 1  column 2 ...
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
00000000  00000000
                     
000000    000000
000000    000000
000000    000000
000000    000000
000000    000000
000000    000000
```
Trying different bitstreams, the configuration of a FB (the inputs from the interconnect into the and array, the and array configuration and the macrocell configuration) is always in the same column. We conclude, that the first column contains the configuration for the first FB, the second column for the second FB and so on. 

Now each FB has `108 * 108` bits of configuration. Fuzzing the and array shows, that the bits controlling which input / which inverse input is and'ed together to for a specific macrocell input of a specific macrocell are always seperated by `108` bits. Because of this we assume the configuration of each FB is arranged in a `108` bit square, where `90` of the `108` columns each configure a output of the and array.


## AND array
The columns can be grouped in several ways. Each macrocell has `5` inputs from the and array and grouping always the 1st input of all macrocells together and then all the 2nd inputs of all macrocells yield the following grouping (each value is always the column that controls that input):

| macrocell | 2nd input | a'th input | b'th input | c'th input | d'th input |
|-----------|-----------|------------|------------|------------|------------|
|         1 |        32 |          0 |          8 |         16 |         24 |
|         2 |        72 |         40 |         48 |         56 |         64 |
|         3 |       102 |         78 |         84 |         90 |         96 |
|         4 |        33 |          1 |          9 |         17 |         25 |
|         5 |        73 |         41 |         49 |         57 |         65 |
|         6 |       103 |         79 |         85 |         91 |         97 |
|         7 |        34 |          2 |         10 |         18 |         26 |
|         8 |        74 |         42 |         50 |         58 |         66 |
|         9 |       104 |         80 |         86 |         92 |         98 |
|        10 |        35 |          3 |         11 |         19 |         27 |
|        11 |        75 |         43 |         51 |         59 |         67 |
|        12 |       105 |         81 |         87 |         93 |         99 |
|        13 |        36 |          4 |         12 |         20 |         28 |
|        14 |        76 |         44 |         52 |         60 |         68 |
|        15 |       106 |         82 |         88 |         94 |        100 |
|        16 |        37 |          5 |         13 |         21 |         29 |
|        17 |        77 |         45 |         53 |         61 |         69 |
|        18 |       107 |         83 |         89 |         95 |        101 |

The a'th, b'th, c'th and d'th input can not yet be assigned to the specific number.


## USERCODE
The usercode is a 4 letter ascii code. It is located in the first FB in rows 6 and 7 and columns `{0,1,2,3,4,5,6,7} * 8 + {6, 7}`. The letters are stored in order, but each two bits are swapped. If `data` contains a array with the bits of the first FB in the order they appear in the `jed` file, the following python code extracts the usercode:
```python
bits = []

for row in range(6, 8):
    for col in range(8):
        bits.append(data[108 * row + 8 * col + 7])
        bits.append(data[108 * row + 8 * col + 6])

usercode = bytes(np.packbits(bits)).decode("ascii")
```

## Interconnect
The interconnect is hard to fuzz, because there is no way to select the specific input of a FB that should be used and the `ISE` fitter quite happily changes which of the inputs is used, when changing the input into the switchbox that is routed to a FB. 

Nonetheless there are some patterns observible by looking at some indermediate files. Specifically the `vm6` files contain two interesting lines:
```
FB_ORDER_OF_INPUTS | FOOBAR1_ | 1 | i1 | A16
```
and 
```
FB_IMUX_INDEX | FOOBAR1_ | -1 | 323 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 \
| -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1
```

first of all we can learn, that xilinx names the FBs `FOOBARx_` and further the number after `FB_ORDER_OF_INPUTS | FOOBAR1_ |` seems to be the number of the input into the and array (from the interconnect). It is zero based. Finally after `FB_IMUX_INDEX | FOOBAR1_ |` there are `54` numbers which seems to control the interconnect configuration. The first number seems to control the interconnect configuration of the first input of the and array, and so on. A `-1` seems to mean no connection, valid connections seem to be positive integers. The exact meaning of these integers is still unclear.


# Plan
## Specific macrocell inputs
Each of the five macrocell inputs has a special function that only that input can perform. By using logic as input that uses these specific functions it should be possible to assign the and array rows to the specific inputs of the macrocell. 
## Macrocell configuration
The macrocell configuration seems quite straight forward to fuzz, as all the different configurations seems to have quite specific uses and thus should be easily exercised by writing appropriate verilog.
## Interconnect
It is still unclear how exactly the interconnect configuration works, currently I think we need to generated more bitstreams to try find a pattern, or may actually find all possible routes.
By generating more bitstreams we can try to either understand the bitstream directly or try and understand the `vm6` files.
## Synthesis / PNR
Do we want to try / improve `yosys` or maybe write something on our own specific to CPLDs / SoP architectures (it should probably be quite flexible to later implement other CPLD architectures aswell)

For PNR it is unclear how well `nextpnr` could be used, probably not that well. We should probably investigate the coolrunner II PNR by `rqou`.

## Verification
To verify all our assumptions the plan is to write a tool that converts a bitstream to verilog which is then checked against the verilog that generated that bitstream, using formal equivalence checking. By employing a fuzzing tool it should be possible to quickly find and minimize verilog that is converted into a bitstream, that we don't understand correctly and then to hopefully improve our understanding of the bitstream.
