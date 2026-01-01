"""
Views for discovery_app
"""
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
# from django_ratelimit.decorators import ratelimit  # Rate limiting disabled
from pathlib import Path
import json
import logging
import threading
from queue import Queue, Empty
from datetime import datetime, timedelta
import re

from agent import BusinessDiscoveryAgent

logger = logging.getLogger(__name__)


def sanitize_input(text, max_length=200):
    """
    Sanitize user input to prevent injection attacks and XSS.
    Removes dangerous characters and limits length.
    """
    if not text:
        return ''
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes and control characters (except newlines and tabs for addresses)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Allow only printable characters and common punctuation for addresses/industries
    # This regex allows letters, numbers, spaces, and common punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\-\'.,&()]', '', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def get_history_file_path():
    """Get the path to the search history file"""
    project_root = Path(__file__).resolve().parent.parent
    history_file = project_root / 'search_history.json'
    return history_file


def find_previous_search(industry, location):
    """
    Check if a previous search exists with the same industry and location.
    Returns the previous search entry if found, None otherwise.
    """
    history_file = get_history_file_path()
    
    if not history_file.exists():
        return None
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # Normalize inputs for comparison (case-insensitive, trimmed)
        normalized_industry = industry.lower().strip()
        normalized_location = location.lower().strip()
        
        # Search in reverse order (most recent first)
        for search_entry in reversed(history):
            entry_industry = search_entry.get('industry', '').lower().strip()
            entry_location = search_entry.get('location', '').lower().strip()
            
            if entry_industry == normalized_industry and entry_location == normalized_location:
                logger.info(f"✅ Found previous search: {industry} in {location}")
                print(f"✅ Found previous search: {industry} in {location}")
                return search_entry
        
        logger.info(f"📝 No previous search found for: {industry} in {location}")
        print(f"📝 No previous search found for: {industry} in {location}")
        return None
        
    except Exception as e:
        logger.warning(f"Could not check previous searches: {e}")
        print(f"⚠️  Could not check previous searches: {e}")
        return None


def load_existing_businesses_from_previous_search(previous_search):
    """
    Load businesses from a previous search entry to check for duplicates.
    Returns sets of place_ids and business keys (name+address) from the previous search.
    """
    existing_place_ids = set()
    existing_business_keys = set()
    
    if not previous_search:
        return existing_place_ids, existing_business_keys
    
    try:
        results = previous_search.get('results', {})
        businesses = results.get('businesses', [])
        
        # Extract place_ids and business keys from each business
        for business in businesses:
            # Check for place_id
            place_id = business.get('place_id')
            if place_id:
                existing_place_ids.add(place_id)
            
            # Also check for name+location combination (fallback for businesses without place_id)
            name = business.get('name', '').lower().strip()
            location = business.get('location', '').lower().strip()
            if name and location:
                business_key = f"{name}|{location}"
                existing_business_keys.add(business_key)
        
        logger.info(f"📋 Loaded {len(existing_place_ids)} place_ids and {len(existing_business_keys)} business keys from previous search for duplicate checking")
        print(f"📋 Loaded {len(existing_place_ids)} place_ids and {len(existing_business_keys)} business keys from previous search for duplicate checking")
        
    except Exception as e:
        logger.warning(f"Could not load existing businesses from previous search: {e}")
        print(f"⚠️  Could not load existing businesses from previous search: {e}")
    
    return existing_place_ids, existing_business_keys


def save_search_to_history(results, industry, location, max_results):
    """Save a search result to the history file"""
    try:
        history_file = get_history_file_path()
        
        # Load existing history
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Sanitize inputs before saving to history
        safe_industry = sanitize_input(industry, max_length=100)
        safe_location = sanitize_input(location, max_length=200)
        
        # Add new search entry
        search_entry = {
            'timestamp': datetime.now().isoformat(),
            'industry': safe_industry,
            'location': safe_location,
            'max_results': max_results,
            'summary': results.get('summary', {}),
            'total_businesses': results.get('summary', {}).get('total_businesses', 0),
            'results': results  # Store full results
        }
        
        history.append(search_entry)
        
        # Save ALL searches (no limit) - all details are preserved in JSON
        # Save back to file with proper formatting
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved search to history: {industry} in {location} (Total searches: {len(history)})")
        print(f"✅ Saved search to history: {industry} in {location} (Total searches: {len(history)})")
        
    except Exception as e:
        logger.warning(f"Could not save search to history: {e}")


