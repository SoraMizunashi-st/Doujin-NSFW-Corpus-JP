import csv
import sys
from collections import defaultdict
import os

def count_words_and_accumulate(dictionary_path, text_path):
    """
    辞書ファイル内の単語の出現回数をテキストファイルでカウントし、
    結果を既存の辞書ファイルのCOUNT列（インデックス17）に加算して上書き保存する。
    辞書の最終行にあるメタ情報も全て保持する。

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

    # 辞書構造に基づいたインデックス定義
    # ID: 0, Category: 1, Hiragana: 2, Katakana: 3, Kanji: 4
    # count列のインデックスは 17
    COUNT_COLUMN_INDEX = 17 
    MIN_REQUIRED_COLUMNS = 5 # ID, Category, MTable1(ひらがな), MTable2(カタカナ), MTable3(漢字)

    # 2. 辞書ファイルの読み込みと単語リストの準備
    word_to_id = {}
    original_rows = []
    existing_counts = {}
    header_out = None

    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            if header:
                header_out = header

            for row in reader:
                # 元の行データを保持 (全ての列を維持するため)
                original_rows.append(row) 
                
                # ターゲット単語の取得に必要な列数チェック
                if len(row) < MIN_REQUIRED_COLUMNS:
                    continue

                id_val = row[0].strip()
                
                # 既存のカウント値を取得
                try:
                    # COUNT_COLUMN_INDEXが存在し、整数に変換できるか確認
                    if len(row) > COUNT_COLUMN_INDEX:
                        existing_count = int(row[COUNT_COLUMN_INDEX].strip() or 0)
                    else:
                        existing_count = 0 # カウント列が存在しない場合は 0
                except ValueError:
                    existing_count = 0 
                
                existing_counts[id_val] = existing_count

                # ターゲットとなる単語 (Hiragana: row[2], Katakana: row[3], Kanji: row[4])
                words = [word.strip() for word in row[2:5] if word.strip()]
                
                if id_val and words:
                    for word in words:
                        word_lower = word.lower()
                        # 重複する単語は最初に登録されたIDを使用 (語彙としてのカウントは1回)
                        if word_lower not in word_to_id:
                            word_to_id[word_lower] = id_val

    except Exception as e:
        print(
            f"エラー: 辞書ファイルの読み込み中に問題が発生しました: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not word_to_id:
        print("警告: 辞書ファイルに有効な単語が含まれていません。", file=sys.stderr)
        # 有効な単語がなくても、ヘッダーと元の行を書き出すために処理を継続
        pass 

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

    # 辞書内の全てのターゲット単語をテキスト内で検索
    # NOTE: これは単純な文字列検索（SubString Match）であり、
    # 厳密な単語境界を考慮していません。
    for target_word_lower in all_target_words:
        target_id = word_to_id[target_word_lower]
        count = text_lower.count(target_word_lower)
        if count > 0:
            # 複数の表記(ひらがな/カタカナ/漢字)が同じIDを持つ場合、カウントを加算
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
                # 行が短すぎる場合はそのまま出力し、メタ情報は消さない
                if not row or len(row) <= COUNT_COLUMN_INDEX:
                    writer.writerow(row) 
                    continue
                
                id_val = row[0].strip()
                
                # 新しいファイルでのカウント結果を取得
                current_file_count = new_counts.get(id_val, 0)
                
                # 既存のカウント値を取得
                existing_count = existing_counts.get(id_val, 0)
                
                # 累積カウントを計算
                total_count = existing_count + current_file_count

                # 元の行をリストに変換して値を変更
                new_row = list(row) 
                
                # インデックス17のカウント列を、累積カウントで置き換える
                # ※インデックス18以降の全てのメタ情報はそのまま保持されます
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
    print(f"辞書ファイル: {os.path.basename(dictionary_path)} （COUNT列[インデックス{COUNT_COLUMN_INDEX}]を上書き、メタ情報保持）")
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