# Bitstream format

According to the Family datasheet, the CPLD consists of three main parts.

For initial calculations all muxes are assumed to use one hot encoding and therefore require a rather large amount of fuses.

## Fast Connect II

Most likely, the "Fast Connect II" switchbox has `(NUMBER_OF_IOs + NUMBER_OF_FBs * 18) * (NUMBER_OF_FBS * 54)` fuses. Each of them determines the connection betwen one input and one output.

For the `XC9572XL-TQ100` this equals to `(72 + 4 * 18) * (4 * 54)` = 31104 of 46656 and thus 66% of the total amount of fuses.

## Function Blocks

To be thought about.

## IO Blocks

The OE muxes (including the invert select mux) requires 8 fuses for the `XC95144XL` and the `XC95288XL` (they feature 4 global OE signals) and 6 fuses for the smaller devices.

The slew rate select and the user pogrammable ground feature are presumably using one Fuse each.

The total amount of fuses for one IOB is to be 8-10

For the `XC9572XL-TQ100` this equals to `72 * 8` = 576 of 46656 and thus 1.2% of the total amount of fuses.