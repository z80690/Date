# -*- coding: utf-8 -*-
# ruff: noqa — 本脚本跑在 Ghidra 内置 Jython 2.7 里（getScriptArgs/currentProgram
# 由 Ghidra 注入，ruff 的 F821 属误报），不进 Date 工作流运行时。
# Ghidra 无头反编译导出脚本（Jython 2.7，Ghidra 内置解释器执行）。
# 由 ghidra_adapter.py 通过 -postScript 调用，不在 Date 工作流进程内跑。
# 用法: -postScript dump_functions.py <输出json路径> [最大函数数]
# 职责：枚举函数 + 逐个反编译成 C 伪码，落 JSON 供适配层归一。

import json

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

args = getScriptArgs()
out_path = args[0]
max_funcs = int(args[1]) if len(args) > 1 else 40

monitor = ConsoleTaskMonitor()
decomp = DecompInterface()
decomp.openProgram(currentProgram)

funcs = list(currentProgram.getFunctionManager().getFunctions(True))[:max_funcs]
results = []
for f in funcs:
    item = {
        "name": f.getName(),
        "entry": str(f.getEntryPoint()),
        "size_bytes": int(f.getBody().getNumAddresses()),
    }
    try:
        res = decomp.decompileFunction(f, 30, monitor)
        if res.decompileCompleted():
            item["decompiled_c"] = res.getDecompiledFunction().getC()
        else:
            item["decompiled_c"] = None
            item["decompile_error"] = str(res.getErrorMessage())
    except Exception as e:  # noqa: BLE001 - 单函数失败不断链
        item["decompiled_c"] = None
        item["decompile_error"] = str(e)
    results.append(item)

payload = {
    "program": currentProgram.getName(),
    "language_id": str(currentProgram.getLanguageID()),
    "function_count": len(results),
    "functions": results,
}
with open(out_path, "w") as fh:
    json.dump(payload, fh)
print("GHIDRA_DUMP_OK " + out_path)
