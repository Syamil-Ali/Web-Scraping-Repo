from fastapi import FastAPI, HTTPException
import traceback

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

app = FastAPI()

# Shared crawler instance
crawler = AsyncWebCrawler()

@app.on_event("startup")
async def startup_event():
    await crawler.start()

@app.on_event("shutdown")
async def shutdown_event():
    await crawler.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to your FastAPI app!"}

@app.get("/url/")
async def crawl_url(target_url: str):
    try:
        # === Crawling Configs ===
        prune_filter = PruningContentFilter(
            threshold=0.45,
            threshold_type="dynamic",
            min_word_threshold=5
        )

        keyword_scorer = KeywordRelevanceScorer(
            keywords=["about-us", "overview", "what we do", "about", "who we are"],
            weight=0.9
        )

        url_filter = URLPatternFilter(patterns=["*about*", "*home*", "*mission*", "service", "services"])

        strategy = BestFirstCrawlingStrategy(
            max_depth=1,
            include_external=False,
            max_pages=5,
            url_scorer=keyword_scorer,
            filter_chain=FilterChain([url_filter])
        )

        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

        config = CrawlerRunConfig(
            word_count_threshold=5,
            exclude_external_links=True,
            remove_overlay_elements=True,
            process_iframes=True,
            markdown_generator=md_generator,
            deep_crawl_strategy=strategy
        )

        results = await crawler.arun(target_url, config=config)
        
        documents = []
        urls = []

        for idx, result in enumerate(results):
            if result.success:
                markdown_content = result.markdown.fit_markdown
                source_url = result.url
                documents.append(markdown_content)
                urls.append(source_url)


                
        return {"result": documents, "urls": urls}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