def index(request):
    """Render the main search page"""
    return render(request, 'discovery_app/index.html')


def send_sse_message(event_type, data):
    """Format a Server-Sent Events message"""
    message = f"event: {event_type}\n"
    message += f"data: {json.dumps(data)}\n\n"
    return message


@csrf_exempt
@require_http_methods(["POST"])
# @ratelimit(key='ip', rate='10/h', method='POST', block=True)  # Rate limiting disabled
def api_search_stream(request):
    """Handle streaming search API requests with Server-Sent Events"""
    # Parse request data first (before generator)
    try:
        # Limit request body size to prevent DoS (1MB max)
        if len(request.body) > 1024 * 1024:
            return JsonResponse({
                'error': 'Request body too large'
            }, status=413)
        
        data = json.loads(request.body.decode('utf-8'))
        
        # Sanitize and validate input
        industry = sanitize_input(data.get('industry', ''), max_length=100)
        location = sanitize_input(data.get('location', ''), max_length=200)
        
        # Validate max_results with error handling
        try:
            max_results = int(data.get('max_results', 50))
        except (ValueError, TypeError):
            max_results = 50
        
        # Validate max_results range
        if max_results < 1:
            max_results = 1
        elif max_results > 100:
            max_results = 100
        
        # Validate required fields after sanitization
        if not industry or not location:
            return JsonResponse({
                'error': 'Industry and location are required'
            }, status=400)
        
        # Additional validation: ensure inputs are not empty after sanitization
        if len(industry) < 2 or len(location) < 2:
            return JsonResponse({
                'error': 'Industry and location must be at least 2 characters long'
            }, status=400)
        
        logger.info(f"Search request: Industry={industry}, Location={location}, Max Results={max_results}")
    except json.JSONDecodeError as e:
        return JsonResponse({
            'error': f'Invalid JSON: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Invalid request: {str(e)}'
        }, status=400)
    
    def event_stream():
        try:
            logger.info(f"🔍 Starting streaming search: {industry} in {location} (max: {max_results})")
            print(f"\n🔍 Starting streaming search: {industry} in {location} (max: {max_results})")
            
            # Send initial status
            yield send_sse_message('status', {
                'message': f'Starting search for "{industry}" in "{location}"...',
                'type': 'starting'
            })
            
            # Create a queue to collect callback results
            business_queue = Queue()
            
            def business_callback_wrapper(processed_biz, index, total):
                business_queue.put(('business', processed_biz, index, total))
            
            # Step 1: Check if previous search exists with same industry and location
            previous_search = find_previous_search(industry, location)
            
            # Step 2: Load existing businesses from previous search (if exists) for duplicate checking
            # Note: We load the results but DON'T display them - only use them to filter duplicates
            existing_place_ids, existing_business_keys = load_existing_businesses_from_previous_search(previous_search)
            
            if previous_search:
                logger.info(f"📚 Previous search found: {industry} in {location} - will skip duplicates from previous results")
                print(f"📚 Previous search found: {industry} in {location} - will skip duplicates from previous results")
                logger.info(f"📋 Loaded {len(existing_place_ids)} place_ids and {len(existing_business_keys)} business keys for duplicate checking")
                print(f"📋 Loaded {len(existing_place_ids)} place_ids and {len(existing_business_keys)} business keys for duplicate checking")
                yield send_sse_message('status', {
                    'message': f'Found previous search. Starting fresh search (will skip duplicates from previous results)...',
                    'type': 'info'
                })
            else:
                logger.info(f"🔄 Starting fresh search for: {industry} in {location} (no previous search found)")
                print(f"🔄 Starting fresh search for: {industry} in {location} (no previous search found)")
            
            # Run the agent with streaming
            agent = BusinessDiscoveryAgent()
            
            # Pass existing businesses to agent for duplicate checking
            # The discovery module will skip any businesses that match these and continue searching
            agent._existing_place_ids = existing_place_ids
            agent._existing_business_keys = existing_business_keys
            
            # We need to run the agent in a thread and yield results as they come
            results_complete = {'done': False, 'results': None, 'error': None}
            
            def run_agent():
                try:
                    results = agent.run_streaming(
                        industry=industry,
                        location=location,
                        max_results=max_results,
                        website_required=False,
                        callback=business_callback_wrapper
                    )
                    results_complete['results'] = results
                    results_complete['done'] = True
                except Exception as e:
                    results_complete['error'] = str(e)
                    results_complete['done'] = True
                    import traceback
                    traceback.print_exc()
            
            # Start agent in a separate thread
            agent_thread = threading.Thread(target=run_agent)
            agent_thread.start()
            
            # Stream results as they come in
            while not results_complete['done'] or not business_queue.empty():
                try:
                    # Check for new businesses (with timeout)
                    try:
                        event_type, processed_biz, index, total = business_queue.get(timeout=0.5)
                        
                        # Send business update
                        yield send_sse_message('business', {
                            'business': processed_biz,
                            'index': index,
                            'total': total
                        })
                        
                        # Send progress update
                        yield send_sse_message('progress', {
                            'current': index,
                            'total': total,
                            'message': f'Processed {index}/{total} businesses'
                        })
                        
                    except Empty:
                        # Queue timeout - continue loop to check if done
                        continue
                    
                except Exception as e:
                    logger.error(f"Error in streaming: {e}")
                    yield send_sse_message('error', {
                        'error': str(e)
                    })
                    break
            
            # Wait for thread to complete
            agent_thread.join(timeout=300)  # 5 minute timeout
            
            # Check for error
            if results_complete['error']:
                yield send_sse_message('error', {
                    'error': results_complete['error']
                })
                return
            
            # Get final results
            final_results = results_complete['results']
            
            if final_results:
                # Save results to file
                output_json = agent.formatter.to_json(final_results)
                
                # Get project root (parent of discovery_app)
                project_root = Path(__file__).resolve().parent.parent
                static_dir = project_root / 'static'
                static_dir.mkdir(exist_ok=True)
                results_file = static_dir / 'results.json'
                
                try:
                    with open(results_file, 'w', encoding='utf-8') as f:
                        f.write(output_json)
                except Exception as e:
                    logger.warning(f"Could not save to static directory: {e}")
                
                # Also save in project root
                try:
                    root_results_file = project_root / 'results.json'
                    with open(root_results_file, 'w', encoding='utf-8') as f:
                        f.write(output_json)
                except Exception as e:
                    logger.warning(f"Could not save to project root: {e}")
                
                # Save to search history
                save_search_to_history(final_results, industry, location, max_results)
                
                # Send final summary
                yield send_sse_message('summary', {
                    'summary': final_results['summary']
                })
                
                # Send completion message
                total = final_results['summary']['total_businesses']
                logger.info(f"✅ Streaming search complete: Found {total} businesses")
                print(f"✅ Streaming search complete: Found {total} businesses")
                
                yield send_sse_message('complete', {
                    'message': f'Search complete! Found {total} businesses.',
                    'total': total
                })
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in streaming API handler: {error_msg}")
            import traceback
            traceback.print_exc()
            yield send_sse_message('error', {
                'error': f'Search failed: {error_msg}'
            })
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def history(request):
    """Display all previous search results from JSON file"""
    history_file = get_history_file_path()
    
    # Load search history from JSON file
    search_history = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                search_history = json.load(f)
            
            # Reverse to show most recent first
            search_history = list(reversed(search_history))
            
            logger.info(f"📚 Loaded {len(search_history)} searches from history file")
            print(f"📚 Loaded {len(search_history)} searches from history file")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing search history JSON: {e}")
            print(f"❌ Error parsing search history JSON: {e}")
        except Exception as e:
            logger.error(f"Error loading search history: {e}")
            print(f"❌ Error loading search history: {e}")
    else:
        logger.info("No search history file found")
        print("📝 No search history file found - history will be created on first search")
    
    context = {
        'search_history': search_history,
        'total_searches': len(search_history)
    }
    
    return render(request, 'discovery_app/history.html', context)

