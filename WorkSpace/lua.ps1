#!/usr/bin/env powershell
# run-lua.ps1

# Lua実行ファイル (lua.exe) のディレクトリを定義
# $PSScriptRoot は、このスクリプトファイルが置かれているディレクトリを指します
$LuaBinDir = ".\bin\Lua\"

# Lua実行ファイルの完全パスを構築
$LuaExePath = Join-Path -Path $LuaBinDir -ChildPath "lua.exe"

# 1番目の引数は実行するLuaスクリプトのファイルパス
$ScriptFile = $args[0]

# 2番目以降の引数を取得し、Luaスクリプトに渡す
# @($args)[1..($args.Length - 1)] で、最初の引数を除いた残りの引数を取得します
$ScriptArgs = @($args)[1..($args.Length - 1)]

# Luaインタープリタを実行し、スクリプトファイルとその引数を渡す
# & はPowerShellで外部コマンドを実行するための演算子です
& $LuaExePath $ScriptFile $ScriptArgs