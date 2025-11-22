"""
Parent Tourism Agent - Orchestrates Weather and Places agents
"""
import re
import datetime
from typing import Dict, Optional, List
from agents.weather_agent import WeatherAgent
from agents.places_agent import PlacesAgent


class TourismAgent:
    """Parent Agent: Orchestrates the tourism system"""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
        self.greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    
    def extract_place_name(self, user_input: str) -> Optional[str]:
        """
        Extract place name from user input
        Handles various patterns including "whats the weather in [place]"
        
        Args:
            user_input: User's input text
            
        Returns:
            Extracted place name or None
        """
        user_lower = user_input.lower()
        original_input = user_input  # Keep original for capitalization
        
        # Pattern 1: "whats the weather in [place]" or "weather in [place]"
        weather_in_pattern = re.search(r'weather\s+(?:in|at|for)\s+([a-zA-Z\s]+?)(?:\s+like|\?|$|,|\.|what|where|how|and)', user_input, re.IGNORECASE)
        if weather_in_pattern:
            place = weather_in_pattern.group(1).strip()
            # Remove trailing question words and connectors but keep the full place name
            place = re.sub(r'\s+(and|what|where|how|is|the|like|can|i|visit|places).*$', '', place, flags=re.IGNORECASE).strip()
            if place and len(place) > 2:
                # Find the place name in original input preserving exact capitalization
                original_lower = original_input.lower()
                place_lower = place.lower()
                start_idx = original_lower.find(place_lower)
                if start_idx != -1:
                    # Extract from original preserving case
                    end_idx = start_idx + len(place)
                    extracted = original_input[start_idx:end_idx].strip()
                    # Clean up any trailing punctuation
                    extracted = re.sub(r'[,\?\.!]+$', '', extracted).strip()
                    if extracted:
                        return extracted
                return place.title()
        
        # Pattern 2: "In [Place], what places..." or "In [Place], what's the weather..."
        in_pattern = re.search(r'\bin\s+([A-Za-z][a-zA-Z\s]+?)(?:,|\?|$|what|where|how|can|i|visit|places|is|the|temperature|weather|and)', user_input, re.IGNORECASE)
        if in_pattern:
            place = in_pattern.group(1).strip()
            # Clean up trailing words but keep the full place name
            place = re.sub(r'\s+(and|what|where|how|can|i|visit|places|is|the|temperature|weather|like).*$', '', place, flags=re.IGNORECASE).strip()
            if place and len(place) > 2:
                # Find the place name in original input preserving exact capitalization
                original_lower = original_input.lower()
                place_lower = place.lower()
                start_idx = original_lower.find(place_lower)
                if start_idx != -1:
                    # Extract from original preserving case, but stop at comma/question mark
                    end_pos = len(original_input)
                    for stop_char in [',', '?', '!', '.']:
                        stop_idx = original_input.find(stop_char, start_idx)
                        if stop_idx != -1 and stop_idx < end_pos:
                            end_pos = stop_idx
                    extracted = original_input[start_idx:end_pos].strip()
                    # Clean up any trailing punctuation
                    extracted = re.sub(r'[,\?\.!]+$', '', extracted).strip()
                    if extracted:
                        return extracted
                return place.strip()
        
        # Pattern 3: "places to visit in [place]" or "places in [place]" or "places for [place]"
        places_in_pattern = re.search(r'places\s+(?:to\s+visit\s+)?(?:in|at|for|to|i\s+can\s+go\s+to)\s+([a-zA-Z\s]+?)(?:\?|$|,|\.|what|where|how|and)', user_input, re.IGNORECASE)
        if places_in_pattern:
            place = places_in_pattern.group(1).strip()
            # Remove trailing words including "and", "for" (if it appears after the place)
            place = re.sub(r'\s+(and|for|what|where|how|can|i|visit|places|is|the|like).*$', '', place, flags=re.IGNORECASE).strip()
            # Also handle case where "for" might be captured - remove it if it's just "for"
            if place.lower() == "for":
                # Try to get the actual place name after "for"
                after_for = re.search(r'places\s+(?:to\s+visit\s+)?for\s+([a-zA-Z\s]+?)(?:\?|$|,|\.|what|where|how|and)', user_input, re.IGNORECASE)
                if after_for:
                    place = after_for.group(1).strip()
                    place = re.sub(r'\s+(and|what|where|how|can|i|visit|places|is|the|like).*$', '', place, flags=re.IGNORECASE).strip()
            if place and len(place) > 2:
                # Find the place name in original input preserving exact capitalization
                original_lower = original_input.lower()
                place_lower = place.lower()
                start_idx = original_lower.find(place_lower)
                if start_idx != -1:
                    # Extract from original preserving case
                    end_pos = len(original_input)
                    for stop_char in [',', '?', '!', '.']:
                        stop_idx = original_input.find(stop_char, start_idx)
                        if stop_idx != -1 and stop_idx < end_pos:
                            end_pos = stop_idx
                    extracted = original_input[start_idx:end_pos].strip()
                    # Clean up any trailing punctuation
                    extracted = re.sub(r'[,\?\.!]+$', '', extracted).strip()
                    if extracted:
                        return extracted
                return place.title()
        
        # Pattern 4: Common patterns like "going to [place]"
        patterns = [
            ("going to go to", 1),
            ("going to", 1),
            ("travel to", 1),
            ("trip to", 1),
        ]
        
        for pattern, position in patterns:
            if pattern in user_lower:
                parts = user_lower.split(pattern, 1)
                if len(parts) > position:
                    place = parts[position].strip()
                    # Remove trailing punctuation and common words
                    place = re.sub(r'[,\.\?\!].*$', '', place).strip()
                    # Remove common trailing words but be more careful
                    stop_words = ["let's", "let", "plan", "my", "trip", "what", "is", "the", "temperature", "there", "and", "are", "places", "i", "can", "visit", "show", "me", "like"]
                    words = place.split()
                    filtered_words = []
                    for word in words:
                        if word not in stop_words:
                            filtered_words.append(word)
                        else:
                            break
                    if filtered_words:
                        # Preserve original capitalization
                        original_words = original_input.split()
                        matched = []
                        for orig_word in original_words:
                            if orig_word.lower() in [w.lower() for w in filtered_words]:
                                matched.append(orig_word)
                        if matched:
                            return " ".join(matched)
                        return " ".join(filtered_words).title()
        
        # Pattern 5: "temperature of [place]" or "temperature in [place]"
        temp_of_pattern = re.search(r'temperature\s+(?:of|in|at)\s+([a-zA-Z\s]+?)(?:\s+and|\s+n\s+|\s+places|\?|$|,|\.)', user_input, re.IGNORECASE)
        if temp_of_pattern:
            place = temp_of_pattern.group(1).strip()
            # Remove trailing words like "and", "places", "there", "n"
            place = re.sub(r'\s+(and|n|places|visit|there|to|the).*$', '', place, flags=re.IGNORECASE).strip()
            if place and len(place) > 2:
                # Find in original preserving case
                original_lower = original_input.lower()
                place_lower = place.lower()
                start_idx = original_lower.find(place_lower)
                if start_idx != -1:
                    # Stop before "and", "n", "places", etc.
                    end_pos = len(original_input)
                    for stop_word in [" and", " n ", " places", " visit", " there"]:
                        stop_idx = original_lower.find(stop_word, start_idx)
                        if stop_idx != -1 and stop_idx < end_pos:
                            end_pos = stop_idx
                    extracted = original_input[start_idx:end_pos].strip()
                    if extracted:
                        return extracted
                return place.title()
        
        # Pattern 6: Simple place name with keyword (e.g., "dubai temperature", "paris weather", "tokyo places")
        # Handle typos in keywords too (temperture, temprature, etc.)
        # Also handle "n" as "and"
        keywords_pattern = r'(?:temperat?u?r?e?|weather|places|visit|attractions|tourist)'
        simple_pattern = re.search(r'^([A-Za-z][a-zA-Z\s]+?)\s+(?:' + keywords_pattern + r'|\s+n\s+)', user_input, re.IGNORECASE)
        if simple_pattern:
            place = simple_pattern.group(1).strip()
            # Clean up trailing spaces
            place = place.strip()
            if place and len(place) > 2:
                # Find the place name in original input - stop before the keyword
                original_lower = original_input.lower()
                place_lower = place.lower()
                start_idx = original_lower.find(place_lower)
                if start_idx != -1:
                    # Find where keyword starts (temperature, weather, etc.) or "n" or "and"
                    keyword_match = re.search(r'\s+(?:temperat?u?r?e?|weather|places|visit|attractions|tourist|\s+n\s+|\s+and\s+)', original_lower[start_idx:], re.IGNORECASE)
                    if keyword_match:
                        end_pos = start_idx + keyword_match.start()
                        extracted = original_input[start_idx:end_pos].strip()
                        if extracted:
                            return extracted
                    else:
                        # No keyword found, just return the place
                        extracted = original_input[start_idx:start_idx + len(place)].strip()
                        if extracted:
                            return extracted
                return place.title()
        
        # Pattern 7: Just a place name with optional punctuation (e.g., "dubai", "dubai?", "paris!")
        # This should be a simple query - just extract the first significant word(s)
        words = original_input.split()
        if len(words) == 1 or (len(words) == 2 and words[1].lower() in ["temperature", "weather", "places", "?"]):
            # Single word or place name + keyword
            place = words[0]
            # Remove punctuation
            place = re.sub(r'[,\?\.!]+$', '', place).strip()
            if place and len(place) > 2 and place[0].isalpha():
                # Check if it's not a common word
                common_words = ["what", "where", "how", "when", "why", "the", "a", "an", "is", "are", "can", "i", "more"]
                if place.lower() not in common_words:
                    return place.title() if place[0].islower() else place
        
        # Pattern 8: Place name followed by question mark or keyword (e.g., "dubai?", "delhi temperature")
        question_pattern = re.search(r'^([A-Za-z][a-zA-Z\s]+?)(?:\?|!|$)', user_input, re.IGNORECASE)
        if question_pattern and len(words) <= 2:
            place = question_pattern.group(1).strip()
            place = re.sub(r'[,\?\.!]+$', '', place).strip()
            if place and len(place) > 2:
                common_words = ["what", "where", "how", "when", "why", "the", "a", "an", "is", "are", "can", "i", "more"]
                if place.lower() not in common_words:
                    return place.title() if place[0].islower() else place
        
        # Pattern 9: Extract capitalized words (city names usually start with capital)
        # But stop before words like "and", "n", "places", "visit", "there"
        words = original_input.split()
        capitalized_words = []
        stop_words_lower = ["what", "is", "the", "weather", "in", "at", "for", "like", "places", "to", "visit", "can", "i", "go", "temperature", "more", "and", "n", "there", "also"]
        for word in words:
            word_lower = word.lower()
            # Stop if we hit a stop word after finding a place name
            if word_lower in stop_words_lower:
                if capitalized_words:
                    break
                continue
            if word and word[0].isupper() and word.isalpha():
                capitalized_words.append(word)
            elif capitalized_words and word.isalpha() and word_lower not in stop_words_lower:
                # Continue if it's part of a multi-word place name
                capitalized_words.append(word)
            elif capitalized_words:
                break
        
        if capitalized_words:
            return " ".join(capitalized_words)
        
        # Pattern 10: Last resort - try to find any word that looks like a place name
        # (starts with letter, not a common word, at least 3 characters)
        # But stop before "and", "n", "places", "visit", "there"
        for i, word in enumerate(words):
            cleaned = re.sub(r'[,\?\.!]+$', '', word).strip()
            if len(cleaned) >= 3 and cleaned[0].isalpha():
                common_words = ["what", "where", "how", "when", "why", "the", "a", "an", "is", "are", "can", "i", "more", "temperature", "weather", "places", "visit", "and", "n", "there", "also"]
                if cleaned.lower() not in common_words:
                    # Check if next word is a stop word - if so, this is likely the place name
                    if i + 1 < len(words):
                        next_word = words[i + 1].lower()
                        if next_word in ["and", "n", "places", "visit", "there", "temperature", "weather"]:
                            return cleaned.title() if cleaned[0].islower() else cleaned
                    return cleaned.title() if cleaned[0].islower() else cleaned
        
        return None
    
    def determine_intent(self, user_input: str) -> Dict[str, bool]:
        """
        Determine what the user wants: weather, places, or both
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with 'weather', 'places', 'timing', and 'place_detail' boolean flags
        """
        user_lower = user_input.lower()
        
        # Check for place detail queries (asking about a specific attraction)
        place_detail_keywords = ["tell me about", "information about", "details about", "what is", "tell me more", "about", "info"]
        wants_place_detail = any(keyword in user_lower for keyword in place_detail_keywords)
        
        # Check for timing queries (not supported)
        timing_keywords = ["timing", "hours", "open", "closed", "schedule", "when", "time to visit", "visiting hours", "opening hours"]
        wants_timing = any(keyword in user_lower for keyword in timing_keywords)
        
        # Check for weather queries - handle typos too (temperture, temprature, etc.)
        weather_keywords = ["temperature", "temperture", "temprature", "temp", "weather", "rain", "forecast", "climate", "hot", "cold", "degrees"]
        wants_weather = any(keyword in user_lower for keyword in weather_keywords)
        
        # Check for places queries - more comprehensive
        places_keywords = ["places", "visit", "attractions", "tourist", "go", "see", "sightseeing", "sights", "landmarks", "what to see", "where to go"]
        wants_places = any(keyword in user_lower for keyword in places_keywords)
        
        # If query explicitly asks "what places" or "where to visit", prioritize places
        if any(phrase in user_lower for phrase in ["what places", "where to", "places to", "places can", "places i", "attractions"]):
            wants_places = True
        
        # IMPORTANT: If user explicitly asks for weather ONLY, don't return places
        # Check for explicit weather-only queries
        if wants_weather and not wants_places:
            # User wants weather only
            wants_places = False
        
        # If neither is explicitly mentioned, check context
        if not wants_weather and not wants_places and not wants_place_detail:
            # If it's a general query about a place, assume both
            if any(word in user_lower for word in ["going", "trip", "travel", "plan"]):
                wants_weather = True
                wants_places = True
            elif len(user_lower.split()) <= 3:
                # Short queries like "dubai" or "dubai?" - default to places
                wants_places = True
            else:
                # Default to places if no specific intent
                wants_places = True
        
        return {
            "weather": wants_weather,
            "places": wants_places,
            "timing": wants_timing,
            "place_detail": wants_place_detail
        }
    
    def extract_place_detail_query(self, user_input: str) -> Optional[str]:
        """
        Extract the place name from a place detail query
        e.g., "tell me about Qutub Minar" -> "Qutub Minar"
        
        Args:
            user_input: User's input text
            
        Returns:
            Extracted place name or None
        """
        user_lower = user_input.lower()
        
        # Patterns for place detail queries
        patterns = [
            r'tell me (?:more )?about (.+?)(?:\?|$|\.|,|please)',
            r'information about (.+?)(?:\?|$|\.|,|please)',
            r'details about (.+?)(?:\?|$|\.|,|please)',
            r'what is (.+?)(?:\?|$|\.|,|please)',
            r'tell me (.+?)(?:\?|$|\.|,|please)',
            r'about (.+?)(?:\?|$|\.|,|please)',
            r'info (.+?)(?:\?|$|\.|,|please)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                place = match.group(1).strip()
                # Remove common trailing words
                place = re.sub(r'\s+(please|thanks|thank you|tell me|more|info).*$', '', place, flags=re.IGNORECASE).strip()
                if place and len(place) > 2:
                    return place
        
        # If no pattern matches, check if it's a simple query without keywords
        # This handles cases like "Qutub Minar" after seeing it in a list
        words = user_input.split()
        if len(words) >= 2 and len(words) <= 5:
            # Likely a place name
            capitalized_words = [w for w in words if w and w[0].isupper()]
            if capitalized_words:
                return " ".join(capitalized_words)
        
        return None
    
    def is_greeting(self, user_input: str) -> bool:
        """
        Check if user input is a greeting (but not a query with a place name)
        
        Args:
            user_input: User's input text
            
        Returns:
            True if input is a greeting
        """
        user_lower = user_input.lower().strip()
        
        # Don't treat as greeting if it contains weather/places keywords or place names
        if any(keyword in user_lower for keyword in ["weather", "temperature", "places", "visit", "attractions", "in ", "at "]):
            return False
        
        # Check if it's just a greeting
        return any(greeting == user_lower or user_lower.startswith(greeting + " ") for greeting in self.greetings)
    
    def is_goodbye(self, user_input: str) -> bool:
        """
        Check if user input is a goodbye/exit statement
        
        Args:
            user_input: User's input text
            
        Returns:
            True if input is a goodbye/exit
        """
        user_lower = user_input.lower().strip()
        goodbye_phrases = [
            "bye", "goodbye", "see you", "see ya", "farewell", "exit", 
            "quit", "close", "thanks", "thank you", "thank", "thx", 
            "appreciate it", "that's all", "that's it", "done", "finished"
        ]
        
        # Check if it's a goodbye phrase
        return any(phrase == user_lower or user_lower.startswith(phrase + " ") or user_lower.endswith(" " + phrase) for phrase in goodbye_phrases)
    
    def split_multiple_queries(self, user_input: str) -> List[str]:
        """
        Split user input into multiple queries if they contain multiple questions
        
        Args:
            user_input: User's input text
            
        Returns:
            List of individual queries
        """
        # Split by common separators - handle "also" specially
        # Pattern: "also tell me" or "also" at start of sentence
        user_lower = user_input.lower()
        
        # Check for "also" pattern
        if ' also ' in user_lower or user_lower.startswith('also '):
            # Split on "also" but keep the context
            parts = re.split(r'\s+also\s+', user_input, flags=re.IGNORECASE)
            if len(parts) > 1:
                # First part is the main query
                # Second part might need the place name from first part
                queries = [parts[0].strip()]
                # For subsequent parts, they might reference the same place
                for part in parts[1:]:
                    part = part.strip()
                    if part:
                        queries.append(part)
                return queries
        
        # Split by other common separators
        separators = [' and ', ' & ', ' plus ', '?', '!']
        queries = [user_input]
        
        for sep in separators:
            new_queries = []
            for query in queries:
                if sep in query.lower():
                    parts = re.split(re.escape(sep), query, flags=re.IGNORECASE)
                    new_queries.extend([p.strip() for p in parts if p.strip()])
                else:
                    new_queries.append(query)
            queries = new_queries
        
        return queries
    
    def check_if_state_or_region(self, place_name: str, geocoding_result: dict) -> bool:
        """
        Check if the place is a state/region/country rather than a city
        Be very conservative - only flag obvious states/regions/countries
        
        Args:
            place_name: Name of the place
            geocoding_result: Result from Nominatim API
            
        Returns:
            True if it appears to be a state/region/country
        """
        place_type = geocoding_result.get("type", "").lower()
        place_class = geocoding_result.get("class", "").lower()
        display_name = geocoding_result.get("display_name", "").lower()
        place_lower = place_name.lower()
        
        # Whitelist of well-known major cities that might be returned as administrative boundaries
        # These are definitely cities, not regions
        major_cities = {
            "london", "paris", "tokyo", "baku", "istanbul", "moscow", "cairo", 
            "delhi", "mumbai", "bangalore", "kolkata", "chennai", "hyderabad",
            "new york", "los angeles", "chicago", "houston", "phoenix",
            "sydney", "melbourne", "toronto", "vancouver", "montreal",
            "berlin", "madrid", "rome", "amsterdam", "vienna", "prague",
            "dubai", "riyadh", "doha", "singapore", "hong kong", "seoul",
            "beijing", "shanghai", "bangkok", "jakarta", "manila",
            "mexico city", "sao paulo", "rio de janeiro", "buenos aires",
            "lagos", "nairobi", "johannesburg", "cape town"
        }
        
        # Check if the place name (normalized) is in our major cities whitelist
        normalized_place = place_lower.strip()
        if normalized_place in major_cities:
            return False  # It's a known major city, treat as city
        
        # Also check if display_name contains the place name followed by common city indicators
        # This handles cases like "London, Greater London, England"
        city_patterns = [
            f"{place_lower},",  # Place name followed by comma (common in city listings)
            f", {place_lower},",  # Place name in middle of address
        ]
        for pattern in city_patterns:
            if pattern in display_name:
                # If it appears early in the display_name, it's likely a city
                if display_name.index(pattern) < 50:  # Within first 50 chars
                    return False
        
        # If display_name contains "city" or "town" with the place name, it's a city
        if ("city" in display_name or "town" in display_name) and place_lower in display_name:
            return False
        
        # If it's explicitly marked as a city/town/village, it's not a state
        city_indicators = ["city", "town", "village", "municipality", "suburb"]
        if any(indicator in place_type or indicator in place_class for indicator in city_indicators):
            return False
        
        # Check for country - only flag if it's clearly a country
        if place_class == "boundary" and place_type == "administrative":
            # Check if display_name explicitly says it's a country
            if "country" in display_name and place_lower in display_name:
                importance = geocoding_result.get("importance", 0)
                # Countries have very high importance (>0.8)
                if importance > 0.8:
                    return True
        
        # Check for state/province - be more conservative
        if "administrative" in place_type and place_class == "administrative":
            # Only flag as region if:
            # 1. It's NOT in the first part of display_name (cities appear first)
            # 2. Importance is moderate (0.4-0.7) - too high means country, too low means city
            # 3. Display name doesn't contain city/town indicators
            importance = geocoding_result.get("importance", 0)
            
            # If importance is very high (>0.8), it might be a country - but we already checked that
            # If importance is very low (<0.4), it's likely a small city/town
            # Only flag if importance is in the middle range AND display_name structure suggests region
            if 0.4 <= importance <= 0.7:
                # Check if the place name appears AFTER a comma in display_name
                # Cities usually appear first: "City, Region, Country"
                # Regions usually appear second: "Region, Country"
                parts = display_name.split(",")
                if len(parts) > 1:
                    first_part = parts[0].strip().lower()
                    # If place name is NOT in first part, it might be a region
                    if place_lower not in first_part:
                        # But check if any part contains city indicators
                        if not any("city" in part or "town" in part for part in parts):
                            return True
        
        # Very conservative - default to False (treat as city)
        return False
    
    def process_query(self, user_input: str) -> str:
        """
        Main method to process user query and return response
        
        Args:
            user_input: User's input text
            
        Returns:
            Formatted response string
        """
        user_input = user_input.strip()
        
        # Handle goodbyes/exits
        if self.is_goodbye(user_input):
            return ("👋 Goodbye! It was great helping you plan your trip. Safe travels and enjoy your journey! 🌍✈️")
        
        # Handle greetings
        if self.is_greeting(user_input):
            hour = datetime.datetime.now().hour
            time_greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
            
            return (f"{time_greeting}! 👋 I'm your travel planning assistant!\n\n"
                   "I can help you with:\n"
                   "- 🌤️ Current weather and forecasts\n"
                   "- 📍 Must-see attractions and hidden gems\n\n"
                   "Where would you like to explore? Try asking:\n"
                   "- 'What's the weather in Bangalore?'\n"
                   "- 'What places can I visit in Paris?'\n"
                   "- 'Tell me about Tokyo - weather and places!'")
        
        # Handle empty or very short inputs
        if len(user_input) < 3:
            return ("I need more information to help you. Please tell me:\n"
                   "- A place name (e.g., 'Bangalore', 'Paris', 'New York')\n"
                   "- What you'd like to know (weather, places to visit, or both)")
        
        # Check for timing queries first (not supported)
        intent_check = self.determine_intent(user_input)
        if intent_check.get("timing"):
            return ("I understand you're asking about visiting hours or timings. Unfortunately, the data source I use (Overpass API) doesn't provide timing information for tourist attractions.\n\n"
                   "For visiting hours, I recommend:\n"
                   "- Checking the official website of the attraction\n"
                   "- Using Google Maps or similar services\n"
                   "- Contacting local tourism offices\n\n"
                   "I can still help you with weather information and suggest places to visit!")
        
        # Check for place detail queries (asking about a specific attraction)
        if intent_check.get("place_detail"):
            place_detail_name = self.extract_place_detail_query(user_input)
            if place_detail_name:
                # Try to get place details
                details = self.places_agent.get_place_details(place_detail_name)
                if details:
                    return self.places_agent.format_place_details_response(details)
                else:
                    return f"Sorry, detailed information about '{place_detail_name}' is not currently available. Please try asking about a different place or check the official website for more information."
            else:
                return "I'd be happy to provide information about a specific place! Please tell me which tourist attraction you'd like to know more about. For example: 'Tell me about Qutub Minar' or 'What is the Eiffel Tower?'"
        
        # Extract place name
        place_name = self.extract_place_name(user_input)
        
        if not place_name:
            return ("I couldn't find a valid place name in your query. Please provide a place name like:\n"
                   "- 'Dubai'\n"
                   "- 'Dubai temperature'\n"
                   "- 'What's the weather in Paris?'\n"
                   "- 'In Bangalore, what places can I visit?'\n"
                   "- 'Show me places to visit in Tokyo'")
        
        # Get coordinates and geocoding info for the place
        geocoding_data = self.places_agent.get_coordinates_with_details(place_name)
        
        if not geocoding_data:
            return f"I don't know if '{place_name}' exists. Could you please provide a valid place name?"
        
        coordinates = geocoding_data.get("coordinates")
        geocoding_info = geocoding_data.get("info", {})
        
        if not coordinates:
            return f"I don't know if '{place_name}' exists. Could you please provide a valid place name?"

        lat, lon = coordinates
        
        # Get proper place name from geocoding for consistent formatting
        # Prefer English name, fallback to name, then display_name, then original
        proper_place_name = geocoding_info.get("name:en") or geocoding_info.get("name_en") or geocoding_info.get("name", place_name)
        
        # If name contains non-ASCII characters (like Arabic), try to get English version
        if proper_place_name and any(ord(char) > 127 for char in proper_place_name):
            # Try display_name - usually has English version
            display_name = geocoding_info.get("display_name", "")
            if display_name:
                # Extract first part before comma (usually the city name)
                parts = display_name.split(",")
                for part in parts:
                    part = part.strip()
                    # Check if this part is in ASCII (English)
                    if part and not any(ord(char) > 127 for char in part):
                        proper_place_name = part
                        break
        
        # Clean up place name - remove "(urban)" or similar suffixes
        if proper_place_name:
            proper_place_name = re.sub(r'\s*\([^)]+\)\s*$', '', proper_place_name).strip()
        
        if not proper_place_name or len(proper_place_name) < 2:
            proper_place_name = place_name.title()
        
        # Check if it's a state/region/country
        is_state_or_region = self.check_if_state_or_region(proper_place_name, geocoding_info)
        if is_state_or_region:
            return (f"I found '{proper_place_name}', but it appears to be a country, state, or region rather than a specific city.\n\n"
                   f"Please specify a city within {proper_place_name} for more accurate weather and attraction information.\n\n"
                   "For example:\n"
                   "- If you meant Karnataka, try 'Bangalore' or 'Mysore'\n"
                   "- If you meant California, try 'Los Angeles' or 'San Francisco'\n"
                   "- If you meant India, try 'Mumbai' or 'Delhi'")
        
        # Determine user intent
        intent = self.determine_intent(user_input)
        
        responses = []
        
        # Get weather if requested
        if intent["weather"]:
            weather_data = self.weather_agent.get_weather(lat, lon)
            if weather_data:
                weather_response = self.weather_agent.format_weather_response(weather_data, proper_place_name)
                responses.append(weather_response)
        
        # Get places if requested (ONLY if user explicitly asked for places OR didn't specify)
        # If user asked ONLY for weather, don't return places
        if intent["places"]:
            places = self.places_agent.get_tourist_attractions(lat, lon)
            if places:
                places_response = self.places_agent.format_places_response(places, proper_place_name)
                responses.append(places_response)
            elif intent["places"]:
                # If places were requested but none found
                # Re-check if it might be a state/region/country that slipped through
                importance = geocoding_info.get("importance", 0)
                place_type = geocoding_info.get("type", "").lower()
                place_class = geocoding_info.get("class", "").lower()
                display_name = geocoding_info.get("display_name", "").lower()
                place_lower = proper_place_name.lower()
                
                # Check if it's likely a state/region/country
                is_likely_region = False
                
                # Method 1: Check if it's an administrative boundary
                if place_class == "boundary" and place_type == "administrative":
                    # Administrative boundaries with moderate to high importance are likely states/regions
                    if importance >= 0.4:  # Lower threshold to catch more states
                        # Check if place name doesn't appear first in display_name
                        # Cities appear first: "City, State, Country"
                        # States appear later: "State, Country"
                        parts = display_name.split(",")
                        if len(parts) > 1:
                            first_part = parts[0].strip().lower()
                            # If the place name is NOT in the first part, it's likely a state/region
                            if place_lower not in first_part:
                                is_likely_region = True
                            # Also check if first part contains city indicators
                            elif "city" in first_part or "town" in first_part:
                                is_likely_region = False  # It's a city
                
                # Method 2: Check display_name structure for common state/country patterns
                if not is_likely_region:
                    # Common state/country keywords in display_name
                    region_keywords = ["state", "province", "region", "country", "republic", "kingdom"]
                    if any(keyword in display_name for keyword in region_keywords):
                        # But check if it's actually a city with these words in the name
                        parts = display_name.split(",")
                        if len(parts) > 1:
                            first_part = parts[0].strip().lower()
                            # If place name is in first part, it might still be a city
                            if place_lower not in first_part:
                                # Check if any part after first contains the place name with region keywords
                                for part in parts[1:]:
                                    if place_lower in part.lower() and any(kw in part.lower() for kw in region_keywords):
                                        is_likely_region = True
                                        break
                
                # Method 3: Check if it's a known state/country name pattern
                # States often have names like "West Bengal", "Uttar Pradesh", etc.
                if not is_likely_region:
                    # Check if importance is high but no city indicators
                    if importance >= 0.5 and place_class == "boundary":
                        if "city" not in display_name and "town" not in display_name:
                            # Check if display_name structure suggests state (appears after comma)
                            parts = display_name.split(",")
                            if len(parts) >= 2:
                                # If place name appears in second or later part, might be state
                                found_in_first = False
                                for i, part in enumerate(parts):
                                    if place_lower in part.lower():
                                        if i == 0:
                                            found_in_first = True
                                        break
                                if not found_in_first:
                                    is_likely_region = True
                
                # Additional check: If importance is very high (>0.7) and it's administrative, likely country
                if not is_likely_region and importance > 0.7 and place_class == "boundary" and place_type == "administrative":
                    # Check if it's likely a country (appears in last part of display_name usually)
                    parts = display_name.split(",")
                    if len(parts) >= 2:
                        last_part = parts[-1].strip().lower()
                        if place_lower in last_part or importance > 0.8:
                            is_likely_region = True
                
                # Additional check: Common country/state names
                common_countries = {"india", "nepal", "china", "usa", "united states", "uk", "united kingdom", "france", "germany", "japan", "australia", "canada", "brazil", "russia"}
                common_states = {"west bengal", "karnataka", "maharashtra", "tamil nadu", "gujarat", "rajasthan", "punjab", "california", "texas", "new york", "florida"}
                
                if place_lower in common_countries or place_lower in common_states:
                    is_likely_region = True
                
                if is_likely_region or is_state_or_region:
                    return (f"I found '{proper_place_name}', but it appears to be a country, state, or region rather than a specific city.\n\n"
                           f"Please enter a city name instead. For example, if you're looking for places in {proper_place_name}, try:\n"
                           "- 'Mumbai' or 'Delhi' (for India)\n"
                           "- 'Kolkata' or 'Darjeeling' (for West Bengal)\n"
                           "- 'Los Angeles' or 'San Francisco' (for California)")
                else:
                    # It's a city but no places found - no data message
                    return f"Sorry, detailed tourist attraction data is not currently available for {proper_place_name}. Please try searching for a nearby major city or a different location."
        
        # Combine responses with consistent formatting
        if responses:
            # If we have both weather and places, format nicely
            if len(responses) == 2:
                weather_resp = responses[0] if "currently" in responses[0] else responses[1]
                places_resp = responses[1] if "currently" in responses[0] else responses[0]
                
                if "currently" in weather_resp and "places you can go" in places_resp:
                    # Lowercase the first word "In" in the places response
                    if places_resp.startswith("In "):
                        places_resp = "in " + places_resp[3:]
                    return f"{weather_resp}. And {places_resp}"
            
            return " ".join(responses)
        
        # Fallback
        return f"Unable to fetch information for {proper_place_name}. Please try rephrasing your query."

