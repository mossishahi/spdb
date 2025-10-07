from spdb.abs import get_abstract
from spdb.emb import get_embedding

# URL = "https://www.cell.com/cell/fulltext/S0092-8674(23)01222-9?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS0092867423012229%3Fshowall%3Dtrue#secsectitle0020"
URL = "https://www.nature.com/articles/s41586-023-06311-1"
abs = get_abstract(URL)
print(abs)
print('-'*100)
print(get_embedding(abs)[:10])


# ------------------------------------------------------------------------------------------------
# output:
# The function of a cell is defined by its intrinsic characteristics and 
# its niche: the tissue microenvironment in which it dwells. Here we 
# combine single-cell and spatial transcriptomics data to discover cellular 
# niches within eight regions of the human heart. We map cells to microanatomical 
# locations and integrate knowledge-based and unsupervised structural annotations.
#  We also profile the cells of the human cardiac conduction system1. The results 
#  revealed their distinctive repertoire of ion channels, G-protein-coupled receptors (GPCRs) 
#  and regulatory networks, and implicated FOXP2 in the pacemaker phenotype. We show that the 
#  sinoatrial node is compartmentalized, with a core of pacemaker cells, fibroblasts and 
#  glial cells supporting glutamatergic signalling. Using a custom CellPhoneDB.org module, 
#  we identify trans-synaptic pacemaker cell interactions with glia. We introduce a druggable
#   target prediction tool, drug2cell, which leverages single-cell profiles and drug–target 
#   interactions to provide mechanistic insights into the chronotropic effects of drugs, 
#   including GLP-1 analogues. In the epicardium, we show enrichment of both IgG+ and IgA+ plasma cells 
#   forming immune niches that may contribute to infection defence. Overall, we provide new clarity to 
#   cardiac electro-anatomy and immunology, and our suite of computational approaches can be applied to other tissues and organs.
# ----------------------------------------------------------------------------------------------------
# [-0.006138592958450317, -0.025601714849472046, 0.08104623854160309, 0.038816336542367935, -0.0004113406757824123, -0.01736520417034626, 0.015231726691126823, 0.00024082421441562474, 0.01860649883747101, -0.07085727155208588]
