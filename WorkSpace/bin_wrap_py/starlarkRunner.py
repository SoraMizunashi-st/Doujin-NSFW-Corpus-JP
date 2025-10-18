# starrun.py
import sys
from starlark.eval import Starlark

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python starrun.py <starlark_file.star>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # ファイル内のコードを実行（評価）する
        # ここでは、組み込みの 'print' 関数などが使える環境で実行される
        Starlark.eval(code)

    except Exception as e:
        print(f"ERROR executing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
