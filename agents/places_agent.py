"""
Places Agent - Fetches tourist attractions using Nominatim and Overpass API
"""
import requests
import time
import re
import random
from typing import List, Optional, Tuple, Dict


class PlacesAgent:
    """Child Agent 2: Handles tourist attraction suggestions for a given location"""
    
    def __init__(self):
        self.nominatim_base = "https://nominatim.openstreetmap.org/search"
        self.overpass_base = "https://overpass-api.de/api/interpreter"
        self.max_places = 5
    
    def get_coordinates(self, place_name: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates (latitude, longitude) for a place using Nominatim API
        
        Args:
            place_name: Name of the place
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        result = self.get_coordinates_with_details(place_name)
        if result:
            return result.get("coordinates")
        return None
    
    def get_coordinates_with_details(self, place_name: str) -> Optional[Dict]:
        """
        Get coordinates with geocoding details for a place using Nominatim API
        
        Args:
            place_name: Name of the place
            
        Returns:
            Dictionary with 'coordinates' tuple and 'info' dict, or None if not found
        """
        try:
            # For common city names, try to get more specific results
            # Some cities have the same name in different countries
            params = {
                "q": place_name,
                "format": "json",
                "limit": 5,  # Get more results to find the best match
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "Tourism-Agent/1.0"
            }
            
            response = requests.get(
                self.nominatim_base, 
                params=params, 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                # Try to find the best match
                # Prefer results that are cities/towns, not states
                # Also prefer results with higher importance (more populated/major cities)
                best_location = None
                best_score = -1
                
                # Major cities that might be returned as administrative boundaries
                major_cities = {
                    "london", "paris", "tokyo", "baku", "istanbul", "moscow", "cairo"
                }
                place_lower = place_name.lower().strip()
                
                for location in data:
                    place_type = location.get("type", "").lower()
                    place_class = location.get("class", "").lower()
                    importance = location.get("importance", 0)
                    display_name = location.get("display_name", "").lower()
                    
                    score = 0
                    # Prefer city/town over administrative
                    if place_type in ["city", "town"]:
                        score += 100
                    elif place_type == "village":
                        score += 50
                    elif place_class == "place":
                        score += 75
                    elif place_class == "boundary" and place_type == "administrative":
                        # Administrative boundaries can be cities too (like London, Baku)
                        # Give them a score based on importance and display_name structure
                        if place_lower in major_cities:
                            score += 90  # High score for known major cities
                        elif importance > 0.6:
                            # High importance administrative boundaries are likely major cities
                            score += 80
                        elif "city" in display_name or "town" in display_name:
                            # If display_name mentions city/town, it's likely a city
                            score += 70
                        elif importance > 0.4:
                            # Medium-high importance might be a city
                            score += 60
                        else:
                            # Low importance administrative = likely a region/state
                            score += 20
                    
                    # Add importance score (higher = more major city)
                    score += importance * 10
                    
                    # Bonus: if place name appears early in display_name, it's likely the city itself
                    if display_name and place_lower in display_name:
                        # Check position - if it's in the first part (before first comma), bonus points
                        first_part = display_name.split(",")[0].strip()
                        if place_lower in first_part:
                            score += 15
                    
                    # Prefer results with higher importance and correct type
                    if score > best_score:
                        best_score = score
                        best_location = location
                
                # If no good match found, use first result
                if not best_location:
                    best_location = data[0]
                
                location = best_location
                lat = float(location.get("lat", 0))
                lon = float(location.get("lon", 0))
                
                # Try to get English name if available
                # Check for "name:en" or prefer English in display_name
                display_name = location.get("display_name", "")
                name = location.get("name", "")
                
                # If display_name contains the original place name, try to extract English version
                # For places with non-English names, try to get a better name
                if "name:en" in location:
                    location["name"] = location["name:en"]
                elif name and not any(ord(char) > 127 for char in name):
                    # Name is already in ASCII (likely English)
                    pass
                else:
                    # Try to extract English name from display_name
                    # Display name format: "Name, City, State, Country"
                    if display_name:
                        parts = display_name.split(",")
                        if parts:
                            # First part is usually the name
                            first_part = parts[0].strip()
                            # If it contains non-ASCII, try to find English alternative
                            if any(ord(char) > 127 for char in first_part):
                                # Look for English name in other fields
                                for key in ["name:en", "name_en", "name"]:
                                    if key in location and location[key]:
                                        alt_name = location[key]
                                        if not any(ord(char) > 127 for char in alt_name):
                                            location["name"] = alt_name
                                            break
                
                return {
                    "coordinates": (lat, lon),
                    "info": location
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Geocoding API error: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing geocoding response: {e}")
            return None
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize place name for comparison (remove extra spaces, lowercase)
        
        Args:
            name: Place name to normalize
            
        Returns:
            Normalized name
        """
        return re.sub(r'\s+', ' ', name.strip().lower())
    
    def _is_similar(self, name1: str, name2: str) -> bool:
        """
        Check if two place names are similar (duplicates or variations)
        
        Args:
            name1: First place name
            name2: Second place name
            
        Returns:
            True if names are similar
        """
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # One contains the other (e.g., "Park" and "Central Park")
        if norm1 in norm2 or norm2 in norm1:
            # But not if one is too short (avoid matching "Park" with everything)
            if len(norm1) > 3 and len(norm2) > 3:
                return True
        
        # Check for common suffixes/prefixes that indicate same place
        # Remove common words and compare
        common_words = ['the', 'a', 'an', 'of', 'in', 'at']
        words1 = [w for w in norm1.split() if w not in common_words]
        words2 = [w for w in norm2.split() if w not in common_words]
        
        # If most words match, consider similar
        if len(words1) > 0 and len(words2) > 0:
            matches = sum(1 for w in words1 if w in words2)
            if matches >= min(len(words1), len(words2)) * 0.7:
                return True
        
        return False
    
    def _refine_places(self, places: List[str]) -> List[str]:
        """
        Remove duplicates and similar place names, keeping the best version
        
        Args:
            places: List of place names
            
        Returns:
            Refined list without duplicates
        """
        if not places:
            return []
        
        refined = []
        seen_places = {}  # Map normalized -> original place name
        
        for place in places:
            normalized = self._normalize_name(place)
            
            # Check if we've seen a similar name
            is_duplicate = False
            for seen_norm, seen_orig in seen_places.items():
                if self._is_similar(place, seen_orig):
                    is_duplicate = True
                    # Keep the longer/more descriptive name
                    if len(place) > len(seen_orig):
                        # Replace the old one
                        del seen_places[seen_norm]
                        refined = [p for p in refined if p != seen_orig]
                        refined.append(place)
                        seen_places[normalized] = place
                    break
            
            if not is_duplicate:
                refined.append(place)
                seen_places[normalized] = place
        
        return refined[:self.max_places]
    
    def get_tourist_attractions(self, latitude: float, longitude: float) -> List[str]:
        """
        Fetch tourist attractions near given coordinates using Overpass API
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            List of tourist attraction names (up to max_places, deduplicated)
        """
        try:
            # Overpass query to find tourist attractions within ~10km radius
            query = f"""
            [out:json][timeout:25];
            (
              node["tourism"~"^(attraction|museum|zoo|theme_park|gallery|monument|viewpoint)$"](around:10000,{latitude},{longitude});
              way["tourism"~"^(attraction|museum|zoo|theme_park|gallery|monument|viewpoint)$"](around:10000,{latitude},{longitude});
              relation["tourism"~"^(attraction|museum|zoo|theme_park|gallery|monument|viewpoint)$"](around:10000,{latitude},{longitude});
            );
            out center;
            """
            
            response = requests.post(
                self.overpass_base,
                data={"data": query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            places = []
            
            if "elements" in data:
                for element in data["elements"]:
                    tags = element.get("tags", {})
                    name = tags.get("name")
                    
                    if name and name.strip():
                        places.append(name.strip())
            
            # Refine and deduplicate places
            refined_places = self._refine_places(places)
            
            return refined_places[:self.max_places]
            
        except requests.exceptions.RequestException as e:
            print(f"Overpass API error: {e}")
            return []
        except (KeyError, ValueError) as e:
            print(f"Error parsing Overpass response: {e}")
            return []
    
    def format_places_response(self, places: List[str], place_name: str) -> str:
        """
        Format places list into a user-friendly response
        
        Args:
            places: List of place names
            place_name: Name of the location
            
        Returns:
            Formatted string response
        """
        if not places:
            return f"Unfortunately, I couldn't find many tourist attractions listed for {place_name}. This might be a remote location or the area may have limited tourist data available."
        
        # More conversational, personality-driven messages
        greetings = [
            f"Here are some amazing places in {place_name} you shouldn't miss!",
            f"Your adventure in {place_name} could start at these gems:",
            f"Discover these must-see spots in {place_name}:",
            f"Ready to explore {place_name}? Check out these places:",
            f"Here are five fantastic places to visit in {place_name}:"
        ]
        
        response = f"{random.choice(greetings)}\n\n"
        for i, place in enumerate(places, 1):
            response += f"- {place}\n"
        
        response += "\n💡 Tip: Click on any place to learn more about it!"
        
        return response.strip()
    
    def get_place_details(self, place_name: str, city_name: str = None) -> Optional[Dict]:
        """
        Get detailed information about a specific tourist attraction
        
        Args:
            place_name: Name of the tourist attraction
            city_name: Optional city name to narrow down search
            
        Returns:
            Dictionary with place details or None if not found
        """
        try:
            # Search for the place using Nominatim
            query = place_name
            if city_name:
                query = f"{place_name}, {city_name}"
            
            params = {
                "q": query,
                "format": "json",
                "limit": 5,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "Tourism-Agent/1.0"
            }
            
            response = requests.get(
                self.nominatim_base,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or len(data) == 0:
                return None
            
            # Find the best match (prefer tourism-related results)
            best_match = None
            best_score = -1
            
            for location in data:
                tags = location.get("tags", {})
                place_type = location.get("type", "").lower()
                place_class = location.get("class", "").lower()
                importance = location.get("importance", 0)
                
                score = 0
                # Prefer tourism-related places
                if place_class == "tourism" or "tourism" in str(tags).lower():
                    score += 100
                if place_class == "amenity" and place_type in ["museum", "gallery", "zoo", "theme_park"]:
                    score += 80
                if place_class == "historic":
                    score += 70
                
                # Check if name matches
                name = location.get("name", "").lower()
                place_lower = place_name.lower()
                if place_lower in name or name in place_lower:
                    score += 50
                
                score += importance * 10
                
                if score > best_score:
                    best_score = score
                    best_match = location
            
            if not best_match:
                best_match = data[0]
            
            # Get details from Overpass API using coordinates
            lat = float(best_match.get("lat", 0))
            lon = float(best_match.get("lon", 0))
            
            if lat == 0 and lon == 0:
                return None
            
            # Query Overpass for detailed information
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["name"~"{place_name}",i](around:1000,{lat},{lon});
              way["name"~"{place_name}",i](around:1000,{lat},{lon});
              relation["name"~"{place_name}",i](around:1000,{lat},{lon});
            );
            out body;
            """
            
            overpass_response = requests.post(
                self.overpass_base,
                data={"data": overpass_query},
                timeout=30
            )
            overpass_response.raise_for_status()
            overpass_data = overpass_response.json()
            
            # Extract information
            details = {
                "name": best_match.get("name", place_name),
                "display_name": best_match.get("display_name", ""),
                "latitude": lat,
                "longitude": lon
            }
            
            # Get tags from Overpass if available
            if "elements" in overpass_data and len(overpass_data["elements"]) > 0:
                element = overpass_data["elements"][0]
                tags = element.get("tags", {})
                
                details["description"] = tags.get("description") or tags.get("description:en")
                details["website"] = tags.get("website")
                details["phone"] = tags.get("phone")
                details["opening_hours"] = tags.get("opening_hours")
                details["fee"] = tags.get("fee")
                details["wikipedia"] = tags.get("wikipedia")
                details["wikipedia:en"] = tags.get("wikipedia:en")
                details["historic"] = tags.get("historic")
                details["heritage"] = tags.get("heritage")
                details["tourism"] = tags.get("tourism")
            
            # Also get tags from Nominatim result
            nominatim_tags = best_match.get("tags", {})
            if not details.get("description"):
                details["description"] = nominatim_tags.get("description") or nominatim_tags.get("description:en")
            if not details.get("website"):
                details["website"] = nominatim_tags.get("website")
            if not details.get("opening_hours"):
                details["opening_hours"] = nominatim_tags.get("opening_hours")
            
            return details
            
        except Exception as e:
            print(f"Error getting place details: {e}")
            return None
    
    def format_place_details_response(self, details: Dict) -> str:
        """
        Format place details into a user-friendly response
        
        Args:
            details: Dictionary with place details
            
        Returns:
            Formatted string response
        """
        if not details:
            return "Sorry, detailed information about this place is not currently available."
        
        name = details.get("name", "This place")
        response = f"**{name}**\n\n"
        
        # Add description if available
        description = details.get("description")
        if description:
            response += f"{description}\n\n"
        
        # Add location
        display_name = details.get("display_name", "")
        if display_name:
            # Extract city/area from display_name
            parts = display_name.split(",")
            if len(parts) > 0:
                location = parts[0].strip()
                if len(parts) > 1:
                    location += f", {parts[1].strip()}"
                response += f"📍 Location: {location}\n\n"
        
        # Add opening hours
        opening_hours = details.get("opening_hours")
        if opening_hours:
            response += f"🕐 Opening Hours: {opening_hours}\n\n"
        
        # Add fee information
        fee = details.get("fee")
        if fee:
            response += f"💰 Admission: {fee}\n\n"
        
        # Add heritage/UNESCO status
        heritage = details.get("heritage")
        historic = details.get("historic")
        if heritage:
            response += f"🏛️ Heritage Status: {heritage}\n\n"
        elif historic:
            response += f"🏛️ Historic Site: {historic}\n\n"
        
        # Add website
        website = details.get("website")
        if website:
            response += f"🌐 Website: {website}\n\n"
        
        # If no additional info, provide basic response
        if response == f"**{name}**\n\n":
            response += f"{name} is a notable tourist attraction"
            if display_name:
                parts = display_name.split(",")
                if len(parts) > 0:
                    response += f" located in {parts[0].strip()}"
            response += "."
        
        return response.strip()

