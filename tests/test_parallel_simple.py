#!/usr/bin/env python3

import csv
import concurrent.futures
import time
from firecrawl_scraper import CourseContentScraper

def load_first_n_urls(n=10):
    """Load first n URLs from CSV"""
    urls = []
    with open("MMC Lessons All Simulation Lessons.csv", "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= n:
                break
            urls.append({
                "url": row["link"],
                "lesson_id": row["lessonID"],
                "lesson_name": row["lessonname"]
            })
    return urls

def load_api_keys():
    """Load API keys from file"""
    with open("API keys.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def scrape_single_url(args):
    """Scrape a single URL with assigned API key"""
    url_data, api_key, worker_id = args
    
    start_time = time.time()
    try:
        print(f"🚀 Worker {worker_id}: Starting {url_data['lesson_id']}")
        print(f"   API Key: {api_key[:20]}...")
        
        scraper = CourseContentScraper(api_key)
        result = scraper.process_course_url(url_data["url"])
        
        duration = time.time() - start_time
        print(f"✅ Worker {worker_id}: Completed {url_data['lesson_id']} in {duration:.1f}s")
        
        return {
            "worker_id": worker_id,
            "lesson_id": url_data["lesson_id"],
            "status": "success",
            "duration": duration
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Worker {worker_id}: Failed {url_data['lesson_id']} in {duration:.1f}s - {str(e)}")
        
        return {
            "worker_id": worker_id,
            "lesson_id": url_data["lesson_id"],
            "status": "failed",
            "duration": duration,
            "error": str(e)
        }

def main():
    print("="*80)
    print("🚀 PARALLEL MMC COURSE SCRAPER - FIRST 10 URLS")
    print("="*80)
    
    # Load data
    api_keys = load_api_keys()
    urls = load_first_n_urls(10)
    
    print(f"📊 Loaded {len(api_keys)} API keys and {len(urls)} URLs")
    print()
    
    # Create worker assignments (each URL gets a different API key)
    tasks = []
    for i, url_data in enumerate(urls):
        api_key = api_keys[i % len(api_keys)]  # Round-robin assignment
        worker_id = i + 1
        tasks.append((url_data, api_key, worker_id))
    
    print("🔧 Worker assignments:")
    for url_data, api_key, worker_id in tasks:
        print(f"   Worker {worker_id}: {url_data['lesson_id']} → {api_key[:20]}...")
    print()
    
    # Run parallel processing
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(scrape_single_url, tasks))
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Summary
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    print("\n" + "="*80)
    print("📊 PARALLEL SCRAPING RESULTS")
    print("="*80)
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"⚡ Average time per URL: {total_duration/len(urls):.1f}s")
    
    print("\n📋 Detailed results:")
    for result in sorted(results, key=lambda x: x["worker_id"]):
        status = "✅" if result["status"] == "success" else "❌"
        duration = result["duration"]
        lesson_id = result["lesson_id"]
        print(f"   {status} Worker {result['worker_id']}: {lesson_id} ({duration:.1f}s)")
    
    print("\n🎉 Parallel scraping completed!")

if __name__ == "__main__":
    main() 