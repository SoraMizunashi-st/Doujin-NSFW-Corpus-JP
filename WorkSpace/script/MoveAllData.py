import sys
import os
import shutil


def move_all_files(source_dir, destination_dir):
    """
    ソースディレクトリ内のすべてのファイルとディレクトリを
    デスティネーションディレクトリに移動する。
    """
    # 1. ディレクトリの存在チェック
    if not os.path.exists(source_dir):
        print(
            f"エラー: ソースディレクトリが見つかりません: {source_dir}", file=sys.stderr
        )
        sys.exit(1)

    # 2. デスティネーションディレクトリの作成（存在しない場合）
    if not os.path.exists(destination_dir):
        try:
            os.makedirs(destination_dir)
            print(f"デスティネーションディレクトリを作成しました: {destination_dir}")
        except OSError as e:
            print(
                f"エラー: デスティネーションディレクトリの作成に失敗しました: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    print("-" * 40)
    print(f"移動元: {source_dir}")
    print(f"移動先: {destination_dir}")
    print("-" * 40)

    moved_count = 0

    # 3. ソースディレクトリ内の全エントリを処理
    try:
        # scandirはディレクトリ内のエントリ（ファイル/ディレクトリ）のイテレータを返す
        with os.scandir(source_dir) as entries:
            for entry in entries:
                source_path = os.path.join(source_dir, entry.name)
                destination_path = os.path.join(destination_dir, entry.name)

                # 移動実行 (ファイルとディレクトリの両方を shutil.move で処理可能)
                shutil.move(source_path, destination_path)
                print(f" -> 移動完了: {entry.name}")
                moved_count += 1

    except Exception as e:
        print(f"エラー: ファイルの移動中に問題が発生しました: {e}", file=sys.stderr)
        # エラーが発生しても移動が完了したファイルはそのまま
        sys.exit(1)

    print("-" * 40)
    print("✅ すべてのファイル/ディレクトリの移動が完了しました。")
    print(f"  合計移動数: {moved_count} エントリ")
    print("-" * 40)


if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) != 3:
        print(
            f"使用方法: python {sys.argv[0]} <移動元ディレクトリ> <移動先ディレクトリ>",
            file=sys.stderr,
        )
        sys.exit(1)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    # メイン処理の実行
    move_all_files(source_dir, destination_dir)
