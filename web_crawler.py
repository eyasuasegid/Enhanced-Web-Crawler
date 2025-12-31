#!/usr/bin/env python3
"""
Enhanced Web Crawler with Better Error Handling
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import time
import ssl
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class EnhancedWebCrawler:
    def __init__(self, base_url, output_dir=None, 
                 timeout=15, verify_ssl=False, max_retries=3, use_structure=False):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.use_structure = use_structure
        self.visited_urls = set()
        self.files_to_analyze = []
        
        # Create output directory
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Create session with retry
        self.session = self._create_session()
    
    def _create_session(self):
        """Create requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def crawl(self, max_pages=50):
        """Crawl the website with better error handling"""
        queue = [self.base_url]
        successful_crawls = 0
        
        while queue and len(self.visited_urls) < max_pages and successful_crawls < max_pages:
            url = queue.pop(0)
            
            if url in self.visited_urls:
                continue
            
            print(f"🔍 Attempting: {url}")
            
            try:
                response = self.session.get(
                    url, 
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )
                
                self.visited_urls.add(url)
                successful_crawls += 1
                
                # Check if successful
                if response.status_code == 200:
                    print(f"✅ Success: {url} ({response.status_code})")
                    
                    # Save HTML
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        self._save_html(url, response.text)
                        # Extract links
                        soup = BeautifulSoup(response.text, 'html.parser')
                        links = self._extract_links(soup, url)
                        # Add new links to queue
                        for link in links:
                            if link not in self.visited_urls and link not in queue:
                                queue.append(link)
                    
                    # Save other files
                    elif self._should_save_file(url):
                        self._save_file(url, response.content)
                    
                    # Be polite
                    time.sleep(1)
                
                else:
                    print(f"⚠️  Status {response.status_code}: {url}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout: {url} (increased timeout to {self.timeout}s)")
                # Try with longer timeout for this specific URL
                try:
                    response = self.session.get(url, timeout=30, verify=self.verify_ssl)
                    if response.status_code == 200:
                        self._save_html(url, response.text)
                except:
                    pass
                    
            except requests.exceptions.SSLError:
                print(f"🔒 SSL Error: {url}. Trying without SSL verification...")
                try:
                    response = requests.get(url, timeout=self.timeout, verify=False)
                    if response.status_code == 200:
                        self._save_html(url, response.text)
                except:
                    pass
                    
            except Exception as e:
                print(f"❌ Error: {url} - {type(e).__name__}: {str(e)[:100]}")
            
            # Update progress
            print(f"📊 Progress: {successful_crawls}/{max_pages} pages")
    
    # ... rest of the methods remain same as original web_crawler.py ...
    
    def _extract_links(self, soup, base_url):
        """Extract all links from page"""
        links = []
        
        for tag in soup.find_all(['a', 'link', 'script', 'img']):
            href = tag.get('href') or tag.get('src')
            
            if not href:
                continue
            
            # Resolve relative URLs
            full_url = urllib.parse.urljoin(base_url, href)
            
            # Allow same domain AND subdomains
            parsed_base = urllib.parse.urlparse(self.base_url)
            parsed_full = urllib.parse.urlparse(full_url)
            
            # Check if it's the same domain or a subdomain
            base_domain = parsed_base.netloc.replace('www.', '')
            target_domain = parsed_full.netloc.replace('www.', '')
            
            if (base_domain == target_domain or target_domain.endswith('.' + base_domain)) and full_url not in self.visited_urls:
                # Filter out specific non-crawlable types if needed, but keeping it minimal for aggressive crawling
                if not any(full_url.endswith(ext) for ext in ['.exe', '.dmg', '.pkg']):
                    links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def _should_save_file(self, url):
        """Check if we should save this file - Aggressive Mode"""
        # Save everything that isn't explicitly skipped
        # We already handled HTML in the main loop
        return True
    
    def _save_html(self, url, content):
        """Save HTML file"""
        if not self.output_dir:
            return
            
        if self.use_structure:
            filepath = self._get_structured_filepath(url, '.html')
        else:
            filename = self._url_to_filename(url, '.html')
            filepath = os.path.join(self.output_dir, filename)
        
        # Ensure directory exists for structured path
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.files_to_analyze.append(filepath)
        print(f"  💾 Saved: {os.path.relpath(filepath, self.output_dir)}")
    
    def _save_file(self, url, content):
        """Save non-HTML file"""
        if not self.output_dir:
            return

        if self.use_structure:
            filepath = self._get_structured_filepath(url)
        else:
            filename = self._url_to_filename(url)
            filepath = os.path.join(self.output_dir, filename)
        
        # Ensure directory exists for structured path
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        self.files_to_analyze.append(filepath)
        print(f"  💾 Saved: {os.path.relpath(filepath, self.output_dir)}")
    
    def _url_to_filename(self, url, default_ext=''):
        """Convert URL to safe filename with hash to prevent collisions"""
        # Remove protocol
        filename = url.replace('https://', '').replace('http://', '')
        
        # Replace problematic characters
        filename = filename.replace('/', '_').replace('?', '_').replace('&', '_')
        
        # Add hash to ensure uniqueness for different query params
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{filename[:50]}_{url_hash}"
        
        # Add extension if missing
        if default_ext and not any(filename.endswith(ext) for ext in ['.html', '.js', '.css']):
            filename += default_ext
        
        return filename

    def _get_structured_filepath(self, url, default_ext=''):
        """Generate a hierarchical file path based on URL"""
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.netloc.replace(':', '_') # Sanitized hostname
        path = parsed.path.strip('/')
        
        if not path:
            filename = 'index.html'
            relative_dir = hostname
        else:
            path_parts = path.split('/')
            filename = path_parts[-1]
            relative_dir = os.path.join(hostname, *path_parts[:-1])
            
            # If path ends with slash or looks like a directory, use index.html
            if url.endswith('/') or not os.path.splitext(filename)[1]:
                if not url.endswith('/'):
                    # It was a file-like path but no extension, treat as file unless we default to dir
                    # But often /foo means /foo/index.html or just file 'foo'. 
                    # Let's check if we provided a default extension (like .html for pages)
                    if default_ext == '.html':
                         # Treat as directory/index.html
                         relative_dir = os.path.join(relative_dir, filename)
                         filename = 'index.html'
                    elif default_ext:
                        filename += default_ext
                else:
                    filename = 'index.html'

        # Just to be safe with mixed extensions
        if default_ext and not filename.endswith(default_ext) and not filename.endswith('.html'):
             filename += default_ext
             
        # Sanitize filename
        filename = filename.replace('?', '_').replace('&', '_').replace('=', '_')
        
        return os.path.join(self.output_dir, relative_dir, filename)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Web Crawler")
    parser.add_argument('url', help='URL to crawl')
    parser.add_argument('-o', '--output', default=None, help='Output directory (optional)')
    parser.add_argument('-p', '--pages', type=int, default=50, help='Max pages to crawl')
    parser.add_argument('-t', '--timeout', type=int, default=15, help='Timeout in seconds')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL verification')

    parser.add_argument('-f', '--folder-structure', action='store_true', help='Use hierarchical folder structure')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting enhanced crawler for: {args.url}")
    print(f"📁 Output: {args.output}")
    print(f"📂 Structure: {args.folder_structure}")
    print(f"⏱️  Timeout: {args.timeout}s")
    print(f"🔒 SSL Verify: {not args.no_ssl}")
    
    crawler = EnhancedWebCrawler(
        args.url, 
        args.output,
        timeout=args.timeout,
        verify_ssl=not args.no_ssl,
        use_structure=args.folder_structure
    )
    
    crawler.crawl(max_pages=args.pages)
    
    print(f"\n✅ Crawling complete!")
    print(f"   Successful crawls: {len(crawler.visited_urls)}")
    print(f"   Files saved: {len(crawler.files_to_analyze)}")
    print(f"   Output directory: {args.output}")
    
    print(f"   Output directory: {args.output}")

if __name__ == '__main__':
    main()
