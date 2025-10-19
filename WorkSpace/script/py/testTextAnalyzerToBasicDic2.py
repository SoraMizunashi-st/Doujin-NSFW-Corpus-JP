import csv
import sys
from collections import defaultdict
import os

def count_words_and_accumulate(dictionary_path, text_path):
    """
    辞書ファイル内の単語の出現回数をテキストファイルでカウントし、
    結果を既存の辞書ファイルの6番目の要素（インデックス5）に加算して上書き保存する。

    Args:
        dictionary_path (str): カウント対象の単語リストを含むCSVファイルのパス（上書きされる）。
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

    # 2. 辞書ファイルの読み込みと単語リストの準備
    id_to_words = defaultdict(list)
    word_to_id = {}
    original_rows = []
    existing_counts = {}
    
    # カウント列のインデックスは 5 (6番目の要素)
    COUNT_COLUMN_INDEX = 15 

    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            header_out = header

            for row in reader:
                # 少なくともID、Category、hiragana, katakana, kanji, COUNTの6要素が必要
                if len(row) < 6:
                    original_rows.append(row)
                    continue

                id_val = row[0].strip()
                
                # 既存のカウント値を取得（インデックス5）
                try:
                    existing_count = int(row[COUNT_COLUMN_INDEX].strip() or 0)
                except (ValueError, IndexError):
                    existing_count = 0  # 6要素目がない、または数字でない場合は0とする
                
                existing_counts[id_val] = existing_count
                original_rows.append(row) # 元の行データを保持

                # ターゲットとなる単語 (hiragana: row[2], katakana: row[3], kanji: row[4])
                # インデックス 2, 3, 4 の3つのみを単語として取得
                words = [word.strip() for word in row[2:5] if word.strip()]
                
                if id_val and words:
                    id_to_words[id_val].extend(words)
                    for word in words:
                        word_lower = word.lower()
                        # 重複する単語は最初に登録されたIDを使用
                        if word_lower not in word_to_id:
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

    all_target_words = list(word_to_id.keys())

    # 3. テキストファイルの読み込み
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        text_lower = text.lower()
    except Exception as e:
        print(
            f"エラー: テキストファイルの読み込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 4. ターゲット単語の出現回数をIDごとにカウント
    new_counts = defaultdict(int)

    for target_word_lower in all_target_words:
        target_id = word_to_id[target_word_lower]
        # 単純な文字列検索でカウント
        count = text_lower.count(target_word_lower)
        if count > 0:
            new_counts[target_id] += count

    # 5. 結果を既存の辞書ファイルに加算して上書き保存
    try:
        with open(dictionary_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            
            # ヘッダーの書き出し
            if header_out:
                writer.writerow(header_out)
            
            # 元のデータに行ごとに新しいカウント結果を加算して書き出す
            for row in original_rows:
                if not row or len(row) < COUNT_COLUMN_INDEX:
                    writer.writerow(row) # 6要素未満の行はそのまま出力
                    continue
                
                id_val = row[0].strip()
                
                # 新しいファイルでのカウント結果を取得
                current_file_count = new_counts.get(id_val, 0)
                
                # 既存のカウント値を取得
                existing_count = existing_counts.get(id_val, 0)
                
                # 累積カウントを計算
                total_count = existing_count + current_file_count

                # 元の行のインデックス5（6番目の要素）を、累積カウントで置き換える
                new_row = list(row) # リストに変換して値を変更可能にする
                new_row[COUNT_COLUMN_INDEX] = str(total_count)
                
                writer.writerow(new_row)

    except Exception as e:
        print(
            f"エラー: 結果ファイルの書き出し中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 完了メッセージ
    print("-" * 30)
    print(f"✅ 集計値の**累積加算**が完了しました。")
    print(f"辞書ファイル: {os.path.basename(dictionary_path)} （6要素目/COUNT列を上書き）")
    print(f"ターゲットテキスト: {os.path.basename(text_path)}")
    print("-" * 30)


if __name__ == "__main__":
    # 引数のチェック: <辞書ファイルパス> <テキストファイルパス>
    if len(sys.argv) != 3:
        print(
            f"使用方法: python {sys.argv[0]} <辞書CSVファイル（上書きされます）> <ターゲットテキストファイル>",
            file=sys.stderr,
        )
        sys.exit(1)

    dictionary_path = sys.argv[1]
    text_path = sys.argv[2]

    # メイン処理の実行
    count_words_and_accumulate(dictionary_path, text_path)