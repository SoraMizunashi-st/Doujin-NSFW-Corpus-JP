# Python Data Curation and Organization Tools

This collection consists of four individual Python scripts designed to automate essential tasks for preparing, analyzing, and organizing large language model (LLM) training corpora.

## 🚀 How to Run the Scripts

Each script is executed independently with its own set of arguments.

**General Execution Structure:**
```bash
python <script_name>.py [arguments...]

//------------------------------------------------------------------------------------------------------
# 1) TextAnalyzer.py
//------------------------------------------------------------------------------------------------------

Analyzes a plain text file for the occurrence frequency of words listed in a CSV dictionary. This is crucial for analyzing specialized domain weight and verifying the distribution of synonyms across your corpus. (The search is case-insensitive).

Usage
Bash

python AnakysisWord.py <dictionary_path> <text_path>
# Example: python TextAnalzer.py ./raw/dic.csv ./raw/Raw_sora001.txt

//------------------------------------------------------------------------------------------------------
# 2) TextOrganizer.py
//------------------------------------------------------------------------------------------------------

Removes all blank lines from an input text file and saves the clean content to a new file with an _org suffix. This ensures contextual continuity and produces a clean corpus, especially for dialogue or script data.

Usage
Bash

python TextOrganizer.py <input_file_path>
# Example: python TextOrganizer.py ./data/input.txt
# Output file will be: ./data/input_org.txt

//------------------------------------------------------------------------------------------------------
# 3) MoveAllFiles.py
//------------------------------------------------------------------------------------------------------

Moves (cuts and pastes) all files and subdirectories from a source directory to a destination directory. Useful for organizing data after processing (e.g., moving selected files to a final training directory).

Usage
Bash

python MoveAllFiles.py <source_dir> <destination_dir>
# Example: python MoveAllFiles.py ./raw/Uncategorize ./data/TrashData

//------------------------------------------------------------------------------------------------------
# 4) CopyAllFiles.py
//------------------------------------------------------------------------------------------------------

Copies (duplicates) all files and subdirectories from a source directory to a destination directory. Used for creating backups or preparing working copies while preserving the original data.

Usage
Bash

python CopyAllFiles.py <source_dir> <copy_dir>
# Example: python CopyAllFiles.py ./raw/Uncategorize ./raw/CopyDirectory

//------------------------------------------------------------------------------------------------------
# 5) testTextAnalyzerToBasicDic2.py
//------------------------------------------------------------------------------------------------------

Analyzes a plain text file for the occurrence frequency of words listed in a CSV dictionary. This is crucial for analyzing specialized domain weight and verifying the distribution of synonyms across your corpus. (The search is case-insensitive).

Usage
Bash

python AnakysisWord.py <dictionary_path> <text_path>




#Example: python .\script\py\testTextAnalyzerToBasicDic2.py .\raw\test\testDic_20251019_AdultBasicWord.csv .\raw\Uncategorized\Raw_sora004_org.txt