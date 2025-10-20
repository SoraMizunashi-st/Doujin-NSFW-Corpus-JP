import pandas as pd
import MeCab
import sys
import os
import site

def get_ipadic_path():
    """pip installしたipadicの辞書ディレクトリパスを取得する"""
    site_packages = site.getsitepackages()
    # ユーザーサイトパッケージも含むすべてのパッケージディレクトリを確認
    all_site_dirs = site_packages + [site.getusersitepackages()]
    
    for site_dir in all_site_dirs:
        # MeCabが期待する辞書の実体（dicrcが存在する場所）のパスを生成
        ipadic_dicdir = os.path.join(site_dir, 'ipadic', 'dicdir')
        
        if os.path.isdir(ipadic_dicdir):
            # 例: C:\Users\...\ipadic\dicdir を返す
            return ipadic_dicdir 
    return ""

def analyze_and_insert_pos(file_path):
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return

    try:
        # ヘッダなしで読み込み
        df = pd.read_csv(file_path, header=None, encoding='utf-8', sep=',', engine='python')
        
        # CSVの列インデックス
        HIRAGANA_COL = 2 
        KANJI_COL = 4     
        POS_COL = 17  # 18列目 (ご指定の最終的な挿入位置インデックス)
    except Exception as e:
        print(f"エラー: CSVファイルの読み込み中に問題が発生しました: {e}")
        return

    # ----------------------------------------------------
    # 2. MeCabの準備と処理ロジック 
    # ----------------------------------------------------
    try:
        ipadic_path = get_ipadic_path()
        
        if ipadic_path:
            # 辞書パス(-d)と、システム設定ファイル探索のキャンセル(-r nul)を組み合わせる
            mecab_args = f"-d \"{ipadic_path}\" -r nul" 
            
            tagger = MeCab.Tagger(mecab_args)
            print(f"MeCab: IPADIC 辞書実体パス ({ipadic_path}) を使用して初期化しました。引数: {mecab_args}")
        else:
            # パスが見つからない場合は引数なしで試行
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
        node = tagger.parseToNode(str(word))
        node = node.next
        if node is None or node.surface == "":
             return "<UnBasic>" 
        # MeCabが1語として認識せず、次ノードが存在する場合 <UnBasic> を返す
        if node.next and node.next.surface:
            return "<UnBasic>"
        features = node.feature.split(',')
        pos = features[0]
        return pos
    
    # ----------------------------------------------------
    # 安定化の修正: 重複列の削除と挿入
    # ----------------------------------------------------
    new_col_name = 'POS_RESULT' # 一時的な列名

    # 実行のたびに列が増えるのを防ぐため、POS_COL以降の列を削除してから挿入する
    current_cols = df.shape[1]
    
    # POS_COL (17) 以上の列が存在する場合、その列以降を削除
    if current_cols > POS_COL:
        # インデックス17以降の列を削除
        df = df.iloc[:, :POS_COL]
        # print(f"DEBUG: 既存のデータ列数が多いため、インデックス {POS_COL} 以降の列を削除しました。")
        
    # 指定の位置に新しい列を挿入
    df.insert(POS_COL, new_col_name, None)
    
    for index, row in df.iterrows():
        target_word = None
        # 5列目（KANJI_COL: 4）に漢字があれば優先
        if not pd.isna(row[KANJI_COL]):
            target_word = str(row[KANJI_COL]).strip()
        # 3列目（HIRAGANA_COL: 2）を使用
        elif not pd.isna(row[HIRAGANA_COL]):
            target_word = str(row[HIRAGANA_COL]).strip()
        
        if target_word:
            df.at[index, new_col_name] = get_pos(target_word)
        else:
            df.at[index, new_col_name] = "<Empty>"

    try:
        # ヘッダーなし、インデックスなしで保存し、既存ファイルを上書き
        df.to_csv(file_path, header=False, index=False, encoding='utf-8')
        print(f"処理が完了しました。ファイルが上書きされました: {file_path}")
    except Exception as e:
        print(f"エラー: ファイルの書き込み中に問題が発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python DicCategoryzer.py [ファイルパス]")
    else:
        file_path = sys.argv[1]
        analyze_and_insert_pos(file_path)