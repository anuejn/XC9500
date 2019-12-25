from util import tmpfile, exec, args, cat
import tempfile


def prj_file(vhdl_file):
    return tmpfile("vhdl work {vhdl_file}".format(vhdl_file=vhdl_file), suffix=".prj")


def xst_file(prj_file, top, output):
    return tmpfile("""
        set -tmpdir "{tmpdir}"
        set -xsthdpdir "xst"
        run
        -ifn {prj_file}
        -ofn {output}
        -ifmt mixed
        -ofmt NGC
        -p xc9500xl
        -top {top}
        -opt_mode Speed
        -opt_level 1
        -iuc NO
        -keep_hierarchy Yes
        -netlist_hierarchy As_Optimized
        -rtlview Yes
        -hierarchy_separator /
        -bus_delimiter <>
        -case Maintain
        -verilog2001 YES
        -fsm_extract YES -fsm_encoding Auto
        -safe_implementation No
        -mux_extract Yes
        -resource_sharing YES
        -iobuf YES
        -pld_mp YES
        -pld_xp YES
        -pld_ce YES
        -wysiwyg YES
        -equivalent_register_removal YES
    """.format(tmpdir=tempfile.gettempdir(), prj_file=prj_file, top=top, output=output), suffix=".xst")


def xst(vhdl_file, top):
    # xst -intstyle ise -ifn /root/ise_test/test/fadd.xst -ofn /root/ise_test/test/fadd.syr
    synth_result = vhdl_file.replace(".vhd", ".ngc")
    exec(
        "xst", args(
        intstyle="ise",
        ifn=xst_file(prj_file(vhdl_file), top, synth_result.replace(".ngc", "")))
    )
    return synth_result


def ngdbuild(device, ngc_file, ucf_file):
    # example: ngdbuild -intstyle ise -dd _ngo -uc fadd.ucf -p $DEVICE fadd.ngc fadd.ngd
    ngd_file = tmpfile(hash_seed=ngc_file+ucf_file+device, suffix=".ngd")
    exec(
        "ngdbuild", args(
        ngc_file,
        ngd_file,
        intstyle="ise",
        dd="_ngo",
        uc=ucf_file,
        p=device,)
    )
    return ngd_file


def cpldfit(device, ngd_file):
    # cpldfit -intstyle ise -p $DEVICE -ofmt vhdl -optimize speed -htmlrpt -loc on -slew fast -init low -inputs 54 -pterms 50 -unused float -power std -terminate keeper fadd.ngd -wysiwyg

    exec("cpldfit", working_dir=tempfile.gettempdir(), args=args(
         "-wysiwyg",
         "-htmlrpt",
         ngd_file,
         intstyle="ise",
         p=device,
         ofmt="vhdl",
         loc="on",
         slew="fast",
         init="low",
         inputs="54",
         pterms="50",
         unused="float",
         power="std",
         terminate="keeper",)
         )

    return ngd_file.replace(".ngd", ".vm6")


def hprep6(label, vm6_file):
    # example: hprep6 -s IEEE1149 -n fadd -i fadd

    exec("hprep6", working_dir=tempfile.gettempdir(), args=args(
        s="IEEE1149",
        n=label,
        i=vm6_file
    ))

    return vm6_file.replace(".vm6", ".jed")


def synth(device, vhdl, ucf, label="test"):
    synth_result = xst(tmpfile(vhdl, suffix=".vhd"), "passthrough")
    ndg_file = ngdbuild(ngc_file=synth_result, device=device, ucf_file=tmpfile(ucf, suffix=".ucf"))
    fit_result = cpldfit(ngd_file=ndg_file, device=device)
    jedec = hprep6(vm6_file=fit_result, label=label)
    return cat(jedec)
