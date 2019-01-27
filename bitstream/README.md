# Bitstream format

According to the Family datasheet, the CPLD consists of three main parts.

The following initial calculations assume, that all muxes are use one hot encoding and therefore require a rather large amount of fuses. Be warned: The calculations are likely to be incorrect and totaly off.

## Fast Connect II

Most likely, the "Fast Connect II" switchbox has `(NUMBER_OF_IOs + NUMBER_OF_FBs * 18) * (NUMBER_OF_FBS * 54)` connections. Each of them determines the connection betwen one input and one output. Because one input can only connect to one output, there is probably one 8-10 bit value for each input.

For the `XC9572XL-TQ100` this equals to `8 * (4 * 54)` = 1728 of 46656 and thus 3.7% of the total amount of fuses.

## Function Blocks

A FB consists of a programmable and array, a product term allocator and 18 Macrocells.  
In the `XC9572XL-TQ100` each FB has (9720 + 1008 + 342) = 11070 Fuses.  
This results in a total of 44280 Fuses (94.9%) for the `XC9572XL-TQ100`.

### Programmable And Array

108 signals (54 + 54 inverted) can form 90 product terms.  
This leads to 108 * 54 = 9720 fuses.

### Product term allocators

The Product term allocator can route each of its 7 inputs (5 + before and after) either to set, ff in, reset, clock, clock enable, before, after. This leads to 7 * 8 = 65 Fuses (1008/1006 per FB).

### Macro cells

The Macrocell uses 6 fuses for set / reset, and 6 fuses for clock.
2 fuses are used to bypass the ff, 3 fuses determine the second input of the xor on the ff (1 / 0 / IN).  
1 Fuse determines the type of the ff (D/T) and one the reset value.
This gives us 19 Fuses per Macro cell / 342 per FB

Probably one bit is to be discovered here.

## IO Blocks

The OE muxes (including the invert select mux) requires 9 fuses for the `XC95144XL` and the `XC95288XL` (they feature 4 global OE signals) and 7 fuses for the smaller devices.

The slew rate select, the user pogrammable ground feature are presumably using 1 fuse each.

The total amount of fuses for one IOB is 9-11.  
For the `XC9572XL-TQ100` this equals to `72 * 9` = 648 of 46656 and thus 1% of the total amount of fuses.

# Conclusion / Progress

The above fuse definitions leave 0 of the 46656 Fuses of a `XC9572XL-TQ100` unexplained.

However, using two bits for a two input mux seems to be a doubious but since the numbers lign up quite well, we are probably having the fuses in the right blocks.
