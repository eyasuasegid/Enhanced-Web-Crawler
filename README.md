# 🕷️ Enhanced Web Crawler

**Enhanced Web Crawler** is a robust, command-line tool designed for security researchers and penetration testers. It rapidly downloads website assets (HTML, JS, CSS, Images) while handling common network issues like timeouts, rate ratings, and SSL errors.

It is the perfect companion for static analysis tools like **ParamHunter Pro**.

## ✨ Key Features

- **🛡️ Safe by Default**: Runs in "Dry Run" mode (no files saved) unless an output directory is explicitly provided.
- **📂 Hierarchical Organization**: Can mirror the website's directory structure locally (`-f`), making manual analysis intuitive.
- **🔄 Smart Retries**: Automatically handles timeouts and 4xx/5xx errors with exponential backoff.
- **⚡ Fast & Configurable**: Set page limits, timeouts, and ignore SSL errors for internal targets.

## 🚀 Usage

### Basic Crawl (Dry Run)
Test connectivity and see what the crawler *would* find without saving anything.
```bash
python3 web_crawler.py https://example.com
```

### Save Findings
Use the `-o` flag to specify where to save the files.
```bash
python3 web_crawler.py https://example.com -o crawl_results
```

### Organized Structure (`-f`)
Use the `-f` flag to save files in folders matching their URL path (e.g., `example.com/assets/style.css`).
```bash
python3 web_crawler.py https://example.com -o crawl_results -f
```

### Full Configuration
Crawl up to 100 pages, ignore SSL errors (for internal/broken certs), and set a 5-second timeout.
```bash
python3 web_crawler.py https://internal-site.local \
    -o internal_scan \
    -f \
    -p 100 \
    -t 5 \
    --no-ssl
```

## 📋 Options

| Flag | Description | Default |
|------|-------------|---------|
| `url` | Target URL to start crawling | N/A |
| `-o`, `--output` | Directory to save files. Required to save data. | `None` (Dry Run) |
| `-f`, `--folder-structure` | Enable hierarchical folder structure. | `False` (Flat) |
| `-p`, `--pages` | Maximum number of pages/files to crawl. | `50` |
| `-t`, `--timeout` | Request timeout in seconds. | `15` |
| `--no-ssl` | Disable SSL certificate verification. | `False` |

## 📦 Dependencies

- `requests`
- `beautifulsoup4`

```bash
pip3 install requests beautifulsoup4
```
