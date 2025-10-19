import sys
import os


def remove_empty_lines(input_path):
    """
    指定されたファイルから空白行を除去し、新しいファイルに保存する。
    出力ファイル名には '_org' サフィックスが付加される。
    """
    # 1. パスの確認と出力ファイル名の決定
    if not os.path.exists(input_path):
        print(f"エラー: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 拡張子を取得
    base, ext = os.path.splitext(input_path)
    # 出力ファイル名は 元のファイル名 + '_org' + 拡張子
    output_path = f"{base}_org{ext}"

    # 2. ファイルの読み込みと空白行の除去
    cleaned_lines = []
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            for line in infile:
                # 行の先頭と末尾の空白（スペース、タブ、改行など）を除去し、
                # 空でなければ（つまり、空白行でなければ）リストに追加
                stripped_line = line.strip()
                if stripped_line:
                    # 元の行の末尾の改行文字は保持せず、strip()後の内容のみを保持
                    cleaned_lines.append(stripped_line)

    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. クリーンアップされた行を新しいファイルに書き出し
    try:
        with open(output_path, "w", encoding="utf-8") as outfile:
            # 各行の間に改行文字 '\n' を挟んで書き込み
            # これにより、オリジナルのファイルにあった空白行が詰まり、
            # 中身のある行だけが連続して書き込まれる
            outfile.write("\n".join(cleaned_lines))

    except Exception as e:
        print(
            f"エラー: 出力ファイルへの書き込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    print("-" * 40)
    print("✅ 空白行の除去が完了しました。")
    print(f"  入力ファイル: {input_path}")
    print(f"  出力ファイル: {output_path}")
    print(f"  処理された行数: {len(cleaned_lines)}行")
    print("-" * 40)


if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) != 2:
        print(
            f"使用方法: python {sys.argv[0]} <入力テキストファイルパス>",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file_path = sys.argv[1]

    # メイン処理の実行
    remove_empty_lines(input_file_path)
