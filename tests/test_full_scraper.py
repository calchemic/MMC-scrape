#!/usr/bin/env python3

import csv
import concurrent.futures
import time
import math
from firecrawl_scraper import CourseContentScraper

def load_test_urls(limit=50):
    """Load first N URLs from CSV for testing"""
    urls = []
    with open("MMC Lessons All Simulation Lessons.csv", "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            urls.append({
                "url": row["link"],
                "lesson_id": row["lessonID"],
                "lesson_name": row["lessonname"],
                "course_id": row["courseid"],
                "course_name": row["coursename"]
            })
    return urls

def load_api_keys():
    """Load API keys from file"""
    with open("API keys.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def scrape_multiple_courses(args):
    """Scrape multiple courses assigned to a single worker/API key"""
    course_batch, api_key, worker_id = args
    
    worker_start_time = time.time()
    results = []
    
    print(f"🚀 Worker {worker_id}: Starting {len(course_batch)} courses")
    print(f"   API Key: {api_key[:20]}...")
    
    # Create scraper with assigned API key
    scraper = CourseContentScraper(api_key)
    
    for i, url_data in enumerate(course_batch):
        course_start_time = time.time()
        lesson_id = url_data["lesson_id"]
        
        try:
            print(f"   📚 Worker {worker_id}: Processing {lesson_id} ({i+1}/{len(course_batch)})")
            
            # Process the course URL
            result = scraper.process_course_url(url_data["url"])
            
            duration = time.time() - course_start_time
            print(f"   ✅ Worker {worker_id}: Completed {lesson_id} in {duration:.1f}s")
            
            results.append({
                "worker_id": worker_id,
                "lesson_id": lesson_id,
                "course_id": url_data["course_id"],
                "status": "success",
                "duration": duration
            })
            
        except Exception as e:
            duration = time.time() - course_start_time
            error_msg = str(e)[:100]  # Truncate long error messages
            print(f"   ❌ Worker {worker_id}: Failed {lesson_id} in {duration:.1f}s - {error_msg}")
            
            results.append({
                "worker_id": worker_id,
                "lesson_id": lesson_id,
                "course_id": url_data["course_id"],
                "status": "failed",
                "duration": duration,
                "error": error_msg
            })
    
    worker_duration = time.time() - worker_start_time
    successful_count = len([r for r in results if r["status"] == "success"])
    
    print(f"🏁 Worker {worker_id}: Completed {successful_count}/{len(course_batch)} courses in {worker_duration:.1f}s")
    
    return {
        "worker_id": worker_id,
        "api_key": api_key[:20] + "...",
        "total_duration": worker_duration,
        "courses_processed": len(course_batch),
        "successful": successful_count,
        "failed": len(course_batch) - successful_count,
        "results": results
    }

def create_worker_batches(urls, api_keys, max_workers=10):
    """Create worker batches where each API key gets multiple courses"""
    num_workers = min(max_workers, len(api_keys))
    total_urls = len(urls)
    
    # Calculate courses per worker
    courses_per_worker = math.ceil(total_urls / num_workers)
    
    print(f"📊 Batch Configuration:")
    print(f"   • Total courses: {total_urls}")
    print(f"   • Workers to use: {num_workers}")
    print(f"   • Courses per worker: {courses_per_worker}")
    print()
    
    # Create worker assignments
    worker_tasks = []
    for i in range(num_workers):
        start_idx = i * courses_per_worker
        end_idx = min(start_idx + courses_per_worker, total_urls)
        
        if start_idx < total_urls:  # Only create task if there are URLs to process
            course_batch = urls[start_idx:end_idx]
            api_key = api_keys[i % len(api_keys)]  # Round-robin API keys
            worker_id = i + 1
            
            worker_tasks.append((course_batch, api_key, worker_id))
    
    return worker_tasks

def main():
    print("="*80)
    print("🚀 PARALLEL MMC COURSE SCRAPER - TEST (50 COURSES)")
    print("="*80)
    
    # Load data
    urls = load_test_urls(50)
    api_keys = load_api_keys()
    
    print(f"📊 Configuration:")
    print(f"   • Total courses to process: {len(urls)}")
    print(f"   • API keys available: {len(api_keys)}")
    print()
    
    # Create worker tasks (use 10 workers for testing)
    worker_tasks = create_worker_batches(urls, api_keys, max_workers=10)
    
    print(f"👥 Worker assignments:")
    for i, (course_batch, api_key, worker_id) in enumerate(worker_tasks):
        print(f"   Worker {worker_id:2d}: {len(course_batch):3d} courses → {api_key[:20]}...")
    print()
    
    # Start parallel processing
    print("🔧 Starting parallel processing...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(worker_tasks)) as executor:
        worker_results = list(executor.map(scrape_multiple_courses, worker_tasks))
    
    # Calculate overall results
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Aggregate results
    all_course_results = []
    total_successful = 0
    total_failed = 0
    
    for worker_result in worker_results:
        all_course_results.extend(worker_result["results"])
        total_successful += worker_result["successful"]
        total_failed += worker_result["failed"]
    
    # Print summary
    print("\n" + "="*80)
    print("📊 PARALLEL SCRAPING RESULTS")
    print("="*80)
    
    print(f"✅ Successful: {total_successful}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Total courses: {len(all_course_results)}")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"⚡ Average time per course: {total_duration/len(all_course_results):.1f}s")
    print(f"🏃 Processing rate: {len(all_course_results)/total_duration*60:.1f} courses/minute")
    
    if total_successful > 0:
        successful_results = [r for r in all_course_results if r["status"] == "success"]
        avg_individual_time = sum(r["duration"] for r in successful_results) / len(successful_results)
        estimated_sequential_time = avg_individual_time * len(all_course_results)
        speedup = estimated_sequential_time / total_duration
        print(f"📈 Average individual processing time: {avg_individual_time:.1f}s")
        print(f"🚀 Estimated speedup: {speedup:.1f}x")
    
    # Worker performance summary
    print("\n📋 Worker Performance:")
    for worker_result in sorted(worker_results, key=lambda x: x["worker_id"]):
        worker_id = worker_result["worker_id"]
        duration = worker_result["total_duration"]
        successful = worker_result["successful"]
        total_courses = worker_result["courses_processed"]
        api_key = worker_result["api_key"]
        
        success_rate = (successful / total_courses * 100) if total_courses > 0 else 0
        
        print(f"   Worker {worker_id:2d}: {successful:3d}/{total_courses:3d} courses ({success_rate:5.1f}%) in {duration:6.1f}s - {api_key}")
    
    print(f"\n🎉 Test completed in {total_duration:.1f}s!")
    print(f"💡 This approach should scale to all 1,537 courses!")

if __name__ == "__main__":
    main() 