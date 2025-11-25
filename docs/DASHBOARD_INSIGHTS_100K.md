# 📊 Superset Dashboard - 100K Tweets Analysis Insights

## Dashboard Overview

The Ukraine Tweets Sentiment Analysis dashboard has been upgraded to process **100,000 tweets**, providing significantly more robust and statistically valid insights. The dashboard now features **8 high-impact visualizations** designed to answer key questions about public sentiment.

## Access the Dashboard

-   **URL**: http://localhost:8088
-   **Username**: admin
-   **Password**: admin
-   **Dashboard**: "Ukraine Tweets Sentiment Analysis"

## Key Visualizations & Insights

### 1. 📈 Sentiment Evolution Over Time (Line Chart)

**What it shows**: Daily volume of positive, negative, and neutral tweets.
**Why it matters**:

-   Identifies key events that triggered spikes in specific sentiments.
-   Shows if public opinion is shifting over time (e.g., becoming more negative or supportive).
-   Correlates real-world news with social media reaction.

### 2. 📊 Overall Sentiment Balance (Donut Chart)

**What it shows**: The global proportion of sentiment.
**Why it matters**:

-   Provides a high-level "temperature check" of the conversation.
-   With 100k rows, this is a statistically significant representation of the dataset.

### 3. ☁️ Trending Topics (Word Cloud)

**What it shows**: The most frequent hashtags used in the conversation.
**Why it matters**:

-   Reveals the main themes and narratives driving the discussion.
-   Helps identify specific campaigns or viral topics (e.g., #StandWithUkraine vs #StopWar).

### 4. 🔥 Most Viral Tweets (Table)

**What it shows**: Tweets with the highest retweet counts, including their sentiment.
**Why it matters**:

-   Shows what content resonates most with the audience.
-   Identifies key influencers and viral narratives.
-   analyzing the sentiment of viral tweets shows if outrage (negative) or support (positive) spreads faster.

### 5. 🗺️ Geographic Sentiment Distribution (Treemap)

**What it shows**: Volume of tweets by location.
**Why it matters**:

-   Visualizes where the conversation is happening globally.
-   Can highlight regional differences in interest or sentiment.

### 6. 👍 Engagement by Sentiment (Bar Chart)

**What it shows**: Total retweets broken down by sentiment category.
**Why it matters**:

-   Goes beyond just tweet count to measure _impact_.
-   Answers: "Do negative tweets get more retweets than positive ones?"

### 7. 📢 Total Potential Reach (Big Number)

**What it shows**: Sum of followers for all users in the dataset.
**Why it matters**:

-   Estimates the maximum potential audience exposed to these tweets.
-   A measure of the conversation's scale and influence.

### 8. 💬 Total Tweets Analyzed (Big Number)

**What it shows**: The scale of the current analysis (100,000 tweets).
**Why it matters**:

-   Confirms the data volume and statistical weight of the insights.

## Technical Improvements

-   **Dataset Size**: Increased from 10,000 to **100,000 rows** for better accuracy.
-   **Data Quality**: Improved timestamp parsing and numeric type conversion in the pipeline.
-   **Automation**: Dashboard creation is fully automated via the Airflow pipeline using the Superset API.
-   **Performance**: Spark processing handled the larger dataset efficiently (~1 hour execution).

## Next Steps for Analysis

1. **Drill Down**: Use the dashboard filters to isolate specific time periods or locations.
2. **Cross-Reference**: Compare the "Trending Topics" with the "Sentiment Evolution" to see which topics drive which sentiments.
3. **Influencer Analysis**: Check the "Most Viral Tweets" to identify key opinion leaders.

---

**Last Updated**: 2025-11-25
**Pipeline Run ID**: manual\_\_2025-11-25T03:23:59+00:00
**Data Source**: ukraine_tweets_sample_100000.csv
