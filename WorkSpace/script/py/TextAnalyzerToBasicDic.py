import csv
import sys
from collections import defaultdict
import os


def count_words_from_file(dictionary_path, text_path):
    """
    辞書ファイル内の単語がテキストファイル内で出現した回数を、IDごとにカウントする。

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

    # 2. 辞書ファイルの読み込み (IDごとに単語リストを生成)
    # {ID: [単語1, 単語2, ...], ...} の形式
    id_to_words = defaultdict(list)
    word_to_id = {}  # 単語からIDへの逆引き用

    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # ヘッダー行をスキップ (ID,Category,hiragana,katakana,kanji)
            header = next(reader, None)

            for row in reader:
                if len(row) < 5:
                    continue  # 不正な行をスキップ

                id_val = row[0].strip()
                # Category(row[1]) は使用しない

                # ターゲットとなる単語 (hiragana, katakana, kanji) を取得
                words = [word.strip() for word in row[2:5] if word.strip()]

                if id_val and words:
                    id_to_words[id_val].extend(words)
                    for word in words:
                        # 単語を小文字に変換して登録 (大文字・小文字を区別しないため)
                        word_lower = word.lower()
                        # 複数IDに同じ単語がある場合、最後に登録されたIDで上書きされるが、
                        # 今回の辞書では単語の重複は少なそうなので許容
                        word_to_id[word_lower] = id_val

    except Exception as e:
        print(
            f"エラー: 辞書ファイルの読み込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not id_to_words:
        print("警告: 辞書ファイルに有効な単語が含まれていません。", file=sys.stderr)
        sys.exit(0)

    # 全てのターゲット単語のリスト
    all_target_words = list(word_to_id.keys())

    # 3. テキストファイルの読み込み
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 大文字・小文字を区別しないため、テキスト全体を小文字に変換
        text_lower = text.lower()

    except Exception as e:
        print(
            f"エラー: テキストファイルの読み込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 4. ターゲット単語の出現回数をIDごとにカウント
    id_counts = defaultdict(int)

    for target_word_lower in all_target_words:
        target_id = word_to_id[target_word_lower]

        # 単純な文字列検索でカウント
        count = text_lower.count(target_word_lower)

        if count > 0:
            id_counts[target_id] += count

    # 5. 結果の出力
    print("-" * 30)
    print(f"ターゲットファイル: {os.path.basename(text_path)}")
    print(f"辞書ファイル: {os.path.basename(dictionary_path)}")
    print("-" * 30)

    # 結果をID順にソートして出力 (IDは文字列として比較されることに注意)
    # データがないIDも出力対象にするため、id_to_wordsのキーを元にループ
    sorted_ids = sorted(id_to_words.keys())

    for id_val in sorted_ids:
        words = id_to_words[id_val]
        count = id_counts.get(id_val, 0)

        # ID, [単語リスト], N回 の形式で出力
        print(f"key : {id_val} {words} {count}回")

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
