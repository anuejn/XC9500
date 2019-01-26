# Bitstream format

According to the Family datasheet, the CPLD consists of three main parts.

The following initial calculations assume, that all muxes are use one hot encoding and therefore require a rather large amount of fuses. Be warned: The calculations are likely to be incorrect and totaly off.

## Fast Connect II

Most likely, the "Fast Connect II" switchbox has `(NUMBER_OF_IOs + NUMBER_OF_FBs * 18) * (NUMBER_OF_FBS * 54)` fuses. Each of them determines the connection betwen one input and one output.

For the `XC9572XL-TQ100` this equals to `(72 + 4 * 18) * (4 * 54)` = 31104 of 46656 and thus 66.6% of the total amount of fuses.

## Function Blocks

A FB consists of a programmable and array, a product term allocator and 18 Macrocells.  
In the `XC9572XL-TQ100` each FB has 3744 fuses.

### Programmable And Array

108 signals (54 + 54 inverted) can form 90 product terms.  
This leads to 9720 fuses. TODO: definitely wrong -> way to many fuses

### Product term allocators

The Product term allocator can route each of its 7 inputs either to set, reset, clock, left or right. This leads to 7 * 5 = 35 Fuses (630/628 per FB).

### Macro cells

The Macrocell uses 6 fuses for set / reset, and 6 fuses for clock.
2 fuses are used to bypass the ff, 3 fuses determine the second input of the second input of the xor on the D input of the ff (1 / 0 / IN). (17 - 18 Fuses per Macro cell / 306/324 per FB)


## IO Blocks

The OE muxes (including the invert select mux) requires 8 fuses for the `XC95144XL` and the `XC95288XL` (they feature 4 global OE signals) and 6 fuses for the smaller devices.

The slew rate select and the user pogrammable ground feature are presumably using 1 Fuse each.

The total amount of fuses for one IOB is 8-10.  
For the `XC9572XL-TQ100` this equals to `72 * 8` = 576 of 46656 and thus 1.2% of the total amount of fuses.