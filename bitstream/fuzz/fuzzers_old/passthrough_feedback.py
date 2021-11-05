def fuzz(device):
    def fb_mc(n):
        return f"FB{n // 18 + 1}_{n % 18 + 1}"

    for from_loc in range(288):
        for to_loc in range(1,3):
            VHDL = """
                library IEEE;
                use IEEE.STD_LOGIC_1164.ALL;
                library unisim;
                use UNISIM.vcomponents.ALL;

                entity passthrough is
                    Port ( output : out  STD_LOGIC; input: in STD_LOGIC);
                end passthrough;

                architecture Behavioral of passthrough is
                    signal Q: STD_LOGIC;
                begin
                    FDCE_inst: FDCE
                    generic map (
                        INIT => '0'
                    )
                    port map (
                    Q => Q,
                    C => '0',
                    CE => '0',
                    CLR => '0',
                    D => input
                    );

                    output <= not Q;
                end Behavioral;
            """
            UCF = f"""
                NET "input" LOC="{fb_mc(from_loc)}"; NET "output"  LOC = "{fb_mc(to_loc)}"; INST "FDCE_inst" KEEP=TRUE; INST "FDCE_inst" LOC="{fb_mc(from_loc)}";
            """

            tags = ["feedback_full", f"feedback72_from_{fb_mc(from_loc)}_to_{fb_mc(to_loc)}"]

            yield VHDL, UCF, tags
#this one is a good one
# def fuzz(device):
#     def fb_mc(n):
#         return f"FB{n // 18 + 1}_{n % 18 + 1}"
#
#     for from_loc in range(36):
#         for to_loc in range(36):
#             VHDL = """
#                 library IEEE;
#                 use IEEE.STD_LOGIC_1164.ALL;
#                 library unisim;
#                 use UNISIM.vcomponents.ALL;
#
#                 entity passthrough is
#                     Port ( output : out  STD_LOGIC; input: in STD_LOGIC);
#                 end passthrough;
#
#                 architecture Behavioral of passthrough is
#                     signal Q: STD_LOGIC;
#                 begin
#                     FDCE_inst: FDCE
#                     generic map (
#                         INIT => '0'
#                     )
#                     port map (
#                     Q => Q,
#                     C => '0',
#                     CE => '0',
#                     CLR => '0',
#                     D => input
#                     );
#
#                     output <= not Q;
#                 end Behavioral;
#             """
#             UCF = f"""
#                 NET "input" LOC="{fb_mc(from_loc)}"; NET "output"  LOC = "{fb_mc(to_loc)}"; INST "FDCE_inst" KEEP=TRUE; INST "FDCE_inst" LOC="{fb_mc(from_loc)}";
#             """
#
#             tags = ["feedback_full", f"feedback_from_{fb_mc(from_loc)}_to_{fb_mc(to_loc)}"]
#
#             yield VHDL, UCF, tags

# def fuzz(device):
#     for a in range(1, 3):
#         for b in range(1, 3):
#             for n in range(1, 3):
#                 for m in range(1, 3):
#                     VHDL = """
#                         library IEEE;
#                         use IEEE.STD_LOGIC_1164.ALL;
#                         library unisim;
#                         use UNISIM.vcomponents.ALL;
#
#                         entity passthrough is
#                             Port ( output : out  STD_LOGIC; input: in STD_LOGIC);
#                         end passthrough;
#
#                         architecture Behavioral of passthrough is
#                           signal Q: STD_LOGIC;
#                         begin
#                           FDCE_inst: FDCE
#                           generic map (
#                               INIT => '0'
#                           )
#                           port map (
#                             Q => Q,
#                             C => '0',
#                             CE => '0',
#                             CLR => '0',
#                             D => input
#                           );
#
#                           FDCE_inst2: FDCE
#                           generic map (
#                               INIT => '0'
#                           )
#                           port map (
#                             Q => output,
#                             C => '0',
#                             CE => '0',
#                             CLR => '0',
#                             D => Q
#                           );
#                         end Behavioral;
#                     """
#                     UCF = """
#                         NET "input" LOC="FB2_18"; NET "output"  LOC = "FB{}_{}"; INST "FDCE_inst" KEEP=TRUE; INST "FDCE_inst" LOC=FB{}_{}; INST "FDCE_inst2" LOC=FB{}_{}; INST "FDCE_inst2" KEEP=TRUE;
#                     """
#
#                     tags = ["feedback_full", "feedback_from_FB{}_{}_to_FB{}_{}".format(b,m,a,n)]
#
#                     yield VHDL, UCF.format(b,m,a,n,b,m,a,n), tags
