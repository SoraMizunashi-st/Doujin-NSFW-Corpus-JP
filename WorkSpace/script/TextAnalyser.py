import csv
import sys
from collections import Counter
import os


def count_words_from_file(dictionary_path, text_path):
    """
    辞書ファイル内の単語がテキストファイル内で出現した回数をカウントする。

    Args:
        dictionary_path (str): カウント対象の単語リストを含むCSVファイルのパス。
        text_path (str): カウント対象のプレーンテキストファイルのパス。
    """
    # 1. パスの存在確認
    if not os.path.exists(dictionary_path):
        print(
            f"エラー: 辞書ファイルが見つかりません: {dictionary_path}", file=sys.stderr
        )
        sys.exit(1)
    if not os.path.exists(text_path):
        print(f"エラー: テキストファイルが見つかりません: {text_path}", file=sys.stderr)
        sys.exit(1)

    # 2. 辞書ファイルの読み込み (単語を小文字に変換)
    target_words = []
    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                # 1行すべてがターゲット単語なので、リストに追加
                # 大文字・小文字を区別しないため、小文字に変換
                target_words.extend(
                    [word.strip().lower() for word in row if word.strip()]
                )

    except Exception as e:
        print(
            f"エラー: 辞書ファイルの読み込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not target_words:
        print("警告: 辞書ファイルに有効な単語が含まれていません。", file=sys.stderr)
        sys.exit(0)

    # 3. テキストファイルの読み込みと単語の抽出
    word_counts = Counter()
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 大文字・小文字を区別しないため、テキスト全体を小文字に変換
        text_lower = text.lower()

        # 単語を区切るための正規表現 (単語の境界を考慮して抽出)
        # ここでは、英数字以外の文字を区切り文字と見なして単語を抽出しています。
        # 日本語などの区切り文字がない言語では、この後のターゲット単語検索がより正確です。

        # 4. ターゲット単語の出現回数をカウント
        for target_word in target_words:
            # 正規表現でターゲット単語を検索
            # re.escapeで特殊文字をエスケープし、\b (単語の境界) を使用して完全一致を保証
            # ただし、日本語では\bがうまく機能しない場合が多いため、
            # 確実な文字列マッチングを行うことが推奨されます。

            # ここでは、単純な文字列検索でカウントします。
            # 必要に応じて、正規表現や形態素解析を導入して精度を上げてください。
            count = text_lower.count(target_word)

            # カウントがゼロでない場合のみCounterに追加
            if count > 0:
                word_counts[target_word] = count

    except Exception as e:
        print(
            f"エラー: テキストファイルの読み込みまたは処理中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 5. 結果の出力
    print("-" * 30)
    print(f"ターゲットファイル: {os.path.basename(text_path)}")
    print(f"辞書ファイル: {os.path.basename(dictionary_path)}")
    print("-" * 30)

    # 結果をカウント順にソートして出力
    if word_counts:
        # 元の辞書の順番を保ちつつ、カウントされたものだけを出力
        results = [
            (word, word_counts[word]) for word in target_words if word in word_counts
        ]

        # 重複を排除し、カウント順にソート (降順)
        unique_results = sorted(
            list(set(results)), key=lambda item: item[1], reverse=True
        )

        for word, count in unique_results:
            print(f"{word}: {count}回")
    else:
        print("カウントされた単語はありませんでした。")

    print("-" * 30)


if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) != 3:
        print(
            f"使用方法: python {sys.argv[0]} <辞書ファイルパス> <テキストファイルパス>",
            file=sys.stderr,
        )
        sys.exit(1)

    dictionary_path = sys.argv[1]
    text_path = sys.argv[2]

    # メイン処理の実行
    count_words_from_file(dictionary_path, text_path)
