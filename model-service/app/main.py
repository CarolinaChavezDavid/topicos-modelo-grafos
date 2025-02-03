from pykeen.triples import TriplesFactory
from fastapi import FastAPI, HTTPException, Depends, Request
from contextlib import asynccontextmanager
import logging
import pandas as pd
import torch

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    load_model() 
    yield
    clear_cache()

app = FastAPI(lifespan=lifespan)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# File paths
MODEL_PATH = "app/model/trained_model.pkl"
TRIPLES_FILE = "app/model/dataset_train.tsv.gz"

# Global variables
heads_id = []
relations_id = []
hr_batch = None
model = None


def load_model() -> None: 
    """Loads the trained model and prepares the necessary tensors."""
    global model, heads_id, relations_id, hr_batch  # Declare global variables

    # Load the trained model
    model = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
    
    # Load triples factory
    triples_factory = TriplesFactory.from_path(TRIPLES_FILE, create_inverse_triples=True)
    
    # Read dataset
    data_frame = pd.read_csv(TRIPLES_FILE, sep="\t", header=None, names=["head", "relation", "tail"])
    

    triples_factory.relation_to_id["http://www.w3.org/2002/07/owl#sameAs"]
    heads = data_frame[list(map(lambda x: True if ('pronto.owl#space_site' in x) and (len(x.split('#')[1].split('_')) == 3) else False, data_frame['head'].values))]['head'].values
    
    # Generate relation mappings
    relations = ["http://www.w3.org/2002/07/owl#sameAs"] * len(heads)

    # Convert to IDs
    heads_id = [triples_factory.entity_to_id[head] for head in heads]
    relations_id = [triples_factory.relation_to_id[relation] for relation in relations]

    # Prepare batch tensor
    hr_batch = torch.tensor(list(zip(heads_id, relations_id)))

def clear_cache() -> None:
    torch.cuda.empty_cache()


@app.post("/similars/{head_id}")
def get_similars(head_id: int):
    """Finds similar elements"""

    logger.info(f"find_similars called with head ID: {head_id}")
     
    if head_id not in heads_id:
        error_msg = f"El inmueble con id {head_id} no se encuentra registrado."
        raise  HTTPException(status_code=400, detail= error_msg)
 
    # Prepare tensor sample
    sample = [[head_id, 5]]

    # Compute scores
    scores = model.score_t(torch.tensor(sample))

    # Pair scores with their indices and sort
    paired_scores = [[value.item(), index] for index, value in enumerate(scores.flatten())]
    sorted_scores = sorted(paired_scores, key=lambda x: x[0])

    # Extract the first 10 indices
    ids = [item[1] for item in sorted_scores][:10]
    
    # Map back to original `heads_id`
    selected_elements = [heads_id[i] for i in ids]
    logger.info(f"Similar head ids: {selected_elements}")
    return selected_elements
