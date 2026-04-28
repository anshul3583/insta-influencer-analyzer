# modules/data_handler.py

import time


class InfluencerDataHandler:
    """Handle all influencer data operations"""

    def __init__(self, apify_key, openai_key):
        self.apify_key = apify_key
        self.openai_key = openai_key

    def get_influencer_stats(self, username):
        """Fetch influencer stats (mock data for now)"""
        time.sleep(1.5)

        # Mock data - will be replaced with real Apify API in Phase 1
        stats = {
            "username": username,
            "followers": 284500000,
            "following": 589,
            "posts": 3247,
            "bio": "Football | Family | Fashion 👑",
            "verified": True,
            "engagement_rate": 3.2,
            "avg_likes": 2450000,
            "avg_comments": 85000,
            "posting_frequency": 4.2,
            "top_hashtags": ["#football", "#family", "#lifestyle"],
            "audience_country": "Global 🌍",
            "audience_age": "18-55",
            "audience_gender": "65% Male, 35% Female",
            "growth_rate": "+2.3%",
            "best_posting_time": "7-9 PM UTC",
            "follower_growth_7d": 150000,
            "follower_growth_30d": 2100000,
            "avg_reach": 85000000,
            "saves_per_post": 450000,
            "shares_per_post": 250000,
            "content_categories": ["Sports", "Lifestyle", "Fashion"],
            "partner_brands": ["Nike", "Adidas", "Puma", "Gucci"],
        }

        return stats

    def get_multiple_influencers(self, usernames):
        """Fetch data for multiple influencers"""
        results = {}
        for username in usernames:
            results[username] = self.get_influencer_stats(username)
        return results

    def compare_influencers(self, username_a, username_b):
        """Get comparison data for two influencers"""
        data_a = self.get_influencer_stats(username_a)
        data_b = self.get_influencer_stats(username_b)

        return {
            "influencer_a": data_a,
            "influencer_b": data_b,
            "comparison": self._calculate_differences(data_a, data_b)
        }

    def _calculate_differences(self, data_a, data_b):
        """Calculate differences between two influencers"""
        return {
            "followers_diff": data_a["followers"] - data_b["followers"],
            "engagement_diff": data_a["engagement_rate"] - data_b["engagement_rate"],
            "reach_diff": data_a["avg_reach"] - data_b["avg_reach"],
            "growth_diff": data_a["follower_growth_30d"] - data_b["follower_growth_30d"],
        }

    def get_trending_influencers(self, niche, count=5):
        """Get trending influencers in a niche"""
        # Mock data
        trending = []
        names = ["cristiano", "leomessi",
                 "kyliejenner", "arianagrande", "therock"]

        for i, name in enumerate(names[:count]):
            trending.append({
                "rank": i + 1,
                "username": name,
                "followers": 284500000 - (i * 50000000),
                "engagement_rate": 3.2 - (i * 0.2),
                "growth_rate": f"+{2.3 - (i * 0.3):.1f}%"
            })

        return trending

    def get_audience_insights(self, username):
        """Get detailed audience insights"""
        # Mock data
        insights = {
            "age_distribution": {
                "13-17": 8,
                "18-24": 35,
                "25-34": 32,
                "35-44": 18,
                "45-54": 5,
                "55+": 2
            },
            "gender_distribution": {
                "male": 65,
                "female": 35
            },
            "top_countries": [
                {"country": "United States", "percentage": 25},
                {"country": "India", "percentage": 18},
                {"country": "Brazil", "percentage": 12},
                {"country": "United Kingdom", "percentage": 10},
                {"country": "Canada", "percentage": 8}
            ],
            "top_cities": [
                {"city": "Los Angeles", "percentage": 8},
                {"city": "New York", "percentage": 7},
                {"city": "Mumbai", "percentage": 6},
                {"city": "London", "percentage": 5},
                {"city": "São Paulo", "percentage": 4}
            ]
        }

        return insights

    def get_content_performance(self, username):
        """Get content performance metrics"""
        # Mock data
        content_perf = {
            "best_performing_posts": [
                {
                    "caption": "Blessed 🙏",
                    "likes": 5200000,
                    "comments": 125000,
                    "engagement": 5.8,
                    "type": "Carousel"
                },
                {
                    "caption": "Family time ❤️",
                    "likes": 4800000,
                    "comments": 98000,
                    "engagement": 5.2,
                    "type": "Reel"
                },
                {
                    "caption": "Work hard 💪",
                    "likes": 4500000,
                    "comments": 87000,
                    "engagement": 4.9,
                    "type": "Photo"
                }
            ],
            "content_type_performance": {
                "Reels": {"avg_engagement": 5.1, "frequency": 40},
                "Carousel": {"avg_engagement": 4.8, "frequency": 35},
                "Photo": {"avg_engagement": 3.2, "frequency": 20},
                "Video": {"avg_engagement": 4.5, "frequency": 5}
            },
            "posting_schedule": {
                "Monday": 2,
                "Tuesday": 1,
                "Wednesday": 2,
                "Thursday": 1,
                "Friday": 2,
                "Saturday": 0,
                "Sunday": 2
            }
        }

        return content_perf

    def get_competitor_analysis(self, username, count=5):
        """Get top competitors for an influencer"""
        # Mock data
        competitors = []
        comp_names = ["leomessi", "therock",
                      "arianagrande", "kyliejenner", "selenagomez"]

        for i, name in enumerate(comp_names[:count]):
            competitors.append({
                "rank": i + 1,
                "username": name,
                "followers": 284500000 - (i * 40000000),
                "engagement_rate": 3.2 - (i * 0.15),
                "audience_overlap": 35 - (i * 5),
                "content_similarity": 72 - (i * 8),
                "partnership_potential": "High" if i < 2 else "Medium" if i < 4 else "Low"
            })

        return competitors
