import sys
import os
from os.path import exists
import pickle
    
# Load models & tokenizer
from dalle_mini import DalleBart, DalleBartProcessor
from vqgan_jax.modeling_flax_vqgan import VQModel

def setup():
    if len(sys.argv) > 1 and sys.argv[1] not in ('mega', 'mini'):
        print("Usage: python setup.py [mega/mini/no arg]")
        return

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

    model_size = 'mini' if len(sys.argv) == 1 else sys.argv[1]
    model_filename = f"{path}/artifacts/dalle{'_mini' * (model_size == 'mini')}.pkl"

    if all([exists(model_filename), exists(f'{path}/artifacts/processor.pkl'), exists(f'{path}/artifacts/vqgan.pkl')]):
        print("Models already downloaded, app is ready to run with 'streamlit run app.py'")
        return
        
    DALLE_MODEL = "dalle-mini/dalle-mini/mini-1:v0" if model_size == 'mini' else 'dalle-mini/dalle-mini/mega-1-fp16:latest'
    DALLE_COMMIT_ID = None

    VQGAN_REPO = "dalle-mini/vqgan_imagenet_f16_16384"
    VQGAN_COMMIT_ID = "e93a26e7707683d349bf5d5c41c5b0ef69b677a9"
    
    print(f"Downloading dalle-{model_size} model. This could take some time...")

    # # Load dalle-mini
    model, params = DalleBart.from_pretrained(
        DALLE_MODEL, revision=DALLE_COMMIT_ID, _do_init=False
    )
    
    print("DALL-E loaded. Now loading VQGAN model...")
    
    # Load VQGAN
    vqgan, vqgan_params = VQModel.from_pretrained(
        VQGAN_REPO, revision=VQGAN_COMMIT_ID, _do_init=False
    )
    
    print("VQGAN loaded. Now loading DALL-E processor...")
    
    processor = DalleBartProcessor.from_pretrained(DALLE_MODEL, revision=DALLE_COMMIT_ID)

    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    
    print("All files downloaded. Saving locally...")

    with open(model_filename, 'wb') as filehandler:
        pickle.dump((model, params), filehandler)
        
    with open(f'{path}/artifacts/vqgan.pkl', 'wb') as filehandler:
        pickle.dump((vqgan, vqgan_params), filehandler)
        
    with open(f'{path}/artifacts/processor.pkl', 'wb') as filehandler:
        pickle.dump(processor, filehandler)
        
    print("Models saved and ready for use.")
        
if __name__ == '__main__':
    setup()