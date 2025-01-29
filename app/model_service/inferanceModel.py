from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import torch

# File paths
MODEL_PATH = "app/model_service/trained_model.pkl"
TRIPLES_FILE = "app/model_service/dataset_train.tsv.gz"

# Global variables
heads_id = []
relations_id = []
hr_batch = None
model = None

def load_model() -> None: 
    """Loads the trained model and prepares the necessary tensors."""
    global model, heads_id, relations_id, hr_batch  # Declare global variables

    # Load the trained model
    model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    
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


def is_valid_id(head: str) -> bool:
    """Checks if the given head ID exists in the dataset."""
    try:
        current_id = int(head)
        return current_id in heads_id
    except ValueError:
        return False


def find_similars(head: int) -> list[int]:
     """Finds the 10 most similar elements for a given head ID."""
     if head not in heads_id:
        raise ValueError(f"El inmueble con id {head} no se encuentra registrado.")
     
     # Prepare tensor sample
     sample = [[head, 5]]

    # Compute scores
     scores = model.score_t(torch.tensor(sample))

     # Pair scores with their indices and sort
     paired_scores = [[value.item(), index] for index, value in enumerate(scores.flatten())]
     sorted_scores = sorted(paired_scores, key=lambda x: x[0])

     # Extract the first 10 indices
     ids = [item[1] for item in sorted_scores][:10]
    
     # Map back to original `heads_id`
     selected_elements = [heads_id[i] for i in ids]

     return selected_elements

