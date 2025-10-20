import pandas as pd
import MeCab
import sys
import os
import site

# 辞書構造に基づいたインデックス定義
ID_COL = 0
HIRAGANA_COL = 2 
KANJI_COL = 4 
# ご提示のCSV構造: ..., count(17), 品詞分類(18), サブ分類(19), ...
POS_COL = 18 

def get_ipadic_path():
    """pip installしたipadicの辞書ディレクトリパスを取得する"""
    # サイトパッケージディレクトリとユーザーサイトパッケージディレクトリを取得
    site_packages = site.getsitepackages()
    all_site_dirs = site_packages + [site.getusersitepackages()]
    
    for site_dir in all_site_dirs:
        # MeCabが期待する辞書の実体（dicdir）のパスを生成
        ipadic_dicdir = os.path.join(site_dir, 'ipadic', 'dicdir')
        
        if os.path.isdir(ipadic_dicdir):
            return ipadic_dicdir 
    return ""

def analyze_and_insert_pos(file_path):
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return

    # 1. 辞書ファイルの読み込み
    try:
        # 'newline='': Windows環境で余分な改行コードの自動変換を防ぐ
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            header_line = f.readline().strip() # 末尾の改行を削除
            data_lines = f.readlines()
        
        from io import StringIO
        # データ行を読み込む
        df = pd.read_csv(StringIO(''.join(data_lines)), header=None, encoding='utf-8', sep=',', engine='python')
        
        # ヘッダーをカンマで分割
        header = header_line.split(',')
        
    except Exception as e:
        print(f"エラー: CSVファイルの読み込み中に問題が発生しました: {e}")
        return

    # ----------------------------------------------------
    # 2. MeCabの準備と処理ロジック 
    # ----------------------------------------------------
    try:
        ipadic_path = get_ipadic_path()
        
        if ipadic_path:
            # IPADIC辞書を指定して初期化
            mecab_args = f"-d \"{ipadic_path}\" -r nul" 
            tagger = MeCab.Tagger(mecab_args)
            print(f"MeCab: IPADIC 辞書実体パス ({os.path.basename(ipadic_path)}) を使用して初期化しました。")
        else:
            # デフォルト辞書で初期化
            tagger = MeCab.Tagger() 
            print("MeCab: デフォルト辞書（IPADICパスが見つからなかったため）を使用して初期化しました。")
            
    except Exception as e:
        print(f"致命的なエラー: MeCabの初期化に失敗しました。")
        print(f"エラー詳細: {e}") 
        return

    def get_pos(word):
        """
        与えられた単語をMeCabで解析し、ルールに従って品詞または <UnBasic> を返す
        """
        if pd.isna(word) or word == "":
            return "<Empty>"
        
        # MeCabの解析結果をノードとして取得
        node = tagger.parseToNode(str(word))
        
        # 最初のノード（BOS/BOS-E）をスキップ
        node = node.next
        
        if node is None or node.surface == "":
             return "<UnBasic>" # 解析失敗
        
        # ノードが一つで終わり、次のノードがEOSであるかを確認
        if node.next and node.next.surface == "":
            features = node.feature.split(',')
            pos = features[0] # 品詞を取得
            return pos
        
        # 複数語に分割された、または解析不能な場合
        return "<UnBasic>" 
    
    # ----------------------------------------------------
    # 3. 品詞の解析とデータフレームへの挿入/上書き
    # ----------------------------------------------------
    
    # データフレームの列数がPOS_COL(18)よりも少ない場合、不足分の列をNaNで追加
    current_cols = df.shape[1]
    if current_cols <= POS_COL:
        # headerの長さまで列を拡張
        max_cols = max(POS_COL + 1, len(header))
        for i in range(current_cols, max_cols):
            df[i] = None # 不足している列をNaNで埋める
    
    # 品詞の結果を一時的に格納するための列を準備
    temp_pos_col_name = 'TEMP_POS_RESULT'
    df[temp_pos_col_name] = "<Empty>" # デフォルト値

    for index, row in df.iterrows():
        target_word = None
        
        # KANJI_COL (4) に漢字があれば優先
        if len(row) > KANJI_COL and not pd.isna(row[KANJI_COL]):
            target_word = str(row[KANJI_COL]).strip()
        # HIRAGANA_COL (2) を使用
        elif len(row) > HIRAGANA_COL and not pd.isna(row[HIRAGANA_COL]):
            target_word = str(row[HIRAGANA_COL]).strip()
        
        if target_word:
            df.at[index, temp_pos_col_name] = get_pos(target_word)

    # 既存の品詞分類カラム(インデックス18)を、新しい結果で上書きする
    df[POS_COL] = df[temp_pos_col_name]
    
    # 一時的に作成した列を削除
    df = df.drop(columns=[temp_pos_col_name])

    # ----------------------------------------------------
    # 4. ファイルの書き出し (空白行対策とデータの保全)
    # ----------------------------------------------------
    try:
        # ヘッダー行を結合し、末尾に改行を一つだけ追加
        header_line_out = ','.join(header) + '\n'
        
        # データフレームをCSV形式の文字列として取得
        # 'line_terminator' 引数を削除しました
        csv_data = df.to_csv(
            header=False, 
            index=False, 
            encoding='utf-8' 
        )
        
        # ヘッダーとデータを結合して上書き保存
        # Pythonのopen関数に newline="" を指定することで、
        # Windows環境でのCRLF二重挿入を防ぐ（これが最後の修正点です）
        with open(file_path, 'w', encoding='utf-8', newline='') as outfile:
            outfile.write(header_line_out)
            outfile.write(csv_data)
            
        print(f"✅ 処理が完了しました。ファイルが上書きされました: {file_path}")
        print(f"👉 品詞分類 (インデックス {POS_COL}) のみがMeCab解析結果で更新されました。")
        print("👉 その他の列（カウント、サブ分類、ライセンス等）は保持されています。")
        
    except Exception as e:
        print(f"エラー: ファイルの書き込み中に問題が発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python DicCategoryzer.py [ファイルパス]")
    else:
        file_path = sys.argv[1]
        analyze_and_insert_pos(file_path)