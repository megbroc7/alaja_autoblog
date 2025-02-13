import requests
import base64
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import markdown

# 🔹 Load API Keys from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_API_KEY = os.getenv("WORDPRESS_API_KEY")
WORDPRESS_URL = os.getenv("WORDPRESS_URL")

# 🔹 Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔹 Encode WordPress credentials for authentication
credentials = f"{WORDPRESS_USERNAME}:{WORDPRESS_API_KEY}"
token = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

# 🔹 Categories Dictionary with IDs from WordPress
CATEGORIES = {
    "Ancestral Healing": 38,
    "Art Therapy & Intuition": 42,
    "Chakra Work & Activation": 39,
    "Clairs & Extrasensory Perception": 36,
    "Crystals & Selenite": 35,
    "Energy Healing": 32,
    "Intuitive Development": 34,
    "Meditation & Self-Discovery": 41,
    "Mystical Teachings": 40,
    "Rituals & Sacred Practices": 43,
    "Sensory Healing": 33,
    "Spiritual Awakening": 37
}

# 🔹 Tags Dictionary with IDs from WordPress
TAGS = {
    "Akashic Records": 60,
    "Ancestor Rituals": 54,
    "13 Chakra System": 50,
    "Clairaudience": 46,
    "Claircognizance": 47,
    "Clairsentience": 45,
    "Clairvoyance": 44,
    "DNA Upgrades": 49,
    "Energetic Boundaries": 66,
    "Energy Work": 53,
    "Frequency Healing": 17,
    "Healing Hands": 52,
    "Healing Relationships": 71,
    "Intuitive Art Therapy": 59,
    "Karmic Healing": 67,
    "Lightworker Path": 62,
    "Manifestation": 55,
    "Moon Cycles & Energy Shifts": 57,
    "Mystic Insights": 58,
    "Sacred Geometry": 63
}

# 🔹 Step 1: Generate a Unique Blog Topic
def generate_blog_topic():
    prompt = """
    Generate a unique, search-optimized blog post topic for a holistic blog written in the tone of an female spirtual healer.
    The topic must be chosen from one of the following ideas:

    - Clairs (clairvoyance, clairsentience, clairaudience, claircognizance)
    - Human senses and energy shifts
    - Healing with Selenite and it's benefits
    - Intuitive art therapy for healing and self-discovery
    - 13 moon cycles and divine feminine energy
    - Ancient mayan 13-day calendar and it's meaning and how history intentionally erased it
    - Mary Magdalene, apostle of apostles, and that she was Jesus' wife 
    - Sacredness of the number 13
    - 13 chakras 
    - 13 DNA strands 

    Ensure the topic also provides **practical applications**, such as:
    - Exercises or techniques the reader can try
    - How to integrate these teachings into daily life
    - Real-world examples of transformation through these practices

    Please ensure the title does not always default to something like "intuitive art therapy: unlocking self healing through creativity". Choose a different topic if possible.

    The title should short, simple and clear to engage readers while being search-friendly. Return the title as plain text (without quotations) and nothing else.  
    """

    response = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[{"role": "system", "content": "You are female spirtual healer that uses intuative art therapy as a main tool in your practice, and must create blog topics that are inspiring, educational, and practical."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

selected_topic = generate_blog_topic()

# 🔹 Step 2: Assign the Most Relevant Category
selected_category = None
for category, category_id in CATEGORIES.items():
    if category.lower() in selected_topic.lower():
        selected_category = category_id
        break

# If no exact match, default to "Energy Healing"
if selected_category is None:
    selected_category = 32  

# 🔹 Step 3: Assign Relevant Tags
selected_tags = []
for tag, tag_id in TAGS.items():
    if tag.lower() in selected_topic.lower():
        selected_tags.append(tag_id)

# If no exact tags match, assign a default tag
if not selected_tags:
    selected_tags = [59]  # Default to "Intuitive Art Therapy"

# 🔹 Step 4: Generate SEO-Optimized, Clear Blog Content
def generate_blog_post(topic):
    prompt = f"""
    Write a 1,800-2,000-word search-optimized blog post in the tone of a female spirtual healer.
    The topic is: {topic}.
    
    The article should be simple, educational, and easy to understand. Use storytelling, 
    ancient wisdom, and a rhythmic, flowing tone. Weave in metaphysical concepts like 
    Clairs (clairvoyance, clairsentience), energy healing, intuitive art therapy, and 
    chakra activation.

    Key Guidelines for Clarity:
    - Use simple, engaging language.
    - Offer practical applications readers can apply to their lives.
    - Include step-by-step guides or actionable exercises.
    - Use structured formatting with only H3, and H4 headings.
    - Make good use of tables, bullet points, numbered lists for readability.
    - Keep paragraphs concise and focused.

    Basic structure:
    1. Introduce the idea
    2. Body that delves deeper into the topic
    3. Easy to apply Practical Exercises
    4. Conclusion and Suggestions/Tips for simple steps to keep the practice in your daily life 

    Do not include a sign off. 
    """

    response = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[{"role": "system", "content": "You are female spirtual healer that uses intuative art therapy as a main tool in your practice, creating inspiring, practical, and educational blog posts."},
                  {"role": "user", "content": prompt}],
        max_tokens=2500
    )

    return response.choices[0].message.content.strip()

blog_content = generate_blog_post(selected_topic)

# 🔹 Step 5: Format Content for WordPress
# Convert the markdown blog-content to HTML

blog_content_html = markdown.markdown(blog_content, extensions=['tables'])

# Remove any leading H1 tag (in case the title is included) to avoid duplicate title in the content
blog_content_html = re.sub(r'^<h1>.*?</h1>', '', blog_content_html, flags=re.DOTALL).strip()

formatted_content = f"""
    {blog_content_html}
    <p><strong>With love and light,</strong><br>🤍 Alaja & Team</p>
"""

# 🔹 Step 6: Post to WordPress with Correct Formatting
blog_post = {
    "title": selected_topic,
    "content": formatted_content,
    "status": "publish",  # Change to "draft" for manual review
    "categories": [selected_category],
    "tags": selected_tags,
    "excerpt": blog_content[:150]  # Meta description for SEO
}

response = requests.post(WORDPRESS_URL, json=blog_post, headers=headers)

# 🔹 Step 7: Check Response
if response.status_code == 201:
    print(f"✅ Blog post published successfully: {response.json().get('link')}")
else:
    print(f"❌ Failed to post: {response.text}")
