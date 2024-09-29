import os
import re
import tiktoken
import argparse
import tempfile
import shutil
from git import Repo
import hashlib

def clone_repository(repo_url, use_cache=False, cache_dir=None):
    if use_cache and cache_dir:
        repo_hash = hashlib.md5(repo_url.encode()).hexdigest()
        cache_path = os.path.join(cache_dir, repo_hash)
        if os.path.exists(cache_path):
            print(f"Using cached repository: {cache_path}")
            return cache_path

    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)

    if use_cache and cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        shutil.copytree(temp_dir, cache_path)
        print(f"Cached repository: {cache_path}")
        shutil.rmtree(temp_dir)
        return cache_path

    return temp_dir

def is_supported_file(filename, include_readme_license, match_pattern=None):
    supported_extensions = ('.py', '.js', '.java', '.cpp', '.h', '.cs', '.rb', '.go', '.rs', '.ts', '.md', '.txt', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat', '.ps1')
    
    if match_pattern:
        return re.search(match_pattern, filename) is not None
    
    if filename.lower().endswith(supported_extensions):
        return True
    if include_readme_license and filename.upper() in ['README', 'LICENSE']:
        return True
    return False

def analyze_repository(repo_path, include_readme_license, include_git_files, path=None, match_pattern=None):
    total_tokens = 0
    file_counts = {}
    all_files = []

    analyze_path = os.path.join(repo_path, path) if path else repo_path

    for root, dirs, files in os.walk(analyze_path):
        if '.git' in root.split(os.path.sep) and not include_git_files:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_path)
            
            all_files.append(relative_path)
            
            if is_supported_file(file, include_readme_license, match_pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        tokens = count_tokens(content)
                        total_tokens += tokens
                        file_counts[relative_path] = tokens
                        print(f"Processed file: {relative_path}, Tokens: {tokens}")
                except Exception as e:
                    print(f"Error processing file {relative_path}: {str(e)}")
            else:
                print(f"Skipped unsupported file: {relative_path}")

    return total_tokens, file_counts, all_files

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def compare_with_llms(total_tokens):
    llm_contexts = {
        "GPT-3.5 Turbo": 4096,
        "GPT-4": 8192,
        "Claude": 100000,
        "Llama 2": 4096,
        "GPT-4 Turbo": 128000
    }

    recommendations = []
    for llm, context in llm_contexts.items():
        if total_tokens == 0:
            coverage = 100  # If there are no tokens, all LLMs have 100% coverage
        else:
            coverage = min(100, (context / total_tokens) * 100)
        recommendations.append((llm, context, coverage))

    return sorted(recommendations, key=lambda x: x[2], reverse=True)

def analyze_and_recommend(repo_path, include_readme_license, include_git_files, path=None, match_pattern=None):
    total_tokens, file_counts, all_files = analyze_repository(repo_path, include_readme_license, include_git_files, path, match_pattern)
    
    print(f"\nAll files found in the repository{' (filtered by path)' if path else ''}{' (filtered by pattern)' if match_pattern else ''}:")
    for file in all_files:
        print(file)
    
    if total_tokens == 0:
        print("\nNo tokens found in the repository. The repository might be empty or contain only unsupported file types.")
        return

    recommendations = compare_with_llms(total_tokens)

    print(f"\nAnalyzing repository: {repo_path}")
    if path:
        print(f"Analyzing path: {path}")
    if match_pattern:
        print(f"Matching files with pattern: {match_pattern}")
    print(f"Total tokens in repository: {total_tokens}")
    print("\nToken distribution by file:")
    for file, tokens in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{file}: {tokens} tokens")

    print("\nLLM Recommendations:")
    for llm, context, coverage in recommendations:
        print(f"{llm} (Context: {context}): {coverage:.2f}% coverage")

    optimal_llm = recommendations[0][0]
    print(f"\nOptimal LLM: {optimal_llm}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a GitHub repository and recommend optimal LLM based on token count.")
    parser.add_argument("repo_url", help="URL of the GitHub repository to analyze.")
    parser.add_argument("--include-readme-license", action="store_true", help="Include README and LICENSE files without extensions in the analysis.")
    parser.add_argument("--include-git-files", action="store_true", help="Include files under the .git folder in the analysis.")
    parser.add_argument("--path", help="Specify a path within the cloned directory to analyze. Only files within this path will be processed.")
    parser.add_argument("--cache", action="store_true", help="Use local cache for downloaded repositories.")
    parser.add_argument("--cache-dir", default=os.path.expanduser("~/.llm_analyzer_cache"), help="Directory to store cached repositories.")
    parser.add_argument("--match", help="Regular expression pattern to match files for analysis.")
    args = parser.parse_args()

    try:
        print(f"Cloning or using cached repository: {args.repo_url}")
        repo_path = clone_repository(args.repo_url, use_cache=args.cache, cache_dir=args.cache_dir)
        print("Repository ready for analysis.")
        analyze_and_recommend(repo_path, args.include_readme_license, args.include_git_files, args.path, args.match)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if not args.cache:
            print("Cleaning up temporary files...")
            shutil.rmtree(repo_path, ignore_errors=True)