import ops
import iopc

TARBALL_FILE="libxkbcommon-0.8.0.tar.xz"
TARBALL_DIR="libxkbcommon-0.8.0"
INSTALL_DIR="libxkbcommon-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_usr_local_share_dir
    global selected_wayland
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_usr_local_share_dir = ops.path_join(install_dir, "usr/local/share")
    selected_wayland = False

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    #extra_conf.append("--extra-cflags=" + cflags)
    #extra_conf.append("--extra-ldflags=" + libs)

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--disable-docs")
    extra_conf.append("--disable-x11")
    if selected_wayland :
        extra_conf.append("--enable-wayland")
    else:
        extra_conf.append("--disable-wayland")
    #extra_conf.append("--with-x-locale-root=/usr/local/share/X11/locale")
    #extra_conf.append('WAYLAND_CFLAGS=' + cflags)
    #extra_conf.append('WAYLAND_LIBS=' + libs)
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)

    src_lib_dir = ops.path_join(install_tmp_dir, "usr/local/lib/")
    lib_so = "libxkbcommon.so.0.0.0"
    ops.copyto(ops.path_join(src_lib_dir, lib_so), dst_lib_dir)
    ops.ln(dst_lib_dir, lib_so, "libxkbcommon.so.0.0")
    ops.ln(dst_lib_dir, lib_so, "libxkbcommon.so.0")
    ops.ln(dst_lib_dir, lib_so, "libxkbcommon.so")

    rules_dir = ops.path_join(dst_usr_local_share_dir, "X11/xkb/rules")
    ops.mkdir(rules_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/rules/evdev"), rules_dir)

    keycodes_dir = ops.path_join(dst_usr_local_share_dir, "X11/xkb/keycodes")
    ops.mkdir(keycodes_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/keycodes/evdev"), keycodes_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/keycodes/aliases"), keycodes_dir)

    types_dir = ops.path_join(dst_usr_local_share_dir, "X11/xkb/types")
    ops.mkdir(types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/complete"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/basic"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/extra"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/iso9995"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/level5"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/mousekeys"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/numpad"), types_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/types/pc"), types_dir)

    compat_dir = ops.path_join(dst_usr_local_share_dir, "X11/xkb/compat")
    ops.mkdir(compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/complete"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/basic"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/iso9995"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/mousekeys"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/accessx"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/misc"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/xfree86"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/level5"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/caps"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/ledcaps"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/lednum"), compat_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/compat/ledscroll"), compat_dir)

    symbols_dir = ops.path_join(dst_usr_local_share_dir, "X11/xkb/symbols")
    ops.mkdir(symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/pc"), symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/srvr_ctrl"), symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/keypad"), symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/altwin"), symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/us"), symbols_dir)
    ops.copyto(ops.path_join(tarball_dir, "test/data/symbols/inet"), symbols_dir)

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)
    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(dst_lib_dir, "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_share_dir, "."), "usr/local/share")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    iopc.add_includes(cflags)

    libs = ""
    libs += " -lxkbcommon"
    iopc.add_libs(libs)

    return False

def MAIN_DEPS(args):
    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

