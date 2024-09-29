# needllm

This tool allows you to quickly assess a repository and get recommendations for the most suitable LLM based on context window sizes. It helps optimize your workflow when working with AI models on your codebase.

## Features

1. Traverses the repository and counts tokens in relevant files.
2. Calculates the total token count for the entire repository or a specified path.
3. Compares the token count with different LLM context windows.
4. Provides recommendations based on the percentage of the repository that fits within each LLM's context window.
5. Supports caching of downloaded repositories for faster subsequent analyses.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/needllm.git
   cd needllm
   ```

2. Create and activate a virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Basic usage:

```
python llm_analyzer.py https://github.com/username/repo
```

Analyze a specific path within the repository:

```
python llm_analyzer.py https://github.com/username/repo --path src/
```

Include README and LICENSE files:

```
python llm_analyzer.py https://github.com/username/repo --include-readme-license
```

Include .git files:

```
python llm_analyzer.py https://github.com/username/repo --include-git-files
```

Use caching to speed up subsequent analyses:

```
python llm_analyzer.py https://github.com/username/repo --cache
```

## Options

- `--path`: Specify a path within the cloned directory to analyze. Only files within this path will be processed.
- `--include-readme-license`: Include README and LICENSE files without extensions in the analysis.
- `--include-git-files`: Include files under the .git folder in the analysis.
- `--cache`: Use local cache for downloaded repositories to speed up subsequent analyses.
- `--cache-dir`: Specify a custom directory to store cached repositories (default is ~/.llm_analyzer_cache).

## Considerations

1. **File Types**: The tool focuses on common code and documentation file types. You may need to adjust the file extensions based on your specific needs.

2. **Tokenization**: The tool uses the GPT-3.5 Turbo tokenizer. For more accurate results with specific models, you might want to use model-specific tokenizers.

3. **Context Relevance**: Remember that larger context windows don't always lead to better performance. The tool provides a simple coverage percentage, but you should also consider the nature of your tasks and the complexity of your codebase.

4. **Performance**: For very large repositories, you might want to implement multiprocessing to speed up the analysis.

5. **Memory Usage**: Be mindful of memory usage when processing large files or repositories.

6. **Caching**: The --cache option can significantly speed up repeated analyses of the same repository. However, it may use additional disk space to store the cached repositories.

## Example

```
python llm_analyzer.py https://github.com/bitcoin/bitcoin --path src/index --cache
```

This command will analyze only the `src/` directory of the Bitcoin repository, use caching for faster subsequent runs, and provide LLM recommendations based on the token count of files in that directory.

## Deactivating the Virtual Environment

When you're done using the tool, you can deactivate the virtual environment:

```
deactivate
```

This will return you to your global Python environment.
