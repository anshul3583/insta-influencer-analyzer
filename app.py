# app.py

import streamlit as st
from config import APP_TITLE, APP_DESCRIPTION, APP_ICON
from modules import (
    render_css,
    render_sidebar,
    render_hero,
    metric_card,
    badge,
    info_card,
    render_footer,
    InfluencerDataHandler,
)

# Page config
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Influencer Radar - Analyze Instagram influencers like a pro 📊"
    }
)

# Render CSS
render_css()

# Sidebar
openai_key, apify_key, stripe_key = render_sidebar()

# Hero section
render_hero()

# Initialize data handler
handler = InfluencerDataHandler(apify_key, openai_key)

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["🔍 Analyze", "⚖️ Compare", "📊 Insights"])

# ==================== TAB 1: ANALYZE ====================
with tab1:
    st.markdown('<h2 class="section-title">🔍 Deep Dive into Any Creator</h2>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        influencer_1 = st.text_input(
            "Drop a username",
            placeholder="e.g., cristiano, leomessi, arianagrande",
            key="influencer_1",
            label_visibility="collapsed"
        )

    with col2:
        analyze_button = st.button(
            "🚀 Analyze", use_container_width=True, type="primary")

    if analyze_button:
        if not openai_key or not apify_key:
            st.error("🔐 Add your API keys in the sidebar first!")
        elif not influencer_1:
            st.error("👀 We need a username to analyze!")
        else:
            with st.spinner("🔄 Fetching the tea..."):
                stats = handler.get_influencer_stats(influencer_1)
                audience = handler.get_audience_insights(influencer_1)
                content_perf = handler.get_content_performance(influencer_1)

            st.success(f"✨ Unlocked @{stats['username']}'s profile!")

            st.markdown("---")

            # Stat cards
            st.markdown(
                '<h3 class="sub-section-title">📈 The Numbers</h3>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                metric_card("👥", "Followers", f"{stats['followers']/1e6:.1f}M")

            with col2:
                metric_card("🔥", "Engagement", f"{stats['engagement_rate']}%")

            with col3:
                metric_card("📱", "Posts", f"{stats['posts']:,}")

            with col4:
                metric_card("📈", "Growth (30d)",
                            f"+{stats['follower_growth_30d']/1e6:.1f}M")

            st.markdown("---")

            # Profile and audience info
            col1, col2 = st.columns(2)

            with col1:
                info_card("👤 Profile", "👤", {
                    "Username": f"@{stats['username']}" + (" ✅" if stats['verified'] else ""),
                    "Bio": stats['bio'],
                    "Location": stats['audience_country'],
                    "Following": f"{stats['following']:,}"
                })

            with col2:
                info_card("👥 Audience", "👥", {
                    "Age Range": stats['audience_age'],
                    "Gender Split": stats['audience_gender'],
                    "Best Post Time": stats['best_posting_time'],
                    "Posting Frequency": f"{stats['posting_frequency']} posts/week"
                })

            st.markdown("---")

            # Engagement details
            st.markdown(
                '<h3 class="sub-section-title">🔥 Engagement Breakdown</h3>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Avg Likes 👍", f"{stats['avg_likes']:,}")

            with col2:
                st.metric("Avg Comments 💬", f"{stats['avg_comments']:,}")

            with col3:
                st.metric("Avg Reach 📢", f"{stats['avg_reach']/1e6:.1f}M")

            st.markdown("---")

            # Hashtags
            st.markdown(
                '<h3 class="sub-section-title">🏷️ Trending Hashtags</h3>', unsafe_allow_html=True)

            cols = st.columns(len(stats['top_hashtags']))
            for col, hashtag in zip(cols, stats['top_hashtags']):
                with col:
                    badge(hashtag)

            st.markdown("---")

            # Content categories
            st.markdown(
                '<h3 class="sub-section-title">📂 Content Categories</h3>', unsafe_allow_html=True)

            cols = st.columns(len(stats['content_categories']))
            for col, category in zip(cols, stats['content_categories']):
                with col:
                    badge(category, "warning")

            st.markdown("---")

            # Audience demographics
            st.markdown(
                '<h3 class="sub-section-title">📊 Audience Demographics</h3>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Age Distribution")
                age_data = audience['age_distribution']
                st.bar_chart({age: percentage for age,
                             percentage in age_data.items()})

            with col2:
                st.subheader("Top Countries")
                countries_data = audience['top_countries']
                countries_dict = {c['country']: c['percentage']
                                  for c in countries_data}
                st.bar_chart(countries_dict)

            st.markdown("---")

            # Partner brands
            st.markdown(
                '<h3 class="sub-section-title">🤝 Partner Brands</h3>', unsafe_allow_html=True)

            cols = st.columns(len(stats['partner_brands']))
            for col, brand in zip(cols, stats['partner_brands']):
                with col:
                    badge(brand, "success")

            st.markdown("---")

            # Best performing content
            st.markdown(
                '<h3 class="sub-section-title">⭐ Best Performing Posts</h3>', unsafe_allow_html=True)

            for post in content_perf['best_performing_posts']:
                with st.expander(f"{post['type']} • {post['likes']:,} likes"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Likes", f"{post['likes']:,}")
                    col2.metric("Comments", f"{post['comments']:,}")
                    col3.metric("Engagement", f"{post['engagement']}%")
                    st.write(f"**Caption:** {post['caption']}")

            st.markdown("---")

            # Download and premium buttons
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📥 Download Report",
                    data=f"username,followers,engagement_rate,posts\n{stats['username']},{stats['followers']},{stats['engagement_rate']},{stats['posts']}",
                    file_name=f"{stats['username']}_analysis.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                st.button("💰 Unlock Premium Insights",
                          use_container_width=True)


# ==================== TAB 2: COMPARE ====================
with tab2:
    st.markdown('<h2 class="section-title">⚖️ Compare Two Influencers</h2>',
                unsafe_allow_html=True)
    st.write("Want to compare side-by-side? Enter two usernames below.")

    col1, col2 = st.columns(2)

    with col1:
        username_a = st.text_input(
            "First Influencer",
            placeholder="e.g., cristiano",
            key="influencer_compare_1"
        )

    with col2:
        username_b = st.text_input(
            "Second Influencer",
            placeholder="e.g., leomessi",
            key="influencer_compare_2"
        )

    if st.button("⚡ Compare", type="primary", use_container_width=True):
        if not openai_key or not apify_key:
            st.error("🔐 Add your API keys in the sidebar first!")
        elif not username_a or not username_b:
            st.error("👀 Please enter both usernames")
        elif username_a.lower() == username_b.lower():
            st.error("⚠️ Please enter two different usernames")
        else:
            with st.spinner(f"🔄 Comparing @{username_a} vs @{username_b}..."):
                comparison = handler.compare_influencers(
                    username_a, username_b)

            st.success("✨ Comparison ready!")

            data_a = comparison['influencer_a']
            data_b = comparison['influencer_b']
            diff = comparison['comparison']

            st.markdown("---")

            # Head-to-head comparison
            st.markdown(
                '<h3 class="sub-section-title">📊 Head-to-Head Comparison</h3>', unsafe_allow_html=True)

            comparison_table = {
                "Metric": [
                    "Followers",
                    "Engagement Rate",
                    "Avg Likes/Post",
                    "Posts",
                    "Growth (30d)",
                    "Avg Reach",
                    "Posting Frequency",
                    "Audience Age",
                    "Gender Split"
                ],
                f"@{data_a['username']}": [
                    f"{data_a['followers']/1e6:.1f}M",
                    f"{data_a['engagement_rate']}%",
                    f"{data_a['avg_likes']:,}",
                    f"{data_a['posts']:,}",
                    f"+{data_a['follower_growth_30d']/1e6:.1f}M",
                    f"{data_a['avg_reach']/1e6:.1f}M",
                    f"{data_a['posting_frequency']}/week",
                    data_a['audience_age'],
                    data_a['audience_gender']
                ],
                f"@{data_b['username']}": [
                    f"{data_b['followers']/1e6:.1f}M",
                    f"{data_b['engagement_rate']}%",
                    f"{data_b['avg_likes']:,}",
                    f"{data_b['posts']:,}",
                    f"+{data_b['follower_growth_30d']/1e6:.1f}M",
                    f"{data_b['avg_reach']/1e6:.1f}M",
                    f"{data_b['posting_frequency']}/week",
                    data_b['audience_age'],
                    data_b['audience_gender']
                ]
            }

            st.dataframe(comparison_table, use_container_width=True)

            st.markdown("---")

            # Key differences
            st.markdown(
                '<h3 class="sub-section-title">🎯 Key Differences</h3>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if diff['followers_diff'] > 0:
                    st.success(f"✅ @{data_a['username']}")
                    st.write(f"+{diff['followers_diff']/1e6:.1f}M followers")
                else:
                    st.info(f"ℹ️ @{data_b['username']}")
                    st.write(
                        f"+{abs(diff['followers_diff'])/1e6:.1f}M followers")

            with col2:
                if diff['engagement_diff'] > 0:
                    st.success(f"✅ @{data_a['username']}")
                    st.write(f"+{diff['engagement_diff']}% engagement")
                else:
                    st.info(f"ℹ️ @{data_b['username']}")
                    st.write(f"+{abs(diff['engagement_diff'])}% engagement")

            with col3:
                if diff['reach_diff'] > 0:
                    st.success(f"✅ @{data_a['username']}")
                    st.write(f"+{diff['reach_diff']/1e6:.1f}M reach")
                else:
                    st.info(f"ℹ️ @{data_b['username']}")
                    st.write(f"+{abs(diff['reach_diff'])/1e6:.1f}M reach")

            with col4:
                if diff['growth_diff'] > 0:
                    st.success(f"✅ @{data_a['username']}")
                    st.write(f"+{diff['growth_diff']/1e6:.1f}M growth")
                else:
                    st.info(f"ℹ️ @{data_b['username']}")
                    st.write(f"+{abs(diff['growth_diff'])/1e6:.1f}M growth")

            st.markdown("---")

            # Side-by-side profile cards
            st.markdown(
                '<h3 class="sub-section-title">👤 Profile Comparison</h3>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                info_card(f"@{data_a['username']}", "👤", {
                    "Followers": f"{data_a['followers']/1e6:.1f}M",
                    "Engagement": f"{data_a['engagement_rate']}%",
                    "Bio": data_a['bio'],
                    "Verified": "✅ Yes" if data_a['verified'] else "❌ No",
                })

            with col2:
                info_card(f"@{data_b['username']}", "👤", {
                    "Followers": f"{data_b['followers']/1e6:.1f}M",
                    "Engagement": f"{data_b['engagement_rate']}%",
                    "Bio": data_b['bio'],
                    "Verified": "✅ Yes" if data_b['verified'] else "❌ No",
                })

            st.markdown("---")

            # Audience comparison
            st.markdown(
                '<h3 class="sub-section-title">👥 Audience Comparison</h3>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"@{data_a['username']}")
                st.write(f"**Age:** {data_a['audience_age']}")
                st.write(f"**Gender:** {data_a['audience_gender']}")
                st.write(f"**Location:** {data_a['audience_country']}")

            with col2:
                st.subheader(f"@{data_b['username']}")
                st.write(f"**Age:** {data_b['audience_age']}")
                st.write(f"**Gender:** {data_b['audience_gender']}")
                st.write(f"**Location:** {data_b['audience_country']}")

            st.markdown("---")

            # Download comparison
            col1, col2 = st.columns(2)

            with col1:
                comparison_csv = f"""username,followers,engagement_rate,avg_likes,posting_frequency
{data_a['username']},{data_a['followers']},{data_a['engagement_rate']},{data_a['avg_likes']},{data_a['posting_frequency']}
{data_b['username']},{data_b['followers']},{data_b['engagement_rate']},{data_b['avg_likes']},{data_b['posting_frequency']}"""

                st.download_button(
                    label="📥 Download Comparison",
                    data=comparison_csv,
                    file_name=f"{data_a['username']}_vs_{data_b['username']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                st.button("💰 Get Premium Comparison Report",
                          use_container_width=True)


# ==================== TAB 3: INSIGHTS ====================
with tab3:
    st.markdown('<h2 class="section-title">📊 Market Insights & Trends</h2>',
                unsafe_allow_html=True)
    st.write("Discover trending influencers and market opportunities")

    st.markdown("---")

    # Tabs within insights
    insights_tab1, insights_tab2, insights_tab3 = st.tabs(
        ["🔥 Trending", "🎯 Competitors", "💡 Opportunities"])

    # ========== TRENDING ==========
    with insights_tab1:
        st.markdown(
            '<h3 class="sub-section-title">🔥 Trending Influencers</h3>', unsafe_allow_html=True)

        if st.button("📊 Load Trending Influencers", type="primary", use_container_width=True, key="trending_btn"):
            if not openai_key or not apify_key:
                st.error("🔐 Add your API keys in the sidebar first!")
            else:
                with st.spinner("🔄 Fetching trending influencers..."):
                    trending = handler.get_trending_influencers(
                        "general", count=5)

                st.success("✨ Trending influencers loaded!")

                st.markdown("---")

                for influencer in trending:
                    with st.expander(f"#{influencer['rank']} @{influencer['username']} • {influencer['followers']/1e6:.1f}M followers"):
                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Followers", f"{influencer['followers']/1e6:.1f}M")
                        col2.metric(
                            "Engagement", f"{influencer['engagement_rate']}%")
                        col3.metric("Growth", influencer['growth_rate'])

                        st.write("---")
                        st.write("**Why trending?**")
                        st.write("📈 Consistent growth over the past 30 days")
                        st.write("🔥 High engagement rate compared to peers")
                        st.write("💬 Increasing comment and share activity")

                        if st.button(f"Analyze @{influencer['username']}", key=f"trend_analyze_{influencer['rank']}"):
                            st.session_state.selected_influencer = influencer['username']
                            st.success(f"Loading @{influencer['username']}...")

    # ========== COMPETITORS ==========
    with insights_tab2:
        st.markdown(
            '<h3 class="sub-section-title">🎯 Find Your Competitors</h3>', unsafe_allow_html=True)
        st.write("Enter a username to find similar influencers in the same niche")

        comp_username = st.text_input(
            "Find competitors for",
            placeholder="e.g., cristiano",
            key="competitor_search"
        )

        if st.button("🔍 Find Competitors", type="primary", use_container_width=True):
            if not openai_key or not apify_key:
                st.error("🔐 Add your API keys in the sidebar first!")
            elif not comp_username:
                st.error("👀 Please enter a username")
            else:
                with st.spinner(f"🔄 Finding competitors for @{comp_username}..."):
                    competitors = handler.get_competitor_analysis(
                        comp_username, count=5)

                st.success(f"✨ Found {len(competitors)} competitors!")

                st.markdown("---")

                # Competitor table
                st.markdown(
                    '<h4 class="sub-section-title">Top Competitors</h4>', unsafe_allow_html=True)

                comp_table = {
                    "Rank": [c['rank'] for c in competitors],
                    "Username": [f"@{c['username']}" for c in competitors],
                    "Followers": [f"{c['followers']/1e6:.1f}M" for c in competitors],
                    "Engagement": [f"{c['engagement_rate']}%" for c in competitors],
                    "Audience Overlap": [f"{c['audience_overlap']}%" for c in competitors],
                    "Partnership Potential": [c['partnership_potential'] for c in competitors],
                }

                st.dataframe(comp_table, use_container_width=True)

                st.markdown("---")

                # Detailed competitor analysis
                st.markdown(
                    '<h4 class="sub-section-title">Detailed Analysis</h4>', unsafe_allow_html=True)

                for comp in competitors:
                    with st.expander(f"#{comp['rank']} @{comp['username']}"):
                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Followers", f"{comp['followers']/1e6:.1f}M")
                        col2.metric(
                            "Engagement", f"{comp['engagement_rate']}%")
                        col3.metric("Audience Overlap",
                                    f"{comp['audience_overlap']}%")

                        st.write("---")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(
                                f"**Content Similarity:** {comp['content_similarity']}%")
                            st.progress(comp['content_similarity'] / 100)

                        with col2:
                            st.write(
                                f"**Partnership Potential:** {comp['partnership_potential']}")
                            if comp['partnership_potential'] == "High":
                                st.success("🟢 Recommended for collaboration")
                            elif comp['partnership_potential'] == "Medium":
                                st.info("🟡 Possible collaboration opportunity")
                            else:
                                st.warning(
                                    "🔴 Lower priority for collaboration")

    # ========== OPPORTUNITIES ==========
    # with insights_tab3:
    #     st.markdown(
    #         '<h3 class="sub-section-title">💡 Monetization Opportunities</h3>', unsafe_allow_html=True)
    #     st.write("Discover collaboration and sponsorship opportunities")

    #     st.markdown("---")

    #     # Opportunity cards
    #     opportunity_cols = st.columns(2)

    #     with opportunity_cols[0]:
    #         st.markdown("""
    #         <div class="card">
    #         <h3 style="color: #FF006E; font-weight: 800;">🤝 Brand Collaborations</h3>
    #         <p>Connect with brands looking for influencer partnerships in your niche.</p>
    #         <ul>
    #         <li>Sponsored posts</li>
    #         <li>Long-term ambassador deals</li>
    #         <li>Product collaborations</li>
    #         </ul>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     with opportunity_cols[1]:
    #         st.markdown("""
    #         <div class="card">
    #         <h3 style="color: #8338EC; font-weight: 800;">📱 Affiliate Marketing</h3>
    #         <p>Earn commissions by promoting products to your engaged audience.</p>
    #         <ul>
    #         <li>Affiliate programs</li>
    #         <li>Commission tracking</li>
    #         <li>Performance analytics</li>
    #         </ul>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     opportunity_cols = st.columns(2)

    #     with opportunity_cols[0]:
    #         st.markdown("""
    #         <div class="card">
    #         <h3 style="color: #FFBE0B; font-weight: 800;">🎬 Sponsored Content</h3>
    #         <p>Create branded content that resonates with your authentic audience.</p>
    #         <ul>
    #         <li>Product placements</li>
    #         <li>Content licensing</li>
    #         <li>Custom campaigns</li>
    #         </ul>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     with opportunity_cols[1]:
    #         st.markdown("""
    #         <div class="card">
    #         <h3 style="color: #00D084; font-weight: 800;">💰 Direct Sales</h3>
    #         <p>Build your own business and sell directly to your followers.</p>
    #         <ul>
    #         <li>Digital products</li>
    #         <li>Courses & coaching</li>
    #         <li>Merchandise</li>
    #         </ul>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     st.markdown("---")

    #     # Monetization checklist
    #     st.markdown(
    #         '<h3 class="sub-section-title">📋 Monetization Readiness</h3>', unsafe_allow_html=True)

    #     col1, col2 = st.columns(2)

    #     with col1:
    #         st.write("**Brand Partnership Requirements:**")
    #         st.checkbox("✅ 10K+ followers", value=True)
    #         st.checkbox("✅ 2%+ engagement rate", value=True)
    #         st.checkbox("✅ Consistent posting schedule", value=True)
    #         st.checkbox("✅ Clear niche focus", value=True)

    #     with col2:
    #         st.write("**Affiliate Program Eligibility:**")
    #         st.checkbox("✅ Active content creation", value=True)
    #         st.checkbox("✅ Engaged community", value=True)
    #         st.checkbox("✅ Brand alignment", value=True)
    #         st.checkbox("✅ Traffic potential", value=True)

    #     st.markdown("---")

    #     # CTA
    #     col1, col2 = st.columns(2)

    #     with col1:
    #         if st.button("🎯 Get Personalized Recommendations", use_container_width=True, type="primary"):
    #             st.success(
    #                 "💌 We'll send personalized opportunity recommendations to your email!")

    #     with col2:
    #         if st.button("📧 Subscribe to Opportunities", use_container_width=True):
    #             st.info(
    #                 "📬 You'll be notified of new partnership opportunities in your niche")


# ==================== FOOTER ====================
render_footer()
