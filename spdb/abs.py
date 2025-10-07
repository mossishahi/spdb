from spdb.utils._scrape import scrape_dataset_abstract  
from spdb.utils._llm import _llm_dataset_abstract
from spdb.utils._else import get_elsevier_abstract_from_url
from spdb.utils._ncbi import get_pmids_from_geo_with_selenium, sort_pmids_by_date, pmid_to_doi
from spdb.utils._pubmed import get_pubmed_abstract
import logging

logger = logging.getLogger(__name__)

easy_to_access = ['arxiv', 'biorxiv', 'medrxiv',  'nature.com']
llm_to_access = ['pubmed.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov', 'cell.com',]

def get_abstract(url: str):
    """
    Get the abstract of the dataset from the url.
    If the url is easy to access, use the scrape_dataset_abstract function.
    If the url is not easy to access, use the _llm_dataset_abstract function.
    """ 
    if any(x in url for x in easy_to_access):
        try:
            return scrape_dataset_abstract(url)
        except Exception as e:
            logger.error(f"Scraping article webpage failed: {e}", exc_info=True)
            pass
    elif 'pii' in url:
        try:
            return get_elsevier_abstract_from_url(url)
        except Exception as e:
            logger.error(f"Getting Elsevier abstract failed: {e}", exc_info=True)
            pass
    elif 'geo' in url:
        try:
            pmid = get_pmids_from_geo_with_selenium(url)
            if len(pmid) > 1:
                pmid = sort_pmids_by_date(pmid)[0]
            return get_pubmed_abstract(pmid_to_doi(pmid))
        except Exception as e:
            logger.error(f"Getting GEO abstract failed: {e}", exc_info=True)
            pass
    elif any(x in url for x in llm_to_access):
        try:
            return _llm_dataset_abstract(url)
        except Exception as e:
            logger.error(f"Getting abstract using LLM failed: {e}", exc_info=True)
            pass
    else:
        return None
