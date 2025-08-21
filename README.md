# AI Agents Demo – MOM Statistics Scraper

This project showcases how multiple AI Agents can collaborate to automate the retrieval of statistical data from the Ministry of Manpower (MOM) website.  

---

## 🚀 Quick Setup

Follow these steps to get started:

```bash
# 1. Clone the repository
git clone https://github.com/patata123/MOM-Agent.git
cd <your-repo-folder>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Populate .env file in the project root with your API keys
# Example:
# OPENAI_API_KEY=your_openai_api_key_here
# FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# 5. Run the demo
python MOM.py
