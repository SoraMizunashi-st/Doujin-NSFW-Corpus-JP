local io = require("io")
local os = require("os")
local string = require("string")

-- パス操作のための補助関数 (Lua標準機能を使用)
local function get_output_path(input_path)
    -- 拡張子のインデックスを見つける (最後のドット)
    local dot_index = string.match(input_path, ".*()%.[^/\\]*$")
    
    local base, ext
    if dot_index then
        -- ドット以前の部分 (ベース名)
        base = string.sub(input_path, 1, dot_index - 1)
        -- ドット以降の部分 (拡張子)
        ext = string.sub(input_path, dot_index)
    else
        -- 拡張子がない場合
        base = input_path
        ext = ""
    end
    
    -- 出力ファイル名を作成: base + "_org" + ext
    return base .. "_org" .. ext
end

local function remove_empty_lines(input_path)
    -- 1. パスの確認と出力ファイル名の決定
    
    -- ファイルが存在するかどうかをチェック (io.openの失敗で代用)
    local f = io.open(input_path, "r")
    if not f then
        io.stderr:write(string.format("エラー: 入力ファイルが見つかりません: %s\n", input_path))
        os.exit(1)
    end
    f:close()

    local output_path = get_output_path(input_path)

    -- 2. ファイルの読み込みと空白行の除去
    local cleaned_lines = {}
    local line_count = 0
    local status, err = pcall(function()
        for line in io.lines(input_path) do
            -- 行の先頭と末尾の空白（スペース、タブ、CR/LFなど）を除去
            -- ^%s*(.*)%s*$ のパターンで行頭と行末の空白を除去
            local stripped_line = string.gsub(line, "^%s*(.*)%s*$", "%1")
            
            -- 空でなければリストに追加
            if string.len(stripped_line) > 0 then
                line_count = line_count + 1
                cleaned_lines[line_count] = stripped_line
            end
        end
    end)
    
    if not status then
        io.stderr:write(string.format("エラー: ファイルの読み込み中に問題が発生しました: %s\n", err))
        os.exit(1)
    end

    -- 3. クリーンアップされた行を新しいファイルに書き出し
    local outfile_status, outfile_err = pcall(function()
        local outfile = io.open(output_path, "w")
        if not outfile then
             error("ファイルを開けません") -- pcallで捕捉されるエラーを発生させる
        end
        
        -- 各行を改行文字で結合して書き込み
        local content = table.concat(cleaned_lines, "\n")
        outfile:write(content)
        outfile:close()
    end)

    if not outfile_status then
        io.stderr:write(string.format("エラー: 出力ファイルへの書き込み中に問題が発生しました: %s\n", outfile_err))
        os.exit(1)
    end

    -- 4. 結果の出力
    local processed_count = #cleaned_lines
    io.write(string.rep("-", 40) .. "\n")
    io.write("✅ 空白行の除去が完了しました。\n")
    io.write(string.format("  入力ファイル: %s\n", input_path))
    io.write(string.format("  出力ファイル: %s\n", output_path))
    io.write(string.format("  処理された行数: %d行\n", processed_count))
    io.write(string.rep("-", 40) .. "\n")
end

-- メイン処理
local args = {...} -- コマンドライン引数を取得 (最初の引数はスクリプト名ではなく次の要素)

-- 引数のチェック
if #args ~= 1 then
    io.stderr:write(string.format("使用方法: lua %s <入力テキストファイルパス>\n", arg[0]))
    os.exit(1)
end

local input_file_path = args[1]

-- メイン関数の実行
remove_empty_lines(input_file_path)