# Bitstream format

According to the Family datasheet, the CPLD consists of three main parts.

The following initial calculations assume, that all muxes are use one hot encoding and therefore require a rather large amount of fuses. Be warned: The calculations are likely to be incorrect and totaly off.

## Fast Connect II

Most likely, the "Fast Connect II" switchbox has `(2 * NUMBER_OF_FBS * NUMBER_OF_MACROCELLS_PER_FB)` inputs. There are `18` macrocells per FB and each macrocell has a feedback path, that feeds the output of the macrocell into the switchbox and a input from a IO cell. Each function block has a `54` and array with `54` inputs, so the switchbox probably has `(NUMBER_OF_FBS * 54)` outputs. If this switchbox would use one hot encoding it would be huge, so it probably doesn't. Additionally the size of the bitstream of the different models is always `11664 * NUMBER_OF_FB`. If each device would always use the minimal encoding for the switchbox the number of bits used for this encoding should grow quadratically with the number of FBs. Because it only grows linear even the bitstreams for the small devices probably contain the bits for the largest possible switchbox (16 FBs). Going from the outputs, there are `576` different inputs (`2 * 16 * 18`) each output can connect to. This could be configured in no less than `10` bits per output.

For the `XC9572XL-TQ100` this equals to `10 * (4 * 54)` = 2160 of 46656 and thus 4.6% of the total amount of fuses.

## Function Blocks

A FB consists of a programmable and array, a product term allocator and 18 Macrocells.  
In the `XC9572XL-TQ100` each FB has (9720 + 504 + 306) = 10530 Fuses.  
This results in a total of 42120 Fuses (90.28%) for the `XC9572XL-TQ100`.

### Programmable And Array

108 signals (54 + 54 inverted) can form 90 (5 per macrocell) product terms.  
This leads to `108 * 90 = 9720` fuses.

### Product term allocators

The Product term allocator can assign its 7 inputs (5 + before and after) inputs to different purposes, in total we estimate 28 fuses per PTA. (TODO: explain this in more detail). This leads to `28 * 18 = 504` bits per function block.

### Macro cells

The Macrocell useys 4 fuses for set / reset, and 4 fuses for clock + 2 for clock invert.
2 fuses are used to bypass the ff, 3 fuses determine the second input of the xor on the ff (1 / 0 / IN).  
1 Fuse determines the type of the ff (D/T) and one the reset value.
This gives us 17 Fuses per Macro cell / 306 per FB.

## IO Blocks

The OE muxes (including the invert select mux) requires 9 fuses for the `XC95144XL` and the `XC95288XL` (they feature 4 global OE signals) and 7 fuses for the smaller devices.

The slew rate select, the user pogrammable ground feature are presumably using 1 fuse each.

The total amount of fuses for one IOB is 9-11.  
For the `XC9572XL-TQ100` this equals to `72 * 9` = 648 of 46656 and thus 1% of the total amount of fuses.

# Conclusion / Progress

The above fuse definitions leave 1728 of the 46656 Fuses of a `XC9572XL-TQ100` unexplained. Incidentially `1728` factors into `18 * 4 * 24` so we could be missing `24` bits per macrocell. 

Furthermore it is possible to store a 4 letter ascii usercode in the bitstream / device. Assuming `8` bits per letter this needs `32` fuses.
