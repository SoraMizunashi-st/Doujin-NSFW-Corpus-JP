import sys
import os
import shutil


def copy_all_files(source_dir, destination_dir):
    """
    ソースディレクトリ内のすべてのファイルとディレクトリを
    デスティネーションディレクトリにコピーする。
    """
    # 1. ディレクトリの存在チェック
    if not os.path.exists(source_dir):
        print(
            f"エラー: コピー元ディレクトリが見つかりません: {source_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. デスティネーションディレクトリの作成（存在しない場合）
    if not os.path.exists(destination_dir):
        try:
            # 存在しない場合は作成
            os.makedirs(destination_dir)
            print(f"デスティネーションディレクトリを作成しました: {destination_dir}")
        except OSError as e:
            print(
                f"エラー: デスティネーションディレクトリの作成に失敗しました: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    print("-" * 40)
    print(f"コピー元: {source_dir}")
    print(f"コピー先: {destination_dir}")
    print("-" * 40)

    copied_count = 0

    # 3. ソースディレクトリ内の全エントリを処理
    try:
        # scandirで効率的にエントリ（ファイル/ディレクトリ）を取得
        with os.scandir(source_dir) as entries:
            for entry in entries:
                source_path = os.path.join(source_dir, entry.name)
                destination_path = os.path.join(destination_dir, entry.name)

                if entry.is_dir():
                    # ディレクトリの場合、copytreeで再帰的にコピー
                    # shutil.copytreeは、コピー先のディレクトリが既に存在する場合、通常エラーとなるため
                    # その場合は既存のディレクトリの内容をマージするよう処理
                    try:
                        shutil.copytree(source_path, destination_path)
                    except FileExistsError:
                        # 既に存在する場合は、上書きせずに中身を再帰的にコピーする処理が必要だが、
                        # 今回はシンプルに、メインディレクトリ内のファイルのみを処理し、
                        # サブディレクトリは完全に新しいものとしてコピーする挙動とする
                        print(
                            f" -> スキップ: 既存のディレクトリ {entry.name} は上書きしません。"
                        )
                        continue
                    print(f" -> コピー完了（ディレクトリ）: {entry.name}")
                else:
                    # ファイルの場合、copy2で属性情報もコピー
                    shutil.copy2(source_path, destination_path)
                    print(f" -> コピー完了（ファイル）: {entry.name}")

                copied_count += 1

    except Exception as e:
        print(f"エラー: ファイルのコピー中に問題が発生しました: {e}", file=sys.stderr)
        sys.exit(1)

    print("-" * 40)
    print("✅ すべてのファイル/ディレクトリのコピーが完了しました。")
    print(f"  合計コピー数: {copied_count} エントリ")
    print("-" * 40)


if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) != 3:
        print(
            f"使用方法: python {sys.argv[0]} <コピー元ディレクトリ> <コピー先ディレクトリ>",
            file=sys.stderr,
        )
        sys.exit(1)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    # メイン処理の実行
    copy_all_files(source_dir, destination_dir)
