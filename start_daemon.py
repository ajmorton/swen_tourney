import util.funcs
import daemon.main

if __name__ == "__main__":
    util.funcs.assert_python_version(3, 5, 2)
    daemon.main.main()
