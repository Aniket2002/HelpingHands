"""
Intelligent therapist matching algorithm for MindBridge.
This service provides personalized therapist recommendations based on 
client preferences, needs, and compatibility factors.
"""

from typing import List, Dict, Tuple
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import TherapistProfile, ClientPreferences, MatchingScore
import math

User = get_user_model()

class TherapistMatchingService:
    """
    Advanced matching algorithm that considers multiple factors:
    - Specialization compatibility
    - Therapy approach alignment  
    - Availability matching
    - Personal preferences (gender, age, language)
    - Budget/insurance compatibility
    - Geographic proximity
    - Previous client ratings
    """
    
    def __init__(self):
        self.weights = {
            'specialization': 0.25,  # Most important factor
            'approach': 0.20,        # Therapy method compatibility
            'availability': 0.15,    # Scheduling compatibility
            'preferences': 0.15,     # Personal preferences
            'budget': 0.10,          # Financial considerations
            'rating': 0.10,          # Quality/experience
            'urgency': 0.05,         # Urgency adjustment
        }
    
    def find_matches(self, client_user, limit=10) -> List[Dict]:
        """
        Find best therapist matches for a client.
        
        Args:
            client_user: User object for the client
            limit: Maximum number of matches to return
            
        Returns:
            List of dictionaries containing therapist info and match scores
        """
        try:
            client_prefs = ClientPreferences.objects.get(user=client_user)
        except ClientPreferences.DoesNotExist:
            # Return basic matches if no preferences set
            return self._get_basic_matches(limit)
        
        # Get all available therapists
        available_therapists = TherapistProfile.objects.filter(
            is_accepting_clients=True,
            user__is_active=True
        ).select_related('user')
        
        matches = []
        
        for therapist_profile in available_therapists:
            score_data = self._calculate_match_score(client_prefs, therapist_profile)
            
            # Store/update matching score in database
            matching_score, created = MatchingScore.objects.update_or_create(
                client=client_user,
                therapist=therapist_profile.user,
                defaults=score_data
            )
            
            matches.append({
                'therapist': therapist_profile,
                'score': score_data['overall_score'],
                'score_breakdown': {
                    'specialization': score_data['specialization_score'],
                    'approach': score_data['approach_score'],
                    'availability': score_data['availability_score'],
                    'preferences': score_data['preference_score'],
                    'budget': score_data['price_score'],
                    'rating': therapist_profile.rating,
                },
                'match_reasons': self._generate_match_reasons(client_prefs, therapist_profile)
            })
        
        # Sort by overall score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
    
    def _calculate_match_score(self, client_prefs: ClientPreferences, 
                              therapist_profile: TherapistProfile) -> Dict[str, float]:
        """Calculate comprehensive matching score between client and therapist."""
        
        # 1. Specialization Score
        specialization_score = self._calculate_specialization_score(
            client_prefs.preferred_specializations,
            therapist_profile.specializations
        )
        
        # 2. Therapy Approach Score
        approach_score = self._calculate_approach_score(
            client_prefs.preferred_therapy_approaches,
            therapist_profile.therapy_approaches
        )
        
        # 3. Availability Score
        availability_score = self._calculate_availability_score(
            client_prefs.preferred_times,
            therapist_profile.availability
        )
        
        # 4. Personal Preferences Score
        preference_score = self._calculate_preference_score(
            client_prefs, therapist_profile
        )
        
        # 5. Budget/Price Score
        price_score = self._calculate_price_score(
            float(client_prefs.budget_max) if client_prefs.budget_max else None,
            float(therapist_profile.rate_per_session),
            client_prefs.insurance_provider,
            therapist_profile.accepts_insurance
        )
        
        # 6. Rating/Quality Score
        rating_score = min(therapist_profile.rating / 5.0, 1.0)
        
        # 7. Urgency Adjustment
        urgency_multiplier = self._get_urgency_multiplier(client_prefs.urgency)
        
        # Calculate weighted overall score
        overall_score = (
            specialization_score * self.weights['specialization'] +
            approach_score * self.weights['approach'] +
            availability_score * self.weights['availability'] +
            preference_score * self.weights['preferences'] +
            price_score * self.weights['budget'] +
            rating_score * self.weights['rating']
        ) * urgency_multiplier
        
        return {
            'overall_score': round(overall_score, 3),
            'specialization_score': round(specialization_score, 3),
            'approach_score': round(approach_score, 3),
            'availability_score': round(availability_score, 3),
            'preference_score': round(preference_score, 3),
            'price_score': round(price_score, 3),
            'distance_score': 0.0,  # Placeholder for future geo features
        }
    
    def _calculate_specialization_score(self, client_specializations: List[str], 
                                      therapist_specializations: List[str]) -> float:
        """Calculate how well therapist specializations match client needs."""
        if not client_specializations:
            return 0.8  # Neutral score if no preferences
        
        if not therapist_specializations:
            return 0.3  # Low score for therapists without specializations
        
        matches = set(client_specializations) & set(therapist_specializations)
        if not matches:
            return 0.2  # Low but not zero for potential flexibility
        
        # Higher score for more overlapping specializations
        overlap_ratio = len(matches) / len(client_specializations)
        return min(0.2 + (overlap_ratio * 0.8), 1.0)
    
    def _calculate_approach_score(self, client_approaches: List[str], 
                                therapist_approaches: List[str]) -> float:
        """Calculate therapy approach compatibility."""
        if not client_approaches:
            return 0.7  # Neutral if no approach preference
        
        if not therapist_approaches:
            return 0.4  # Lower score for no specified approaches
        
        matches = set(client_approaches) & set(therapist_approaches)
        if matches:
            overlap_ratio = len(matches) / len(client_approaches)
            return min(0.3 + (overlap_ratio * 0.7), 1.0)
        
        return 0.3  # Some compatibility possible
    
    def _calculate_availability_score(self, client_times: List[str], 
                                    therapist_availability: Dict) -> float:
        """Calculate scheduling compatibility."""
        if not client_times or not therapist_availability:
            return 0.6  # Neutral score
        
        # Simplified availability matching
        # In real implementation, this would check specific time slots
        available_times = therapist_availability.get('preferred_times', [])
        if not available_times:
            return 0.5
        
        matches = set(client_times) & set(available_times)
        if matches:
            return min(0.4 + (len(matches) / len(client_times) * 0.6), 1.0)
        
        return 0.3
    
    def _calculate_preference_score(self, client_prefs: ClientPreferences, 
                                  therapist_profile: TherapistProfile) -> float:
        """Calculate personal preference compatibility."""
        score = 0.0
        factors = 0
        
        # Gender preference
        if client_prefs.therapist_gender_preference:
            factors += 1
            # Note: gender field would need to be added to CustomUser model
            # For now, skip gender matching or use a default score
            score += 0.7  # Neutral score when gender field not available
        
        # Language preference
        if client_prefs.preferred_languages:
            factors += 1
            client_langs = set(client_prefs.preferred_languages)
            therapist_langs = set(therapist_profile.languages_spoken)
            if client_langs & therapist_langs:
                score += 1.0
            else:
                score += 0.3  # Partial credit
        
        # Age group compatibility
        if client_prefs.age_preference:
            factors += 1
            # Simplified age matching logic
            if therapist_profile.years_of_experience >= 5:
                score += 0.8
            else:
                score += 0.6
        
        return score / factors if factors > 0 else 0.7
    
    def _calculate_price_score(self, client_budget: float | None, therapist_rate: float, 
                             client_insurance: str, accepts_insurance: bool) -> float:
        """Calculate budget/insurance compatibility."""
        if client_insurance and accepts_insurance:
            return 1.0  # Perfect match with insurance
        
        if not client_budget:
            return 0.6  # Neutral if no budget specified
        
        if therapist_rate <= client_budget:
            # Higher score for rates well within budget
            ratio = therapist_rate / client_budget
            return 1.0 - (ratio * 0.3)  # Score decreases as rate approaches budget
        else:
            # Lower score for rates over budget, but not zero
            over_ratio = (therapist_rate - client_budget) / client_budget
            return max(0.1, 0.5 - (over_ratio * 0.4))
    
    def _get_urgency_multiplier(self, urgency: str) -> float:
        """Adjust scores based on client urgency."""
        multipliers = {
            'low': 1.0,
            'medium': 1.05,
            'high': 1.1,
            'crisis': 1.2
        }
        return multipliers.get(urgency, 1.0)
    
    def _generate_match_reasons(self, client_prefs: ClientPreferences, 
                              therapist_profile: TherapistProfile) -> List[str]:
        """Generate human-readable reasons for the match."""
        reasons = []
        
        # Specialization matches
        spec_matches = (set(client_prefs.preferred_specializations) & 
                       set(therapist_profile.specializations))
        if spec_matches:
            spec_names = [dict(TherapistProfile.SPECIALIZATIONS).get(spec, spec) 
                         for spec in spec_matches if spec is not None]
            spec_names = [name for name in spec_names if name is not None]
            if spec_names:
                reasons.append(f"Specializes in {', '.join(spec_names)}")
        
        # Approach matches
        approach_matches = (set(client_prefs.preferred_therapy_approaches) & 
                          set(therapist_profile.therapy_approaches))
        if approach_matches:
            approach_names = [dict(TherapistProfile.THERAPY_APPROACHES).get(app, app) 
                            for app in approach_matches if app is not None]
            approach_names = [name for name in approach_names if name is not None]
            if approach_names:
                reasons.append(f"Uses {', '.join(approach_names)} approach")
        
        # Experience
        if therapist_profile.years_of_experience >= 10:
            reasons.append(f"{therapist_profile.years_of_experience}+ years of experience")
        
        # Insurance
        if (client_prefs.insurance_provider and 
            therapist_profile.accepts_insurance):
            reasons.append("Accepts your insurance")
        
        # Rating
        if therapist_profile.rating >= 4.5:
            reasons.append(f"Highly rated ({therapist_profile.rating:.1f}/5.0)")
        
        # Languages
        lang_matches = (set(client_prefs.preferred_languages) & 
                       set(therapist_profile.languages_spoken))
        if lang_matches:
            reasons.append(f"Speaks {', '.join(lang_matches)}")
        
        return reasons[:4]  # Limit to top 4 reasons
    
    def _get_basic_matches(self, limit: int) -> List[Dict]:
        """Return basic matches when no client preferences are available."""
        therapists = TherapistProfile.objects.filter(
            is_accepting_clients=True,
            user__is_active=True
        ).order_by('-rating', '-years_of_experience')[:limit]
        
        return [{
            'therapist': t,
            'score': 0.7,  # Neutral score
            'score_breakdown': {
                'specialization': 0.7,
                'approach': 0.7,
                'availability': 0.7,
                'preferences': 0.7,
                'budget': 0.7,
                'rating': t.rating / 5.0 if t.rating else 0.5,
            },
            'match_reasons': [f"{t.years_of_experience}+ years experience", 
                            f"Rated {t.rating:.1f}/5.0" if t.rating else "New therapist"]
        } for t in therapists]
