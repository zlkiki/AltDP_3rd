// ExportTargetFunctions.java
// Ghidra Headless script to export C decompiled pseudocode and metadata for specified target functions/symbols.
//
//@category StructuralDecompile
//@author AltDP_3rd Agent

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class ExportTargetFunctions extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("Usage: ExportTargetFunctions <output_dir> <symbol_patterns_comma_separated> [output_prefix]");
            return;
        }

        String outputDirPath = args[0];
        String symbolPatternsRaw = args[1];
        String outputPrefix = (args.length >= 3 && !args[2].trim().isEmpty()) ? args[2].trim() : "";

        File outDir = new File(outputDirPath);
        if (!outDir.exists()) {
            outDir.mkdirs();
        }

        Set<String> patterns = new HashSet<>();
        for (String p : symbolPatternsRaw.split(",")) {
            String trimmed = p.trim();
            if (!trimmed.isEmpty()) {
                patterns.add(trimmed);
            }
        }

        println("==========================================================");
        println("[AltDP Export] Program: " + currentProgram.getName());
        println("[AltDP Export] Output Dir: " + outDir.getAbsolutePath());
        println("[AltDP Export] Target Patterns: " + patterns);
        println("==========================================================");

        DecompInterface decompiler = new DecompInterface();
        DecompileOptions options = new DecompileOptions();
        decompiler.setOptions(options);
        decompiler.openProgram(currentProgram);

        FunctionManager funcMgr = currentProgram.getFunctionManager();
        SymbolTable symTable = currentProgram.getSymbolTable();

        int matchedCount = 0;
        List<String> metaJsonEntries = new ArrayList<>();
        Set<String> processedAddrs = new HashSet<>();

        // 1. Check existing functions
        FunctionIterator funcs = funcMgr.getFunctions(true);
        while (funcs.hasNext() && !monitor.isCancelled()) {
            Function func = funcs.next();
            String name = func.getName();
            Symbol sym = func.getSymbol();
            String fullName = (sym != null) ? sym.getName(true) : name;

            boolean matches = false;
            for (String p : patterns) {
                if (name.contains(p) || fullName.contains(p) || (sym != null && sym.getName().contains(p))) {
                    matches = true;
                    break;
                }
            }
            if (matches) {
                processedAddrs.add(func.getEntryPoint().toString());
                matchedCount++;
                decompileAndSave(decompiler, func, name, fullName, outDir, outputPrefix, metaJsonEntries);
            }
        }

        // 2. Search Symbols for noanalysis mode
        for (Symbol sym : symTable.getAllSymbols(true)) {
            if (monitor.isCancelled()) break;
            String symName = sym.getName();
            String fullSymName = sym.getName(true);
            boolean matches = false;
            for (String p : patterns) {
                if (symName.contains(p) || fullSymName.contains(p)) {
                    matches = true;
                    break;
                }
            }
            if (!matches) continue;

            String addrStr = sym.getAddress().toString();
            if (processedAddrs.contains(addrStr)) continue;
            processedAddrs.add(addrStr);

            Function func = funcMgr.getFunctionAt(sym.getAddress());
            if (func == null) {
                try {
                    func = createFunction(sym.getAddress(), symName);
                } catch (Exception e) {
                    // Ignore
                }
            }

            if (func != null) {
                matchedCount++;
                decompileAndSave(decompiler, func, symName, fullSymName, outDir, outputPrefix, metaJsonEntries);
            }
        }

        decompiler.dispose();

        // Write meta json
        String jsonFileName = (outputPrefix.isEmpty() ? "export" : outputPrefix) + "_meta.json";
        File jsonFile = new File(outDir, jsonFileName);
        try (PrintWriter pw = new PrintWriter(new FileWriter(jsonFile))) {
            pw.println("{\n  \"program\": \"" + escapeJson(currentProgram.getName()) + "\",");
            pw.println("  \"matched_count\": " + matchedCount + ",");
            pw.println("  \"functions\": [\n" + String.join(",\n", metaJsonEntries) + "\n  ]\n}");
        }

        println("==========================================================");
        println("[AltDP Export] Completed! Matched functions: " + matchedCount);
        println("[AltDP Export] Metadata saved to: " + jsonFile.getAbsolutePath());
        println("==========================================================");
    }

    private void decompileAndSave(
        DecompInterface decompiler,
        Function func,
        String name,
        String fullName,
        File outDir,
        String outputPrefix,
        List<String> metaJsonEntries
    ) {
        println("-> Decompiling matched function: " + name + " @ " + func.getEntryPoint());
        String proto = func.getPrototypeString(true, true);

        DecompileResults results = decompiler.decompileFunction(func, 60, monitor);
        String cCode = "";
        if (results != null && results.decompileCompleted() && results.getDecompiledFunction() != null) {
            cCode = results.getDecompiledFunction().getC();
        } else {
            cCode = "// Decompilation placeholder for " + fullName + "\n" +
                    "// Entry Point: " + func.getEntryPoint() + "\n" +
                    "// Signature: " + proto + "\n";
        }

        String sanitizedName = name.replaceAll("[^a-zA-Z0-9_]", "_");
        String fileName = (outputPrefix.isEmpty() ? "" : (outputPrefix + "_")) + sanitizedName + ".c";
        File cFile = new File(outDir, fileName);

        try (PrintWriter pw = new PrintWriter(new FileWriter(cFile))) {
            pw.println("/*");
            pw.println(" * AltDP_3rd Decompiled Ground Truth Asset");
            pw.println(" * Module: " + currentProgram.getName());
            pw.println(" * Function Name: " + name);
            pw.println(" * Full Symbol: " + fullName);
            pw.println(" * Prototype: " + proto);
            pw.println(" * Entry Point: " + func.getEntryPoint());
            pw.println(" * Extracted At: " + new java.util.Date());
            pw.println(" */\n");
            pw.println(cCode);
        } catch (Exception e) {
            println("Error saving file: " + e.getMessage());
        }

        String metaEntry = String.format(
            "    {\n" +
            "      \"name\": \"%s\",\n" +
            "      \"full_symbol\": \"%s\",\n" +
            "      \"entry_point\": \"%s\",\n" +
            "      \"file\": \"%s\",\n" +
            "      \"prototype\": \"%s\"\n" +
            "    }",
            escapeJson(name),
            escapeJson(fullName),
            escapeJson(func.getEntryPoint().toString()),
            escapeJson(fileName),
            escapeJson(proto)
        );
        metaJsonEntries.add(metaEntry);
    }

    private String escapeJson(String raw) {
        if (raw == null) return "";
        return raw.replace("\\", "\\\\")
                  .replace("\"", "\\\"")
                  .replace("\b", "\\b")
                  .replace("\f", "\\f")
                  .replace("\n", "\\n")
                  .replace("\r", "\\r")
                  .replace("\t", "\\t");
    }
}
